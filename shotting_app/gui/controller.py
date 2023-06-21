import json
import os
import sys
from copy import copy

import mss
import qdarkstyle
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication
from infi.systray import SysTrayIcon
from pynput.keyboard import GlobalHotKeys

from shotting_app import values
from shotting_app.capture.capture import Capture, VID_ENCODERS, P_ENCODERS, FileSaver


def save_config(config, file_name):
    with open(file_name, 'w') as file:
        json.dump(config, file, indent=4)


def get_default_config():
    return values.DEFAULT_CONFIG


def get_config_options():
    return values.ALL_CONFIG_VALUES


def n_of_displays():
    with mss.mss() as sct:
        displays = len(sct.monitors)
    return displays - 1


class Controller(QObject):
    def __init__(self, view, verbose=False):
        super(Controller, self).__init__()
        self.verbose = verbose
        self.closed = False

        self.view = view
        self.create_tray()
        self.n_of_displays = n_of_displays()
        self.config = self._load_config(values.CONFIG_FILE_NAME)
        self._set_config_options()
        self._show_config()


        # self.view.option_button.clicked.connect(self.select_option_widget)
        self.view.start_button.clicked.connect(self.start_capture)
        self.view.capture_button.clicked.connect(self.export_replay)
        self.view.screenshot_button.clicked.connect(self.export_screenshot)
        self.view.stop_button.clicked.connect(self.stop_capture)
        self.view.exit_button.clicked.connect(self.close_app)
        self.view.reset_button.clicked.connect(self.show_default_config)
        self.view.save_button.clicked.connect(self.update_config_from_gui)
        # self.view.video_hotkey.

        self.model: Capture = None
        self.hotkeys: GlobalHotKeys = None

        self._setup_services()

        if not self.config['tray']:
            self._show_gui()

        if self.config['start_capture']:
            self.model.start_recording()

        self.view.show()

    def _make_hotkeys(self) -> GlobalHotKeys:
        """
        GlobalHotKeys object will use current hotkeys
        :return: GlobalHotKeys object ready to be started
        """

        def export_replay():
            self.export_replay()

        def export_screenshot():
            self.export_screenshot()

        global_hotkeys = GlobalHotKeys(
            {self.config["video_hotkey"]: export_replay,
             self.config["screen_hotkey"]: export_screenshot})
        global_hotkeys.daemon = True
        return global_hotkeys

    def create_tray(self) -> SysTrayIcon:
        """
        :return: SysTrayIcon object ready to be started
        """

        def show_gui(_):
            self._show_gui()

        def start_capture(_):
            self.start_capture()

        def export_replay(_):
            self.export_replay()

        def stop_capture(_):
            self.stop_capture()

        def close_app(_):
            if not self.closed:
                self.close_app()

        menu_options = (("Options", values.OPTIONS_ICON, show_gui),
                        ("Start recording", values.VIDEO_ICON, start_capture),
                        ("Get recording", values.CAPTURE_ICON, export_replay),
                        ("Stop recording", values.STOP_REC_ICON, stop_capture))

        return SysTrayIcon(values.APP_ICON, values.APP_NAME, menu_options, on_quit=close_app)

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
            VID_ENCODERS[self.config['codec']]
        except KeyError:
            self.config['codec'] = 'mp4'
        finally:
            vid_encoder = VID_ENCODERS[self.config['codec']]

        try:
            P_ENCODERS[self.config['p_ext']]
        except KeyError:
            self.config['p_ext'] = 'png'
        finally:
            p_encoder = P_ENCODERS[self.config['p_ext']]

        vid_path = self.config['video_path']
        vid_pref = "video"
        vid_ext = self.config['codec']
        p_path = self.config['screen_path']
        p_pref = "screenshot"
        p_ext = self.config['p_ext']
        return Capture.from_config(
            self.config,
            vid_encoder(self.config['fps'], FileSaver(vid_path, vid_pref, vid_ext)),
            p_encoder(FileSaver(p_path, p_pref, p_ext)),
            verbose=self.verbose)

    def _load_config(self, file_name):
        try:
            with open(file_name, "r") as config:
                out_conf = json.load(config)
                for key in values.DEFAULT_CONFIG.keys():
                    if key not in out_conf or out_conf[key] is None:
                        out_conf[key] = values.DEFAULT_CONFIG[key]
                    if out_conf['display'] > self.n_of_displays:
                        out_conf['display'] = 1

        except IOError:  # if not found, create a new one
            out_conf = copy(values.DEFAULT_CONFIG)
        except json.decoder.JSONDecodeError:
            out_conf = copy(values.DEFAULT_CONFIG)
        return out_conf

    def _set_config_options(self):
        """
        Get all possible options and display them in view
        """
        options = get_config_options()
        self.view.resolution_combo_box.addItems([str(x) for x in options['resolution']])
        self.view.FPS_combo_box.addItems([str(x) for x in options['fps']])
        self.view.extension_combo_box.addItems([str(x) for x in options['codec']])
        self.view.photo_extension_combo_box.addItems([str(x) for x in options['p_ext']])
        self.view.display_combo_box.addItems([f"Display {str(x)}" for x in range(1, self.n_of_displays+1)])

    def _setup_services(self):
        self.model = self._make_model()

        self.hotkeys = self._make_hotkeys()
        self.hotkeys.start()

    def _show_config(self, config=None):
        """
        Display values from configuration into view. If None, use configuration stored in class
        :param config: configuration to view
        """
        if config is None:
            config = self.config
        all_conf = get_config_options()

        # Set indices
        resolution_index = all_conf['resolution'].index(config['resolution'])
        fps_index = all_conf['fps'].index(config['fps'])
        codec_index = all_conf['codec'].index(config['codec'])
        p_ext_index = all_conf['p_ext'].index(config['p_ext'])
        display_index = config['display']

        self.view.resolution_combo_box.setCurrentIndex(resolution_index)
        self.view.FPS_combo_box.setCurrentIndex(fps_index)
        self.view.extension_combo_box.setCurrentIndex(codec_index)
        self.view.photo_extension_combo_box.setCurrentIndex(p_ext_index)
        self.view.display_combo_box.setCurrentIndex(display_index - 1)

        # Set values in view
        self.view.video_hotkey.setText(config['video_hotkey'])
        self.view.screen_hotkey.setText(config['screen_hotkey'])
        self.view.quality_slider.setValue(config['quality'])
        self.view.duration_horizontal_slider.setValue(config['duration'])
        self.view.v_storage_line.setText(config['video_path'])
        self.view.s_storage_line.setText(config['screen_path'])

        self.view.ram_display.display(self._get_ram_usage())

    def _get_ram_usage(self):
        """
        Based on settings chosen calculate the RAM usage
        """
        # todo calculate ram usage based on config currently used
        return 400

    def _stop_services(self):
        self.stop_capture()
        self.hotkeys.stop()

    @pyqtSlot()
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
        self.config['p_ext'] = self.view.photo_extension_combo_box.currentText()
        self.config['display'] = self.view.display_combo_box.currentIndex() + 1

        # Get normal values
        self.config['video_hotkey'] = self.view.video_hotkey.text()
        self.config['screen_hotkey'] = self.view.screen_hotkey.text()
        self.config['quality'] = int(self.view.quality_slider.value())
        self.config['duration'] = int(self.view.duration_horizontal_slider.value())
        self.config['video_path'] = self.view.v_storage_line.text()
        self.config['screen_path'] = self.view.s_storage_line.text()

        # Save config to file
        save_config(self.config, values.CONFIG_FILE_NAME)

        # Restart all services with the new configuration
        self._setup_services()
        self._show_config()

        if was_recording:
            self.start_capture()

    @pyqtSlot()
    def show_default_config(self):
        """
        Display default configuration in view
        """
        self._show_config(get_default_config())

    @pyqtSlot()
    def start_capture(self):
        if self.model:
            self.model.start_recording()

    @pyqtSlot()
    def export_replay(self):
        if self.verbose:
            print("[Controller] Replay")
        if self.model:
            self.model.export_recording()

    @pyqtSlot()
    def export_screenshot(self):
        if self.verbose:
            print("[Controller] Screenshot")
        if self.model:
            self.model.export_screenshot()

    @pyqtSlot()
    def stop_capture(self):
        if self.model:
            self.model.stop_recording()

    @pyqtSlot()
    def close_app(self):
        """
        Stop all processes and close the app
        """
        if self.verbose:
            print("[Controller] Closing the app...")
        self._stop_services()
        self.view.should_close = True
        self.view.close()
        self.closed = True
