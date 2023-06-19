import sys

from PyQt5.QtWidgets import QMainWindow, QApplication
from gui import UiMainWindow
import qdarkstyle


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = UiMainWindow()
        self.ui.setupUi(self)

        self.ui.main_stacked_widget.setCurrentIndex(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # qdarktheme.setup_theme()

    window = MainWindow()  # Przykładowe okno MainWindow, należy je zdefiniować
    window.show()
    sys.exit(app.exec_())
