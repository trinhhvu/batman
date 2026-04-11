"""
main.py — Entry Point for TRACK Sync App
========================================
Runs the PyQT5 application.
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui import TrackerApp

from PyQt5.QtCore import Qt

def main():
    try:
        # Enable High DPI scaling
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        window = TrackerApp()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        with open("crash.log", "w") as f:
            f.write(traceback.format_exc())
        print("CRASH LOGGED TO crash.log")
        sys.exit(1)

if __name__ == "__main__":
    main()
