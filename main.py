"""
main.py — Entry Point for Batman v2 Unified App
================================================
Launches the unified Batman v2 application combining:
  - Video Downloader (Dailymotion)
  - Video Analytics (Batman v1)

Run: python main.py
"""

import sys
from PyQt5.QtWidgets import QApplication
from app import DDProjectApp


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DDProjectApp()
    window.show()
    sys.exit(app.exec_())
