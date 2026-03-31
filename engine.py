import yt_dlp
import os
import re
import time
from utils import get_ffmpeg_path

class DownloadEngine:
    def __init__(self, download_path):
        self.download_path = download_path

    def analyze_video(self, url):
        """Extracts video information using yt-dlp."""
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def get_ydl_opts(self, quality, progress_hook):
        """Configures yt-dlp options based on selected quality and hook."""
        # Quality mapping
        q_map = {
            "Best Available": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]/best"
        }
        fmt = q_map.get(quality, "best")
        
        return {
            'format': fmt,
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'ffmpeg_location': get_ffmpeg_path(),
            'concurrent_fragment_downloads': 16, 
            'retries': 20, 
            'fragment_retries': 20,
            'quiet': True, 
            'no_warnings': True
        }

    def start_download(self, url, quality, progress_hook):
        """Triggers the download for a given URL with error check."""
        if not url:
            raise ValueError("URL is empty or None")
            
        ydl_opts = self.get_ydl_opts(quality, progress_hook)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

def parse_progress(d):
    """Parses percent and speed from yt-dlp progress dictionary."""
    if not d or 'status' not in d:
        return None

    if d['status'] == 'downloading':
        p_str = d.get('_percent_str', '0%')
        # Remove ANSI color codes
        p_str = re.sub(r'\x1b\[[0-9;]*m', '', p_str).strip().replace('%', '')
        try:
            return float(p_str) / 100, p_str, d.get('_speed_str', 'N/A')
        except:
            return 0.0, "0", "N/A"
    return None
