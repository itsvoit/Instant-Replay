import json
import sys
from copy import copy

from PyQt5.QtWidgets import QApplication

from shotting_app import values, capture
from shotting_app.gui.gui import UiMainWindow
import qdarkstyle


def _save_config(config, file_name):
    with open(file_name, 'w') as file:
        json.dump(config, file, indent=4)


def load_config(file_name):
    try:
        with open(file_name, "r") as config:
            out_conf = json.load(config)
            for key in values.DEFAULT_CONFIG.keys():
                if key not in out_conf:
                    out_conf[key] = values.DEFAULT_CONFIG[key]

    except IOError:  # if not found, create a new one
        out_conf = copy(values.DEFAULT_CONFIG)
    except json.decoder.JSONDecodeError:
        out_conf = copy(values.DEFAULT_CONFIG)
    return out_conf


def get_default_settings():
    return values.DEFAULT_CONFIG


def get_config():
    return values.ALL_CONFIG_VALUES


class Controller:
    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        self.config = load_config(values.CONFIG_FILE_NAME)
        self.model = None

        self.view = UiMainWindow(self)
        self.set_config_for_gui()
        self.model = self._make_model()

        self._run_tray()
        if not self.config['tray']:
            self._run_gui()

        self._create_hotkeys()

        if self.config['start_capture']:
            self.model.start_recording()

        self.view.show_user_settings()
        self.view.show()
        sys.exit(app.exec())

    def _create_hotkeys(self):
        # todo create hotkeys for:
        #  - get replay
        #  - get screenshot
        ...

    def _run_tray(self):
        # todo tray loop

        ...

    def _run_gui(self):
        self.view.show()

    def _make_model(self):
        # Get correct video encoder
        try:
            capture.ENCODERS[self.config['codec']]
        except KeyError:
            self.config['codec'] = 'mp4'
        finally:
            encoder = capture.ENCODERS[self.config['codec']]
        return capture.Capture.from_config(self.config, encoder(self.config['fps']))

    def update_config_from_gui(self):
        # todo overwrite file config
        #  get config from gui, save it to file with _save_config(config, file_name)
        #  restart the model - create new model with new config
        #       stop recording
        #       create new model
        #       start new recording (if it was started before)
        self.stop_capture()

        # Get indexed values
        self.config['resolution'] = self.view.resolution_combo_box.currentText()
        self.config['fps'] = self.view.FPS_combo_box.currentText()
        self.config['codec'] = self.view.extension_combo_box.currentText()
        self.config['display'] = self.view.display_combo_box.currentText()

        # Get normal values
        self.config['video_hotkey'] = self.view.video_hotkey.text()
        self.config['screen_hotkey'] = self.view.screen_hotkey.text()
        self.config['save_sound'] = self.view.sounds_button.isChecked()
        self.config['quality'] = self.view.quality_slider.value()
        self.config['duration'] = self.view.duration_horizontal_slider.value()
        self.config['video_path'] = self.view.v_storage_line.text()
        self.config['screen_path'] = self.view.s_storage_line.text()

        # Save config to file
        _save_config(self.config, values.CONFIG_FILE_NAME)

        # Make model with new config and start capture
        self.model = self._make_model()
        self.start_capture()

    def set_config_for_gui(self):
        # todo from config retrieve all necessary info
        #  convert values to strings
        #  calculate indices (indexes)
        #  set everything for the view
        # Set indices
        ...

        # Set values in view
        self.view.video_hotkey.setText(self.config['video_hotkey'])
        self.view.screen_hotkey.setText(self.config['screen_hotkey'])
        self.view.sounds_button.setChecked(self.config['save_sound'])
        self.view.quality_slider.setValue(self.config['quality'])
        self.view.duration_horizontal_slider.setValue(self.config['duration'])
        self.view.v_storage_line.setText(self.config['video_path'])
        self.view.s_storage_line.setText(self.config['screen_path'])

    def get_ram_usage(self):
        # todo calculate ram usage based on config currently used
        return 400

    def start_capture(self):
        if self.model:
            self.model.start_recording()

    def get_replay(self):
        if self.model:
            self.model.export_recording()

    def get_screenshot(self):
        if self.model:
            self.model.export_screenshot()

    def stop_capture(self):
        if self.model:
            self.model.stop_recording()

    def close_app(self):
        self.stop_capture()
        self.view.close_app()
