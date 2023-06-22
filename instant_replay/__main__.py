import sys

from instant_replay.app import ScreenRecorder

if __name__ == "__main__":
    app = ScreenRecorder(sys.argv)
    sys.exit(app.exec())
