import sys
import os

# Add TRACK directory to path
sys.path.append(os.path.abspath("TRACK"))

from tracker import DailymotionTracker

def test_tracker_scan():
    tracker = DailymotionTracker()
    # Use one of the failing IDs
    url = "https://www.dailymotion.com/video/xa594pe"
    print(f"Analyzing video {url} via Tracker...")
    try:
        results = tracker.get_latest_videos(url, max_items=2)
        print(f"Success! Found {len(results)} videos.")
        for v in results:
            print(f"- {v['title']} ({v['id']})")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_tracker_scan()
