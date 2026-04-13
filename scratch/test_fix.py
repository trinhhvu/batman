import sys
import os

# Add TRACK directory to path
sys.path.append(os.path.abspath("TRACK"))

from engine import DownloadEngine

def test_analysis():
    ydl_opts = {
        'verbose': True,
        'nocheckcertificate': True,
        'legacyserverconnect': True,
        'force_ipv4': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.dailymotion.com/'
    }
    import yt_dlp
    url = "https://www.dailymotion.com/video/xa594pe"
    print(f"Analyzing {url} with verbose=True...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        print("Success!")
        print(f"Title: {info.get('title')}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_analysis()
