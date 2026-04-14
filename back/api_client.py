"""
back/api_client.py — Dailymotion Public API Client
====================================================
All HTTP requests to Dailymotion are centralized here.
NO PyQt imports. Pure Python + requests.
"""

import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT, "Referer": "https://www.dailymotion.com/"}

DETAIL_FIELDS = (
    "thumbnail_480_url,thumbnail_720_url,owner,channel,"
    "title,views_total,views_last_day,views_last_hour,"
    "updated_time,url,geoblocking"
)


def extract_video_id(text: str):
    """Extract Dailymotion video ID from a URL or raw text."""
    q = (text or '').strip()
    if not q:
        return None
    m = re.search(r'/video/([a-zA-Z0-9]+)', q)
    if m:
        return m.group(1)
    if re.fullmatch(r'[\w-]{6,16}', q):
        return q
    return None


def fetch_video_details(video_id: str) -> dict:
    """Fetch detailed video info from Dailymotion Public API."""
    url = f"https://api.dailymotion.com/video/{video_id}?fields={DETAIL_FIELDS}"
    res = requests.get(url, headers=HEADERS, verify=False, timeout=10)
    if res.status_code != 200:
        raise ValueError(f"API error ({res.status_code})")
    data = res.json()
    if data.get('error'):
        raise ValueError(data.get('message', 'Unknown error'))
    # Sync total views
    v_total = int(data.get('views_total') or 0)
    v_day = int(data.get('views_last_day') or 0)
    v_hour = int(data.get('views_last_hour') or 0)
    data['views_total'] = max(v_total, v_day, v_hour)
    return data


def search_videos(query: str, sort: str = 'trending', limit: int = 20) -> list:
    """Search Dailymotion videos by keyword."""
    url = "https://api.dailymotion.com/videos"
    params = {
        'search': query,
        'sort': sort,
        'limit': limit,
        'page': 1,
        'fields': 'id'
    }
    res = requests.get(url, params=params, verify=False, timeout=10)
    if res.status_code != 200:
        raise ValueError(f"Search API returned {res.status_code}")
    data = res.json()
    return [item['id'] for item in data.get('list', []) if 'id' in item]


def fetch_thumbnail_data(url: str) -> bytes:
    """Download thumbnail image data."""
    return requests.get(url, timeout=8).content
