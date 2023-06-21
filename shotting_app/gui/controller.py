import json
import os
import sys
from copy import copy

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from infi.systray import SysTrayIcon
from pynput import keyboard

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
                if key not in out_conf or out_conf[key] is None:
                    out_conf[key] = values.DEFAULT_CONFIG[key]

    except IOError:  # if not found, create a new one
        out_conf = copy(values.DEFAULT_CONFIG)
    except json.decoder.JSONDecodeError:
        out_conf = copy(values.DEFAULT_CONFIG)
    return out_conf


def get_default_config():
    return values.DEFAULT_CONFIG


def get_config_options():
    return values.ALL_CONFIG_VALUES


class Controller:
    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        self.config = load_config(values.CONFIG_FILE_NAME)

        self.view = UiMainWindow(self)
        self._set_config_options()
        self._show_config()

        self.model = None
        self.tray = None
        self.hotkeys = None

        self._setup_services()

        if not self.config['tray']:
            self._show_gui()

        if self.config['start_capture']:
            self.model.start_recording()

        self.view.show()
        sys.exit(app.exec())

    def _make_hotkeys(self) -> keyboard.GlobalHotKeys:
        """
        GlobalHotKeys object will use current hotkeys
        :return: keyboard.GlobalHotKeys object ready to be started
        """

        def export_replay():
            self.export_replay()

        def export_screenshot():
            self.export_screenshot()

        global_hotkeys = keyboard.GlobalHotKeys(
            {self.config["video_hotkey"]: export_replay,
             self.config["screen_hotkey"]: export_screenshot})
        global_hotkeys.daemon = True
        return global_hotkeys

    def _make_tray(self) -> SysTrayIcon:
        """
        :return: SysTrayIcon object ready to be started
        """

        def show_gui(tray):
            self._show_gui()

        def start_capture(tray):
            self.start_capture()

        def export_replay(tray):
            self.export_replay()

        def stop_capture(tray):
            self.stop_capture()

        def close_app(tray):
            self.close_app()

        menu_options = (("Options", None, show_gui),
                        ("Start recording", None, start_capture),
                        ("Get recording", None, export_replay),
                        ("Stop recording", None, stop_capture))

        return SysTrayIcon(os.path.join(".", "icons", "application_icon.png"),
                           "Application icon", menu_options, on_quit=close_app)

    def _show_gui(self):
        """
        Restore window view and put it in front
        """
        self.view.show()
        self.view.setWindowState(self.view.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.view.activateWindow()

    def _make_model(self):
        """
        Get model with a correct video encoder (according to the extension used)
        """
        try:
            capture.VID_ENCODERS[self.config['codec']]
        except KeyError:
            self.config['codec'] = 'mp4'
        finally:
            vid_encoder = capture.VID_ENCODERS[self.config['codec']]

        try:
            capture.P_ENCODERS[self.config['p_ext']]
        except KeyError:
            self.config['p_ext'] = 'png'
        finally:
            p_encoder = capture.P_ENCODERS[self.config['p_ext']]

        vid_path = self.config['video_path']
        vid_pref = "video"
        vid_ext = self.config['codec']
        p_path = self.config['screen_path']
        p_pref = "screenshot"
        p_ext = self.config['p_ext']
        return capture.Capture.from_config(
            self.config,
            vid_encoder(self.config['fps'], capture.FileSaver(vid_path, vid_pref, vid_ext)),
            p_encoder(capture.FileSaver(p_path, p_pref, p_ext)),
            verbose=True)


    def _set_config_options(self):
        """
        Get all possible options and display them in view
        """
        options = get_config_options()
        self.view.resolution_combo_box.addItems([str(x) for x in options['resolution']])
        self.view.FPS_combo_box.addItems([str(x) for x in options['fps']])
        self.view.extension_combo_box.addItems([str(x) for x in options['codec']])
        self.view.display_combo_box.addItems([str(x) for x in options['display']])

    def _setup_services(self):
        self.model = self._make_model()

        if self.tray is None:
            self.tray = self._make_tray()
            self.tray.start()

        self.hotkeys = self._make_hotkeys()
        self.hotkeys.start()

    def update_config_from_gui(self):
        """
        Save configuration present in view into a file.
        Restart all services with new configuration.
        If recording was running - resume it with the new settings
        """
        was_recording = self.model.is_recording
        self._stop_services()

        # Get indexed values
        self.config['resolution'] = self.view.resolution_combo_box.currentText()
        self.config['fps'] = int(self.view.FPS_combo_box.currentText())
        self.config['codec'] = self.view.extension_combo_box.currentText()
        self.config['display'] = self.view.display_combo_box.currentIndex() + 1

        # Get normal values
        self.config['video_hotkey'] = self.view.video_hotkey.text()
        self.config['screen_hotkey'] = self.view.screen_hotkey.text()
        self.config['save_sound'] = self.view.sounds_button.isChecked()
        self.config['quality'] = int(self.view.quality_slider.value())
        self.config['duration'] = int(self.view.duration_horizontal_slider.value())
        self.config['video_path'] = self.view.v_storage_line.text()
        self.config['screen_path'] = self.view.s_storage_line.text()

        # Save config to file
        _save_config(self.config, values.CONFIG_FILE_NAME)

        # Restart all services with the new configuration
        self._setup_services()
        self._show_config()

        if was_recording:
            self.start_capture()

    def _show_config(self, config=None):
        """
        Display values from configuration into view. If None, use configuration stored in class
        :param config: configuration to view
        """
        if config is None:
            config = self.config
        d_conf = get_config_options()

        # Set indices
        resolution_index = d_conf['resolution'].index(config['resolution'])
        fps_index = d_conf['fps'].index(config['fps'])
        codec_index = d_conf['codec'].index(config['codec'])
        display_index = d_conf['display'].index(config['display'])
        self.view.resolution_combo_box.setCurrentIndex(resolution_index)
        self.view.FPS_combo_box.setCurrentIndex(fps_index)
        self.view.extension_combo_box.setCurrentIndex(codec_index)
        self.view.display_combo_box.setCurrentIndex(display_index)

        # Set values in view
        self.view.video_hotkey.setText(config['video_hotkey'])
        self.view.screen_hotkey.setText(config['screen_hotkey'])
        self.view.sounds_button.setChecked(config['save_sound'])
        self.view.quality_slider.setValue(config['quality'])
        self.view.duration_horizontal_slider.setValue(config['duration'])
        self.view.v_storage_line.setText(config['video_path'])
        self.view.s_storage_line.setText(config['screen_path'])

    def set_default_config(self):
        """
        Display default configuration in view
        """
        self._show_config(get_default_config())

    def get_ram_usage(self):
        """
        Based on settings chosen calculate the RAM usage
        """
        # todo calculate ram usage based on config currently used
        return 400

    def start_capture(self):
        if self.model:
            self.model.start_recording()

    def export_replay(self):
        print("Replay")
        if self.model:
            self.model.export_recording()

    def export_screenshot(self):
        print("Screenshot")
        if self.model:
            self.model.export_screenshot()

    def stop_capture(self):
        if self.model:
            self.model.stop_recording()

    def _stop_services(self):
        self.stop_capture()
        self.hotkeys.stop()

    def close_app(self):
        """
        Stop all processes and close the app
        """
        self._stop_services()
        self.view.should_close = True
        self.view.close()
