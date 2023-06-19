import sys
from PyQt5.QtWidgets import QApplication
from gui import UiMainWindow
import qdarkstyle


class Controller:
    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.view = UiMainWindow(self)
        self.get_user_settings()
        self.view.show()
        sys.exit(app.exec())

    def get_user_settings(self):
        #najlepsza opcja byloby chyba zwracanie slownika <wartość: lista wartosci>,
        # bo boxy i inne, przyjmuja liste stringow i moge dodac od razu te opcje
        # no i pierwsza wartoscia jest jest opcja z .conf

        return ... #todo zwraca slownik z ustawieniami

    def get_default_settings(self):
        return ... #todo zwraca default ustawienia

    def save_settings(self, settings):
        #todo zapisuje wartosc settings, wczesniej musi byc zrobione obliczanie ramu
        # i wpisanie wartosci do settings['ram_ussage'], po tym zwraca settings['ram_ussage']
        return ...

    def start_capture(self):
        ...

    def stop_capture(self):
        ...

    def change_config(self):
        ...
