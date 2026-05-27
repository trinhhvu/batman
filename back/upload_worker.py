"""
back/upload_worker.py - Multi-Account Background Workers for Dailymotion Uploading
Handles per-account API authentication and multipart streaming uploads in the background.
Each worker receives an isolated account config dict — no shared global state.
"""

import os
import uuid
import requests
import urllib3
from PyQt5.QtCore import QThread, pyqtSignal

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DAILYMOTION_API   = "https://api.dailymotion.com"
DAILYMOTION_TOKEN = f"{DAILYMOTION_API}/oauth/token"
DAILYMOTION_ME    = f"{DAILYMOTION_API}/me"
OAUTH_SCOPE       = "manage_videos userinfo"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT}


def password_login(client_id: str, client_secret: str, email: str, password: str) -> str:
    """Exchange email/password for an access token. Returns the token string."""
    resp = requests.post(
        DAILYMOTION_TOKEN,
        data={
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": email,
            "password": password,
            "scope": OAUTH_SCOPE,
        },
        headers={"User-Agent": USER_AGENT},
        timeout=20,
        verify=False,
    )
    if resp.status_code != 200:
        raise Exception(f"Login failed ({resp.status_code}): {resp.text[:300]}")
    token = resp.json().get("access_token")
    if not token:
        raise Exception("No access_token returned by Dailymotion.")
    return token


def get_user_info(token: str) -> dict:
    """Returns basic user info (screenname, username, id) using a valid token."""
    resp = requests.get(
        f"{DAILYMOTION_ME}?fields=screenname,username,id",
        headers=_auth_header(token),
        timeout=10,
        verify=False,
    )
    if resp.status_code != 200:
        raise Exception(f"User info fetch failed ({resp.status_code}): {resp.text[:200]}")
    return resp.json()


class AuthWorker(QThread):
    """Authenticate one account config dict via password grant."""
    success = pyqtSignal(str, str)   # (screenname, token)
    error   = pyqtSignal(str)

    def __init__(self, account: dict):
        """
        account dict keys: client_id, client_secret, email, password, access_token (optional)
        """
        super().__init__()
        self.account = account

    def run(self):
        try:
            # Fast path: validate saved token
            token = self.account.get("access_token", "")
            if token:
                try:
                    info = get_user_info(token)
                    name = info.get("screenname") or info.get("username") or "Channel"
                    self.success.emit(name, token)
                    return
                except Exception:
                    pass  # token expired, fall through to re-login

            # Full password login
            token = password_login(
                self.account.get("client_id", ""),
                self.account.get("client_secret", ""),
                self.account.get("email", ""),
                self.account.get("password", ""),
            )
            info = get_user_info(token)
            name = info.get("screenname") or info.get("username") or "Channel"
            self.success.emit(name, token)
        except Exception as e:
            self.error.emit(str(e))


class UploadWorker(QThread):
    """Uploads a video to Dailymotion with precise real-time progress updates."""
    progress = pyqtSignal(float, str)   # (fraction 0-1, info_text)
    status   = pyqtSignal(str)          # status messages
    success  = pyqtSignal(str)          # video_id on success
    error    = pyqtSignal(str)          # error message

    def __init__(self, account: dict, file_path: str, metadata: dict):
        """
        account  - must contain a valid 'access_token' key.
        metadata - keys: title, description, tags, category, publish (bool)
        """
        super().__init__()
        self.account    = account
        self.file_path  = file_path
        self.metadata   = metadata
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found: {self.file_path}")

            token = self.account.get("access_token", "")
            if not token:
                raise Exception("No access token — please login to this channel first.")

            headers = _auth_header(token)

            # Step 1: Get upload URL
            self.status.emit("Requesting upload URL...")
            res = requests.get(
                f"{DAILYMOTION_API}/file/upload",
                headers=headers, verify=False, timeout=15,
            )
            if res.status_code == 401:
                raise Exception("Token expired. Please re-login to this channel.")
            if res.status_code != 200:
                raise Exception(f"Upload URL error ({res.status_code}): {res.text[:200]}")

            upload_url = res.json().get("upload_url")
            if not upload_url:
                raise Exception("Dailymotion did not return an upload URL.")

            if self._cancelled:
                return

            # Step 2: Stream file via multipart
            self.status.emit("Streaming video to Dailymotion...")

            boundary    = f"----DM{uuid.uuid4().hex}"
            filename    = os.path.basename(self.file_path)
            file_size   = os.path.getsize(self.file_path)

            header_part = (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                "Content-Type: application/octet-stream\r\n\r\n"
            ).encode()
            footer_part = f"\r\n--{boundary}--\r\n".encode()
            total_bytes = len(header_part) + file_size + len(footer_part)
            mb_total    = total_bytes / (1024 * 1024)

            def _stream():
                yield header_part
                bytes_sent = len(header_part)
                chunk_size = 256 * 1024

                with open(self.file_path, "rb") as fh:
                    while not self._cancelled:
                        chunk = fh.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
                        bytes_sent += len(chunk)
                        frac    = bytes_sent / total_bytes
                        mb_sent = bytes_sent / (1024 * 1024)
                        self.progress.emit(frac, f"{mb_sent:.1f} / {mb_total:.1f} MB")

                if not self._cancelled:
                    yield footer_part
                    self.progress.emit(1.0, f"{mb_total:.1f} / {mb_total:.1f} MB")

            upload_headers = {
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Content-Length": str(total_bytes),
                **headers,
            }
            up_res = requests.post(
                upload_url, data=_stream(),
                headers=upload_headers, verify=False, timeout=7200,
            )

            if self._cancelled:
                self.status.emit("Upload cancelled.")
                return

            if up_res.status_code != 200:
                raise Exception(f"Upload failed ({up_res.status_code}): {up_res.text[:200]}")

            uploaded_url = up_res.json().get("url")
            if not uploaded_url:
                raise Exception("No file URL returned after upload.")

            # Step 3: Create video object
            self.status.emit("Registering video on channel...")
            payload = {
                "url":         uploaded_url,
                "title":       self.metadata.get("title", "Video"),
                "description": self.metadata.get("description", ""),
                "tags":        self.metadata.get("tags", ""),
                "channel":     self.metadata.get("category", "tech"),
                "published":   "true" if self.metadata.get("publish", True) else "false",
            }
            create_res = requests.post(
                f"{DAILYMOTION_API}/me/videos",
                data=payload, headers=headers, verify=False, timeout=30,
            )
            if create_res.status_code != 200:
                raise Exception(
                    f"Video creation failed ({create_res.status_code}): {create_res.text[:200]}"
                )

            video_id = create_res.json().get("id")
            if not video_id:
                raise Exception("Video created but no ID was returned.")

            self.success.emit(video_id)

        except Exception as e:
            self.error.emit(str(e))
