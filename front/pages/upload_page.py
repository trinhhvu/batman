"""
front/pages/upload_page.py — Multi-Channel Dailymotion Uploader Tab
=====================================================================
Supports saving, switching, and uploading to multiple Dailymotion channels.
Each channel account is stored independently in config.json.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QProgressBar, QFrame, QMessageBox, QFileDialog, QTextEdit,
    QListView, QCheckBox, QScrollArea, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSlot

from front.design import COLORS as C, FONT_HEADLINE, action_btn_style, danger_btn_style
from back.config import load_config, save_config
from back.upload_worker import AuthWorker, UploadWorker

# Sentinel text for the "add new" dropdown item
_ADD_NEW = "[+ Add new channel]"


class UploadPage(QWidget):
    """Multi-channel Dailymotion upload dashboard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UploadPage")

        self._auth_worker   = None
        self._upload_worker = None

        # In-memory list of account dicts (mirrors config.json)
        self._accounts: list[dict] = []
        self._active_idx: int = -1   # index into self._accounts

        self._build_ui()
        self._load_accounts()

    # ─────────────────────────────────────────────────────────
    # UI Construction
    # ─────────────────────────────────────────────────────────
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(40, 40, 40, 40)
        main.setSpacing(28)

        # ── Header ──────────────────────────────────────────
        header = QVBoxLayout()
        header.setSpacing(4)
        title = QLabel("Dailymotion Upload")
        title.setObjectName("PageTitle")
        title.setFont(QFont(FONT_HEADLINE, 28, QFont.Bold))
        header.addWidget(title)
        sub = QLabel("Manage multiple channels — batch upload videos without browser.")
        sub.setObjectName("SubtitleLabel")
        header.addWidget(sub)
        main.addLayout(header)

        # ── Body: 2-column layout ────────────────────────────
        body = QHBoxLayout()
        body.setSpacing(28)

        # ─── LEFT COLUMN ─────────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(20)

        # 1. Channel selector card
        self.channel_card = QFrame()
        self.channel_card.setObjectName("BentoCard")
        cl = QVBoxLayout(self.channel_card)
        cl.setContentsMargins(24, 24, 24, 24)
        cl.setSpacing(14)

        ch_title = QLabel("CHANNEL ACCOUNTS")
        ch_title.setObjectName("SectionTitle")
        cl.addWidget(ch_title)

        # Dropdown row
        dd_row = QHBoxLayout()
        dd_row.setSpacing(10)
        self.channel_combo = QComboBox()
        self.channel_combo.setView(QListView())
        self.channel_combo.setMinimumHeight(44)
        self.channel_combo.currentIndexChanged.connect(self._on_channel_changed)
        dd_row.addWidget(self.channel_combo, 1)

        self.delete_ch_btn = QPushButton("DELETE")
        self.delete_ch_btn.setFixedSize(90, 44)
        self.delete_ch_btn.setStyleSheet(
            f"QPushButton {{ background-color: transparent; color: {C['error']}; "
            f"border: 1px solid {C['error']}; border-radius: 10px; "
            f"font-size: 11px; font-weight: 800; }}"
        )
        self.delete_ch_btn.clicked.connect(self._delete_current_account)
        dd_row.addWidget(self.delete_ch_btn)
        cl.addLayout(dd_row)

        # Status badge
        self.status_badge = QLabel("Unauthenticated")
        self.status_badge.setObjectName("GeoBanner")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setMinimumHeight(34)
        self._set_badge("disconnected", "Unauthenticated")
        cl.addWidget(self.status_badge)

        # Credentials
        self.account_name_input = QLineEdit()
        self.account_name_input.setPlaceholderText("Channel name (e.g. Channel 1)")
        cl.addWidget(self.account_name_input)

        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Client ID (API Key)")
        cl.addWidget(self.client_id_input)

        self.client_secret_input = QLineEdit()
        self.client_secret_input.setPlaceholderText("Client Secret")
        self.client_secret_input.setEchoMode(QLineEdit.Password)
        cl.addWidget(self.client_secret_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Dailymotion email")
        cl.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Account password")
        self.password_input.setEchoMode(QLineEdit.Password)
        cl.addWidget(self.password_input)

        # Auth buttons
        auth_row = QHBoxLayout()
        auth_row.setSpacing(10)

        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setObjectName("ActionButton")
        self.login_btn.clicked.connect(self._handle_login)
        auth_row.addWidget(self.login_btn, 1)

        self.save_btn = QPushButton("SAVE INFO")
        self.save_btn.clicked.connect(self._save_current_account)
        auth_row.addWidget(self.save_btn, 1)
        cl.addLayout(auth_row)

        left.addWidget(self.channel_card)

        # 2. Progress card
        self.progress_card = QFrame()
        self.progress_card.setObjectName("BentoCard")
        pl = QVBoxLayout(self.progress_card)
        pl.setContentsMargins(24, 24, 24, 24)
        pl.setSpacing(14)

        prog_title = QLabel("UPLOAD PROGRESS")
        prog_title.setObjectName("SectionTitle")
        pl.addWidget(prog_title)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        pl.addWidget(self.progress_bar)

        self.progress_label = QLabel("Ready to upload")
        self.progress_label.setObjectName("SubtitleLabel")
        pl.addWidget(self.progress_label)

        self.cancel_btn = QPushButton("CANCEL UPLOAD")
        self.cancel_btn.setStyleSheet(danger_btn_style())
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._cancel_upload)
        pl.addWidget(self.cancel_btn)

        left.addWidget(self.progress_card)
        left.addStretch()
        body.addLayout(left, 2)

        # ─── RIGHT COLUMN ──────────────────────────────────────
        self.details_card = QFrame()
        self.details_card.setObjectName("BentoCard")
        dl = QVBoxLayout(self.details_card)
        dl.setContentsMargins(28, 28, 28, 28)
        dl.setSpacing(18)

        det_title = QLabel("VIDEO METADATA")
        det_title.setObjectName("SectionTitle")
        dl.addWidget(det_title)

        # File select
        file_row = QHBoxLayout()
        file_row.setSpacing(10)
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select video file...")
        self.file_input.setReadOnly(True)
        file_row.addWidget(self.file_input, 1)

        browse_btn = QPushButton("SELECT FILE")
        browse_btn.setObjectName("ActionButton")
        browse_btn.setFixedWidth(130)
        browse_btn.clicked.connect(self._select_file)
        file_row.addWidget(browse_btn)
        dl.addLayout(file_row)

        self.video_title_input = QLineEdit()
        self.video_title_input.setPlaceholderText("Video title")
        dl.addWidget(self.video_title_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Video description (optional)...")
        self.desc_input.setStyleSheet(
            f"QTextEdit {{ background-color: {C['surface_container_low']}; "
            f"border: none; border-radius: 10px; padding: 12px 16px; "
            f"color: {C['on_surface']}; }}"
        )
        self.desc_input.setMaximumHeight(110)
        dl.addWidget(self.desc_input)

        cat_tag_row = QHBoxLayout()
        cat_tag_row.setSpacing(14)

        self.category_combo = QComboBox()
        self.category_combo.setView(QListView())
        self.category_combo.setMinimumHeight(44)
        self.categories_map = {
            "Tech & Science": "tech",
            "Comedy & Fun": "fun",
            "News & Politics": "news",
            "Music": "music",
            "Sports": "sport",
            "Lifestyle": "lifestyle",
            "Gaming": "videogames",
            "Animals": "animals",
            "Travel": "travel",
            "Auto & Vehicles": "vehicles",
        }
        self.category_combo.addItems(list(self.categories_map.keys()))
        cat_tag_row.addWidget(self.category_combo, 1)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags (comma separated)")
        cat_tag_row.addWidget(self.tags_input, 1)
        dl.addLayout(cat_tag_row)

        self.publish_chk = QCheckBox("Publish after upload")
        self.publish_chk.setChecked(True)
        self.publish_chk.setCursor(Qt.PointingHandCursor)
        dl.addWidget(self.publish_chk)

        dl.addStretch()

        self.upload_btn = QPushButton("UPLOAD TO DAILYMOTION")
        self.upload_btn.setObjectName("ActionButton")
        self.upload_btn.setMinimumHeight(52)
        self.upload_btn.clicked.connect(self._start_upload)
        dl.addWidget(self.upload_btn)

        body.addWidget(self.details_card, 3)
        main.addLayout(body)

    # ─────────────────────────────────────────────────────────
    # Account helpers
    # ─────────────────────────────────────────────────────────
    def _load_accounts(self):
        """Read accounts from config.json and populate the dropdown."""
        cfg = load_config()
        self._accounts = cfg.get("dailymotion_accounts", [])
        self._rebuild_combo()

    def _save_accounts_to_config(self):
        cfg = load_config()
        cfg["dailymotion_accounts"] = self._accounts
        save_config(cfg)

    def _rebuild_combo(self):
        """Sync QComboBox items with self._accounts (block signals during rebuild)."""
        self.channel_combo.blockSignals(True)
        self.channel_combo.clear()

        for acc in self._accounts:
            self.channel_combo.addItem(acc.get("name", "Unnamed channel"))
        self.channel_combo.addItem(_ADD_NEW)

        # Restore previous selection or default to first real account
        if self._accounts:
            idx = max(0, min(self._active_idx, len(self._accounts) - 1))
            self.channel_combo.setCurrentIndex(idx)
            self._active_idx = idx
        else:
            # No accounts yet → force "add new" state
            self.channel_combo.setCurrentIndex(0)  # which is _ADD_NEW
            self._active_idx = -1

        self.channel_combo.blockSignals(False)
        self._sync_form_to_account()

    def _sync_form_to_account(self):
        """Fill form fields from the current active account dict."""
        acc = self._active_account()
        if acc is None:
            # Clear form for new account entry
            self.account_name_input.clear()
            self.client_id_input.clear()
            self.client_secret_input.clear()
            self.email_input.clear()
            self.password_input.clear()
            self._set_badge("disconnected", "Unauthenticated")
            self.delete_ch_btn.setEnabled(False)
            return

        self.delete_ch_btn.setEnabled(True)
        self.account_name_input.setText(acc.get("name", ""))
        self.client_id_input.setText(acc.get("client_id", ""))
        self.client_secret_input.setText(acc.get("client_secret", ""))
        self.email_input.setText(acc.get("email", ""))
        self.password_input.setText(acc.get("password", ""))

        if acc.get("access_token"):
            self._set_badge("checking", "Checking token...")
            self._run_auth(acc, silent=True)
        else:
            self._set_badge("disconnected", "Not logged in")

    def _active_account(self) -> dict | None:
        if 0 <= self._active_idx < len(self._accounts):
            return self._accounts[self._active_idx]
        return None

    def _read_form_as_account(self) -> dict:
        """Build an account dict from current form fields."""
        acc = self._active_account() or {}
        return {
            "name":          self.account_name_input.text().strip() or "Unnamed channel",
            "client_id":     self.client_id_input.text().strip(),
            "client_secret": self.client_secret_input.text().strip(),
            "email":         self.email_input.text().strip(),
            "password":      self.password_input.text().strip(),
            "access_token":  acc.get("access_token", ""),
        }

    # ─────────────────────────────────────────────────────────
    # Slots — Channel Combo
    # ─────────────────────────────────────────────────────────
    def _on_channel_changed(self, idx: int):
        total = self.channel_combo.count()
        if idx == total - 1:
            # User chose [+ Add new channel]
            self._active_idx = -1
        else:
            self._active_idx = idx
        self._sync_form_to_account()

    # ─────────────────────────────────────────────────────────
    # Save / Delete Account
    # ─────────────────────────────────────────────────────────
    def _save_current_account(self):
        new_acc = self._read_form_as_account()
        if not new_acc["client_id"] or not new_acc["email"]:
            QMessageBox.warning(self, "Missing info", "Please enter at least Client ID and Email.")
            return

        if self._active_idx == -1:
            # Adding a brand-new account
            self._accounts.append(new_acc)
            self._active_idx = len(self._accounts) - 1
        else:
            # Update existing
            self._accounts[self._active_idx] = new_acc

        self._save_accounts_to_config()
        self._rebuild_combo()
        QMessageBox.information(self, "Saved", f"Saved kênh: {new_acc['name']}")

    def _delete_current_account(self):
        if self._active_idx < 0 or self._active_idx >= len(self._accounts):
            return
        name = self._accounts[self._active_idx].get("name", "")
        reply = QMessageBox.question(
            self, "Delete channel",
            f"Bạn có chắc muốn xoá kênh \"{name}\" không?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._accounts.pop(self._active_idx)
        self._active_idx = max(0, self._active_idx - 1) if self._accounts else -1
        self._save_accounts_to_config()
        self._rebuild_combo()

    # ─────────────────────────────────────────────────────────
    # Authentication
    # ─────────────────────────────────────────────────────────
    def _run_auth(self, account: dict, silent: bool = False):
        """Run AuthWorker for the given account dict."""
        if self._auth_worker and self._auth_worker.isRunning():
            return

        self._auth_worker = AuthWorker(account)
        if silent:
            self._auth_worker.success.connect(
                lambda name, tok: self._on_auth_success(name, tok, silent=True)
            )
            self._auth_worker.error.connect(self._on_auth_error_silent)
        else:
            self._auth_worker.success.connect(
                lambda name, tok: self._on_auth_success(name, tok, silent=False)
            )
            self._auth_worker.error.connect(self._on_auth_error)
        self._auth_worker.start()

    def _handle_login(self):
        acc = self._read_form_as_account()
        if not acc["client_id"] or not acc["email"] or not acc["password"]:
            QMessageBox.warning(
                self, "Missing info",
                "Please enter Client ID, Email, and Password to login."
            )
            return
        # Temporarily store form data so AuthWorker can use it
        self._pending_login_acc = acc
        self._set_badge("checking", "Logging in...")
        self._set_auth_buttons_enabled(False)
        self._run_auth(acc, silent=False)

    @pyqtSlot(str, str)
    def _on_auth_success(self, screenname: str, token: str, silent: bool = False):
        # Update the account in memory with the fresh token
        acc = self._active_account()
        if acc is not None:
            acc["access_token"] = token
        elif hasattr(self, "_pending_login_acc"):
            self._pending_login_acc["access_token"] = token
            acc = self._pending_login_acc

        # Persist token
        if self._active_idx >= 0 and self._active_idx < len(self._accounts):
            self._accounts[self._active_idx]["access_token"] = token
            self._save_accounts_to_config()

        self._set_badge("connected", f"Connected: {screenname}")
        if not silent:
            self._set_auth_buttons_enabled(True)
            # Auto-save the account including the new token
            self._save_current_account_silently(token)

    @pyqtSlot(str)
    def _on_auth_error(self, msg: str):
        self._set_badge("disconnected", "Login error")
        self._set_auth_buttons_enabled(True)
        QMessageBox.critical(self, "Auth error", f"Failed to login:\n{msg}")

    @pyqtSlot(str)
    def _on_auth_error_silent(self, _msg: str):
        self._set_badge("disconnected", "Token expired — please login again")

    def _save_current_account_silently(self, token: str = ""):
        new_acc = self._read_form_as_account()
        if token:
            new_acc["access_token"] = token

        if self._active_idx == -1:
            self._accounts.append(new_acc)
            self._active_idx = len(self._accounts) - 1
        else:
            self._accounts[self._active_idx] = new_acc

        self._save_accounts_to_config()
        self._rebuild_combo()

    def _set_auth_buttons_enabled(self, enabled: bool):
        self.login_btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)

    # ─────────────────────────────────────────────────────────
    # Status badge helper
    # ─────────────────────────────────────────────────────────
    def _set_badge(self, state: str, text: str):
        """state: 'connected' | 'disconnected' | 'checking'"""
        if state == "connected":
            bg, fg = C["surface_container_low"], C["success"]
        elif state == "checking":
            bg, fg = C["surface_container"], C["on_surface_variant"]
        else:
            bg, fg = C["error_container"], C["error"]

        self.status_badge.setText(text)
        self.status_badge.setStyleSheet(
            f"QLabel {{ background-color: {bg}; color: {fg}; "
            f"border-radius: 8px; font-weight: 800; font-size: 11px; "
            f"letter-spacing: 0.5px; padding: 6px 12px; }}"
        )

    # ─────────────────────────────────────────────────────────
    # File select
    # ─────────────────────────────────────────────────────────
    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select video file", "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv)"
        )
        if path:
            self.file_input.setText(path)
            if not self.video_title_input.text().strip():
                self.video_title_input.setText(
                    os.path.splitext(os.path.basename(path))[0]
                )

    # ─────────────────────────────────────────────────────────
    # Upload
    # ─────────────────────────────────────────────────────────
    def _start_upload(self):
        if self._upload_worker and self._upload_worker.isRunning():
            return

        acc = self._active_account()
        if acc is None:
            QMessageBox.warning(self, "No channel selected", "Please select or add a channel before uploading.")
            return

        if not acc.get("access_token"):
            QMessageBox.warning(self, "Not logged in",
                                "This channel is unauthenticated. Please login first.")
            return

        file_path = self.file_input.text().strip()
        title     = self.video_title_input.text().strip()

        if not file_path:
            QMessageBox.warning(self, "Select file", "Please select a video file to upload.")
            return
        if not title:
            QMessageBox.warning(self, "Empty title", "Please enter a title for the video.")
            return

        cat_key = self.categories_map.get(self.category_combo.currentText(), "tech")
        metadata = {
            "title":       title,
            "description": self.desc_input.toPlainText().strip(),
            "tags":        self.tags_input.text().strip(),
            "category":    cat_key,
            "publish":     self.publish_chk.isChecked(),
        }

        self._set_upload_state(uploading=True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Preparing...")

        self._upload_worker = UploadWorker(acc, file_path, metadata)
        self._upload_worker.progress.connect(self._on_progress)
        self._upload_worker.status.connect(self._on_status)
        self._upload_worker.success.connect(self._on_success)
        self._upload_worker.error.connect(self._on_error)
        self._upload_worker.start()

    def _set_upload_state(self, uploading: bool):
        self.upload_btn.setEnabled(not uploading)
        self.upload_btn.setText("UPLOADING..." if uploading else "UPLOAD TO DAILYMOTION")
        self.cancel_btn.setVisible(uploading)
        self._set_auth_buttons_enabled(not uploading)

    @pyqtSlot(float, str)
    def _on_progress(self, frac: float, info: str):
        self.progress_bar.setValue(int(frac * 1000))
        self.progress_label.setText(f"Uploading: {info}  ({frac * 100:.1f}%)")

    @pyqtSlot(str)
    def _on_status(self, text: str):
        self.progress_label.setText(text)

    @pyqtSlot(str)
    def _on_success(self, video_id: str):
        self._set_upload_state(uploading=False)
        self.progress_bar.setValue(1000)
        self.progress_label.setText("Upload successful!")
        self.file_input.clear()
        self.video_title_input.clear()
        self.desc_input.clear()
        self.tags_input.clear()

        acc_name = (self._active_account() or {}).get("name", "channel")
        QMessageBox.information(
            self, "Upload successful!",
            f"Video uploaded to {acc_name}!\n\n"
            f"Video ID: {video_id}\n"
            f"URL: https://www.dailymotion.com/video/{video_id}"
        )

    @pyqtSlot(str)
    def _on_error(self, msg: str):
        self._set_upload_state(uploading=False)
        self.progress_label.setText("Upload failed")
        QMessageBox.critical(self, "Upload Error", f"An error occurred:\n{msg}")

    def _cancel_upload(self):
        if self._upload_worker and self._upload_worker.isRunning():
            reply = QMessageBox.question(
                self, "Cancel Upload",
                "Are you sure you want to cancel the upload?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._upload_worker.cancel()
                self._upload_worker.wait()
                self._set_upload_state(uploading=False)
                self.progress_bar.setValue(0)
                self.progress_label.setText("Upload cancelled.")

    def refresh_theme(self):
        """Standardized theme refresh — handled by QApplication stylesheet."""
        pass
