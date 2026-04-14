"""
back/config.py — Centralized Config Persistence
=================================================
Single source of truth for loading/saving config.json and download path.
Eliminates the duplicated helpers that were scattered across UI files.
"""

import os
import json

from back import TRACK_ROOT

CONFIG_PATH = os.path.join(TRACK_ROOT, "config.json")


def load_config() -> dict:
    """Load the full config dict from config.json."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg: dict):
    """Save the full config dict to config.json."""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4)


def load_download_path() -> str:
    """Read saved download_folder from config.json."""
    try:
        cfg = load_config()
        folder = cfg.get("download_folder", "downloads")
        if os.path.isabs(folder):
            return folder
        return os.path.join(TRACK_ROOT, folder)
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Downloads")


def save_download_path(path: str):
    """Persist the download folder into config.json."""
    cfg = load_config()
    cfg["download_folder"] = path
    save_config(cfg)
