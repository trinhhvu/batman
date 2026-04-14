"""
back — Business logic layer (API, downloads, workers)
No PyQt widget imports allowed here (only QThread/QObject/signals for threading).
"""
import os

TRACK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
