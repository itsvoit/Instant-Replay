import sys

import qdarkstyle
from PyQt5.QtWidgets import QApplication

from gui.controller import Controller
from gui.gui import UiMainWindow


class ScreenRecorder(QApplication):
    def __init__(self, argv):
        super(ScreenRecorder, self).__init__(argv)
        self.view = UiMainWindow()
        self.controller = Controller(self.view)
        self.tray = self.controller.create_tray()
        self.tray.start()

        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def exec(self) -> int:
        out = super().exec()
        self.tray.shutdown()
        return out


if __name__ == "__main__":
    app = ScreenRecorder(sys.argv)
    sys.exit(app.exec())
