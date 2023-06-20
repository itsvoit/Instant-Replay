import sys
from PyQt5.QtWidgets import QApplication
from shotting_app.gui.gui import UiMainWindow
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
        # najlepsza opcja byloby chyba zwracanie slownika <wartość: lista wartosci>,
        # bo boxy i inne, przyjmuja liste stringow i moge dodac od razu te opcje
        # no i pierwsza wartoscia jest opcja z .conf

        # todo zwraca slownik z ustawieniami
        return {'resolution': ['1920x1080'],
                'fps': ['15', '30','50', '60'],
                'codec': ['H.264', 'H.265'],
                'display': ['Screen 1', 'Screen 2'],
                'video_hotkey': 'Ctrl+X',
                'screen_hotkey': 'Ctrl+Y',
                'save_sound': False,
                'quality': 85,
                'duration': 30,
                'video_path': './Wideo',
                'screen_path': './ScreenShoots',
                'ram_ussage': 400}

    def get_default_settings(self):
        # todo zwraca default ustawienia
        return {'resolution': ['1920x1080'],
                'fps': ['15', '30', '50', '60'],
                'codec': ['H.264', 'H.265'],
                'display': ['Screen 1', 'Screen 2'],
                'video_hotkey': 'Ctrl+X',
                'screen_hotkey': 'Ctrl+Y',
                'save_sound': False,
                'quality': 85,
                'duration': 30,
                'video_path': './Wideo',
                'screen_path': './ScreenShoots',
                'ram_ussage': 400}

    def save_settings(self, settings):
        # todo zapisuje wartosc settings, wczesniej musi byc zrobione obliczanie ramu
        # i wpisanie wartosci do settings['ram_usage'], po tym zwraca settings['ram_usage']
        return {'resolution': ['1920x1080'],
                'fps': ['15', '30', '50', '60'],
                'codec': ['H.264', 'H.265'],
                'display': ['Screen 1', 'Screen 2'],
                'video_hotkey': 'Ctrl+X',
                'screen_hotkey': 'Ctrl+Y',
                'save_sound': False,
                'quality': 85,
                'duration': 30,
                'video_path': './Wideo',
                'screen_path': './ScreenShoots',
                'ram_ussage': 400}

    def start_capture(self):
        ...

    def stop_capture(self):
        ...

    def change_config(self):
        ...
