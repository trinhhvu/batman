"""
tracker.py — Backend Logic for Dailymotion TRACK App
=====================================================
Handles:
  - OAuth2 browser-based authentication
  - yt-dlp video downloading

Dependencies: requests, yt-dlp
"""

import os
import re
import json
import time
import requests
import yt_dlp
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


# Generic Browser User-Agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
HISTORY_PATH = os.path.join(BASE_DIR, "history.json")

DAILYMOTION_API = "https://api.dailymotion.com"
DAILYMOTION_AUTH = "https://www.dailymotion.com/oauth/authorize"
DAILYMOTION_TOKEN = f"{DAILYMOTION_API}/oauth/token"
DAILYMOTION_ME = f"{DAILYMOTION_API}/me"

OAUTH_PORT = 10101
OAUTH_REDIRECT = f"http://127.0.0.1:{OAUTH_PORT}"
OAUTH_SCOPE = "manage_videos userinfo"
OAUTH_TIMEOUT_SECONDS = 120


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def clean_ansi(text: str) -> str:
    """Strip ANSI escape codes from yt-dlp output strings."""
    if not isinstance(text, str):
        return str(text)
    return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', text)


def _make_auth_header(token: str) -> dict:
    """Build the Authorization header dict."""
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }


# ---------------------------------------------------------------------------
# OAuth Callback Handler
# ---------------------------------------------------------------------------
class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Tiny HTTP handler that captures the OAuth authorization code."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        query = parse_qs(urlparse(self.path).query)
        code = query.get("code", [None])[0]

        if code:
            self.server.auth_code = code
            body = (
                "<html><body style='font-family:sans-serif;text-align:center;"
                "padding-top:50px'>"
                "<h1>✅ Success!</h1>"
                "<p>Authentication complete. You can close this window.</p>"
                "</body></html>"
            )
        else:
            body = (
                "<html><body style='font-family:sans-serif;text-align:center;"
                "padding-top:50px'>"
                "<h1>❌ Error</h1>"
                "<p>Authentication failed. Please try again.</p>"
                "</body></html>"
            )
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default request logging."""
        return


# ---------------------------------------------------------------------------
# Main Tracker Class
# ---------------------------------------------------------------------------
class DailymotionTracker:
    """Handles config, authentication, and downloading."""

    def __init__(self):
        self.config: dict = {}
        self.history: list = []
        self.access_token: str | None = None

        self._load_config()
        self._load_history()
        self._init_download_path()

    # --- Config & History ---------------------------------------------------

    def _load_config(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def save_config(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def _load_history(self):
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4)

    def _init_download_path(self):
        folder = self.config.get("download_folder", "downloads")
        if not os.path.isabs(folder):
            folder = os.path.join(BASE_DIR, folder)
        self.download_path = folder
        os.makedirs(self.download_path, exist_ok=True)

    def set_download_path(self, path: str):
        self.download_path = path
        self.config["download_folder"] = path
        self.save_config()
        os.makedirs(self.download_path, exist_ok=True)

    # --- Authentication -----------------------------------------------------

    def start_browser_auth(self) -> str:
        """Run OAuth2 Authorization Code flow via local HTTP callback."""
        client_id = self.config.get("api_key", "").strip()
        client_secret = self.config.get("api_secret", "").strip()
        if not client_id or not client_secret:
            raise Exception("Please enter API Key (Client ID) and API Secret first.")

        auth_url = (
            f"{DAILYMOTION_AUTH}?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={OAUTH_REDIRECT}"
            f"&scope={OAUTH_SCOPE}"
        )

        server = HTTPServer(("127.0.0.1", OAUTH_PORT), _OAuthCallbackHandler)
        server.auth_code = None
        webbrowser.open(auth_url)

        start = time.time()
        while server.auth_code is None and (time.time() - start) < OAUTH_TIMEOUT_SECONDS:
            server.handle_request()

        if not server.auth_code:
            raise Exception("Authentication timed out or was cancelled.")

        # Exchange authorization code for access token
        resp = requests.post(DAILYMOTION_TOKEN, data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": OAUTH_REDIRECT,
            "code": server.auth_code,
        })

        if resp.status_code != 200:
            raise Exception(f"Token exchange failed ({resp.status_code}): {resp.text[:200]}")

        token = resp.json().get("access_token")
        self.access_token = token
        self.config["access_token"] = token
        self.save_config()
        return token

    def login_via_password(self, email: str, password: str) -> str:
        """Fetch token directly using Dailymotion credentials (no redirect needed)."""
        client_id = self.config.get("api_key", "").strip()
        client_secret = self.config.get("api_secret", "").strip()
        if not client_id or not client_secret:
            raise Exception("Please enter API Key and Secret first.")

        resp = requests.post(DAILYMOTION_TOKEN, data={
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": email,
            "password": password,
            "scope": OAUTH_SCOPE
        }, headers={"User-Agent": USER_AGENT})

        if resp.status_code != 200:
            raise Exception(f"Password login failed ({resp.status_code}): {resp.text[:200]}")

        token = resp.json().get("access_token")
        self.access_token = token
        self.config["access_token"] = token
        self.save_config()
        return token

    def get_access_token(self) -> str:
        """Return cached token or trigger browser auth if missing."""
        if self.access_token:
            return self.access_token
        saved = self.config.get("access_token")
        if saved:
            self.access_token = saved
            return saved
        return self.start_browser_auth()

    def _refresh_token_on_401(self) -> str:
        """Clear current token and re-authenticate."""
        self.access_token = None
        self.config.pop("access_token", None)
        return self.start_browser_auth()

    def get_user_info(self) -> dict:
        """Fetch current user profile. Re-auths on 401."""
        token = self.get_access_token()
        url = f"{DAILYMOTION_ME}?fields=screenname,username,id"
        resp = requests.get(url, headers=_make_auth_header(token))

        if resp.status_code == 200:
            return resp.json()

        if resp.status_code == 401:
            token = self._refresh_token_on_401()
            resp = requests.get(url, headers=_make_auth_header(token))
            if resp.status_code == 200:
                return resp.json()

        raise Exception(f"Auth failed (HTTP {resp.status_code}): {resp.text[:200]}")

    # --- Video Scanning (yt-dlp) --------------------------------------------

    def get_latest_videos(self, channel_url: str, max_items: int = 20) -> list[dict]:
        """Scan a Dailymotion channel and return video metadata."""
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "force_generic_extractor": True,
            "nocheckcertificate": True,
            "legacyserverconnect": True,
            "force_ipv4": True,
            "user_agent": USER_AGENT,
            "referer": "https://www.dailymotion.com/"
        }
        results = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(channel_url, download=False)
                if not info:
                    return []

                # API Fields to fetch for parity with Analyze page
                api_fields = (
                    "thumbnail_480_url,thumbnail_720_url,owner,channel,"
                    "title,views_total,views_last_day,views_last_hour,"
                    "updated_time,url,geoblocking,duration"
                )
                api_url_tmpl = "https://api.dailymotion.com/video/{video_id}?fields=" + api_fields
                headers = {
                    "User-Agent": USER_AGENT,
                    "Referer": "https://www.dailymotion.com/"
                }

                for entry in (info.get("entries") or [])[:max_items]:
                    if not entry:
                        continue
                    vid = entry.get("id")
                    try:
                        # Fetch full details via API (same as Analyze page)
                        res = requests.get(
                            api_url_tmpl.format(video_id=vid),
                            headers=headers, verify=False, timeout=8
                        )
                        if res.status_code == 200:
                            data = res.json()
                            # Sync total views (API lag fix)
                            v_total = int(data.get('views_total') or 0)
                            v_day = int(data.get('views_last_day') or 0)
                            v_hour = int(data.get('views_last_hour') or 0)
                            data['views_total'] = max(v_total, v_day, v_hour)
                            
                            # Add duration_string
                            dur = data.get("duration", 0)
                            mm, ss = divmod(dur, 60)
                            data["duration_string"] = f"{int(mm):02d}:{int(ss):02d}"
                            # Add thumbnail for card logic
                            data["thumbnail"] = data.get('thumbnail_720_url') or data.get('thumbnail_480_url') or data.get('thumbnail', '')
                            
                            results.append(data)
                        else:
                            # Fallback to basic yt-dlp info if API fails
                            v_url = f"https://www.dailymotion.com/video/{vid}"
                            full = ydl.extract_info(v_url, download=False)
                            dur = full.get("duration", 0)
                            mm, ss = divmod(dur, 60)
                            results.append({
                                "id": vid,
                                "url": v_url,
                                "title": full.get("title", entry.get("title", "Unknown")),
                                "view_count": full.get("view_count", 0),
                                "duration_string": f"{int(mm):02d}:{int(ss):02d}",
                                "thumbnail": full.get("thumbnail", ""),
                            })
                    except Exception:
                        results.append({
                            "id": vid,
                            "url": f"https://www.dailymotion.com/video/{vid}",
                            "title": entry.get("title", "Video"),
                            "duration_string": "00:00",
                        })
            except Exception:
                pass

        return results

    # --- Video Download (yt-dlp) --------------------------------------------

    def download_video(self, video_data: dict, progress_callback=None) -> tuple:
        """Download a video using yt-dlp. Returns (file_path, title, description)."""
        url = video_data["url"]

        ydl_opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best",
            "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "concurrent_fragment_downloads": 16,
            "nocheckcertificate": True,
            "legacyserverconnect": True,
            "force_ipv4": True,
            "user_agent": USER_AGENT,
            "referer": "https://www.dailymotion.com/"
        }

        if progress_callback:
            vid = video_data["id"]

            def _hook(d):
                if d["status"] != "downloading":
                    return
                try:
                    raw = clean_ansi(d.get("_percent_str", "0.0%")).replace("%", "").strip()
                    pct = float(raw) if raw else 0.0
                    speed = clean_ansi(d.get("_speed_str", "N/A")).strip()
                    progress_callback(vid, pct / 100.0, f"{pct:.1f}", speed)
                except Exception:
                    pass

            ydl_opts["progress_hooks"] = [_hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return (
                ydl.prepare_filename(info),
                info.get("title"),
                info.get("description", ""),
            )


