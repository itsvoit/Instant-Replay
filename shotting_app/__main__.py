import sys

from shotting_app.app import ScreenRecorder

if __name__ == "__main__":
    app = ScreenRecorder(sys.argv)
    sys.exit(app.exec())
