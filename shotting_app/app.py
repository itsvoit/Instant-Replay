import sys

import qdarkstyle
from PyQt5.QtWidgets import QApplication

from shotting_app.gui.controller import Controller
from shotting_app.gui.gui import UiMainWindow


class ScreenRecorder(QApplication):
    def __init__(self, argv):
        super(ScreenRecorder, self).__init__(argv)
        verbose = True if len(argv) > 0 and argv[0] else False
        self.view = UiMainWindow(verbose)
        self.controller = Controller(self.view, verbose)
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
