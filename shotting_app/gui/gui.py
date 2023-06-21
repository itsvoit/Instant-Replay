import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog

widget_back_ground = "background-color: #505F72"
menu_button_style = '''
                    QPushButton{
                        background-color: #455364;
                        text-align: left; 
                        padding-left: 10px; 
                    }

                    QPushButton:hover{
                        background-color: #5F7289;
                        text-align: left; 
                        padding-left: 10px;                        
                    }'''


class UiMainWindow(QMainWindow):

    def __init__(self, controller):
        super().__init__()
        self.should_close = False
        self.setWindowIcon(QIcon("./icons/application_icon.png"))
        self.setObjectName("Screen Recorder")
        self.resize(875, 612)
        self.setMinimumSize(QtCore.QSize(875, 612))
        self.setMaximumSize(QtCore.QSize(875, 612))

        self.controller = controller
        self.central_widget = self.make_central_widget()
        self.full_menu_widget = self.make_menu_widget()
        self.menu_vertical_layout = self.make_menu_layout()
        self.option_v_layout = self.make_vertical_layout("verticalLayout_4", self.full_menu_widget)

        self.option_button = self.make_menu_button("option_button", "./icons/options_icon.png")
        self.video_button = self.make_menu_button("video_button", "./icons/video_icon.png")
        self.editor_button = self.make_menu_button("editor_button", "./icons/editor_icon.png")
        spacerItem = QtWidgets.QSpacerItem(20, 150)
        self.start_button = self.make_menu_button("start_button", "./icons/start_recording_icon.png")
        # todo rename icon to something humanly readable
        self.capture_button = self.make_menu_button("capture_button",
                                                    os.path.join(".", "icons/frame-expand_icon-icons.com_48296.png"))
        self.stop_button = self.make_menu_button("stop_button", "./icons/stop_recording_icon.png")
        spacerItem2 = QtWidgets.QSpacerItem(20, 220, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)

        self.menu_vertical_layout.addWidget(self.option_button)
        self.menu_vertical_layout.addWidget(self.video_button)
        self.menu_vertical_layout.addWidget(self.editor_button)
        self.menu_vertical_layout.addItem(spacerItem)
        self.menu_vertical_layout.addWidget(self.start_button)
        self.menu_vertical_layout.addWidget(self.capture_button)
        self.menu_vertical_layout.addWidget(self.stop_button)
        self.menu_vertical_layout.addItem(spacerItem2)

        self.option_v_layout.addLayout(self.menu_vertical_layout)

        self.option_button.clicked.connect(self.select_option_widget)
        self.start_button.clicked.connect(self.start_capturing)
        self.capture_button.clicked.connect(self.capture_video)
        self.stop_button.clicked.connect(self.stop_capturing)

        self.exit_button = self.make_menu_button("exit_button", "./icons/powercircleandlinesymbol_118369.png")

        self.exit_button.clicked.connect(self.close_button_action)
        self.option_v_layout.addWidget(self.exit_button)

        self.main_widget = self.make_main_widget()
        self.main_stacked_widget = self.make_stacked_widget()

        self.option = QtWidgets.QWidget()
        self.option.setObjectName("option")

        self.resolution_combo_box = self.make_combo_box("resolution_combo_box", (270, 30))
        self.FPS_combo_box = self.make_combo_box('FPS_combo_box', (270, 80))
        self.extension_combo_box = self.make_combo_box('extension_combo_box', (270, 130))
        self.photo_extension_combo_box = self.make_combo_box('extension_combo_box', (270, 180))

        self.quality_slider = self.make_slider("quality_slider", (270, 330), 1, 95)

        self.v_storage_line = self.make_storage_line("v_storage_line", (270, 430))
        self.v_storage_line.setDisabled(True)

        self.s_storage_line = self.make_storage_line('s_storage_line', (270, 480))

        self.display_combo_box = self.make_combo_box('display_combo_box', (270, 530))
        self.s_storage_line.setDisabled(True)

        self.layout_widget_labels = self.make_layout_widget_for_label()

        self.menu_label_vertica_layout = self.make_vertical_layout("menu_label_vertica_layout",
                                                                   self.layout_widget_labels)

        self.resolution_label = self.make_label("resolution_label", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.resolution_label)

        self.FPS_label = self.make_label("FPS_label", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.FPS_label)

        self.extension_label = self.make_label("extension_label", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.extension_label)

        self.photo_extension_label = self.make_label("photo_extension_label", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.photo_extension_label)

        self.v_hotkey = self.make_label("v_hotkey", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.v_hotkey)

        self.s_hotkey = self.make_label("s_hotkey", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.s_hotkey)

        self.quality_label = self.make_label("quality_label", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.quality_label)

        self.duration_label = self.make_label("duration_label", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.duration_label)

        self.v_storage_label = self.make_label("v_storage_label", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.v_storage_label)

        self.s_storage_label = self.make_label("s_storage_label", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.s_storage_label)

        self.display_label = self.make_label("display_label", self.layout_widget_labels)
        self.menu_label_vertica_layout.addWidget(self.display_label)

        self.v_storage_browse = self.make_button("v_storage_button", (470, 430))
        self.v_storage_browse.clicked.connect(self.browse_v_storage)

        self.s_storage_browse = self.make_button("s_storage_button", (470, 480))
        self.s_storage_browse.clicked.connect(self.browse_s_storage)

        self.duration_display = self.make_lcd_display("duration_display", (470, 330), 91, 32)

        self.reset_button = self.make_button("reset_button", (470, 570))
        self.reset_button.clicked.connect(self.restart_settings)

        self.save_button = self.make_button("save_button", (590, 570))
        self.save_button.clicked.connect(self.save_settings)

        self.duration_horizontal_slider = self.make_horizontal_slider("duration_slider", (270, 380), 10, 120)

        self.v_dur_display = self.make_lcd_display("v_dur_display", (470, 380), 91, 32)

        self.video_hotkey = self.make_line("video_path", (270, 230))

        self.screen_hotkey = self.make_line("screen_path", (270, 280))

        self.ram_label = self.make_label("ram_req_label", self.option)
        self.ram_label.setGeometry(QtCore.QRect(480, 60, 201, 41))

        self.ram_display = self.make_lcd_display("ram_display", (480, 100), 210, 42)

        self.main_stacked_widget.addWidget(self.option)

        self.video = QtWidgets.QWidget()
        self.video.setObjectName("video")

        self.main_stacked_widget.addWidget(self.video)

        self.video_editor = QtWidgets.QWidget()
        self.video_editor.setObjectName("video_editor")

        self.main_stacked_widget.addWidget(self.video_editor)
        self.setCentralWidget(self.central_widget)

        self.retranslateUi()

        self.main_stacked_widget.setCurrentIndex(0)

        self.quality_slider.valueChanged['int'].connect(self.duration_display.display)

        self.duration_horizontal_slider.valueChanged['int'].connect(self.v_dur_display.display)
        QtCore.QMetaObject.connectSlotsByName(self)

    def make_central_widget(self):
        central_widget = QtWidgets.QWidget(self)
        central_widget.setObjectName("central_widget")

        return central_widget

    def make_menu_widget(self):
        full_menu_widget = QtWidgets.QWidget(self.central_widget)
        full_menu_widget.setGeometry(QtCore.QRect(0, 0, 151, 611))
        full_menu_widget.setAutoFillBackground(False)
        full_menu_widget.setStyleSheet(widget_back_ground)
        full_menu_widget.setObjectName("full_menu_widget")

        return full_menu_widget

    def make_vertical_layout(self, name, widget):
        v_layout = QtWidgets.QVBoxLayout(widget)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)
        v_layout.setObjectName(name)

        return v_layout

    def make_menu_layout(self):
        menu_vertica_layout = QtWidgets.QVBoxLayout()
        menu_vertica_layout.setObjectName("menu_vertica_layout")

        return menu_vertica_layout

    def make_menu_button(self, name, icon_path):
        button = QtWidgets.QPushButton(self.full_menu_widget)
        button.setStyleSheet(menu_button_style)
        font = QtGui.QFont()
        font.setPointSize(11)
        button.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(25, 30))
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setObjectName(name)

        return button

    def make_main_widget(self):
        main_widget = QtWidgets.QWidget(self.central_widget)
        main_widget.setGeometry(QtCore.QRect(151, 0, 720, 611))
        main_widget.setMinimumSize(QtCore.QSize(720, 611))
        main_widget.setMaximumSize(QtCore.QSize(720, 611))
        main_widget.setObjectName("main_widget")

        return main_widget

    def make_stacked_widget(self):
        main_stacked_widget = QtWidgets.QStackedWidget(self.central_widget)
        main_stacked_widget.setGeometry(QtCore.QRect(160, 0, 713, 611))
        main_stacked_widget.setMinimumSize(QtCore.QSize(713, 611))
        main_stacked_widget.setMaximumSize(QtCore.QSize(713, 611))
        main_stacked_widget.setBaseSize(QtCore.QSize(0, 0))
        main_stacked_widget.setStyleSheet("\\")
        main_stacked_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        main_stacked_widget.setObjectName("main_stacked_widget")

        return main_stacked_widget

    def make_combo_box(self, name, geometry):
        combo_box = QtWidgets.QComboBox(self.option)
        combo_box.setGeometry(QtCore.QRect(geometry[0], geometry[1], 181, 32))
        font = QtGui.QFont()
        font.setPointSize(11)
        combo_box.setFont(font)
        combo_box.setObjectName(name)

        return combo_box

    def make_storage_line(self, name, geometry):
        storage_line = QtWidgets.QLineEdit(self.option)
        storage_line.setGeometry(QtCore.QRect(geometry[0], geometry[1], 181, 32))
        font = QtGui.QFont()
        font.setPointSize(11)
        storage_line.setFont(font)
        storage_line.setObjectName(name)

        return storage_line

    def make_slider(self, name, geometry, min_, max_):
        slider = QtWidgets.QSlider(self.option)
        slider.setGeometry(QtCore.QRect(geometry[0], geometry[1], 181, 32))
        font = QtGui.QFont()
        font.setPointSize(11)
        slider.setFont(font)
        slider.setMinimum(min_)
        slider.setMaximum(max_)
        slider.setOrientation(QtCore.Qt.Horizontal)
        slider.setObjectName(name)

        return slider

    def make_check_button(self, name, geometry):
        button = QtWidgets.QCheckBox(self.option)
        button.setGeometry(QtCore.QRect(geometry[0], geometry[1], 31, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        button.setFont(font)
        button.setText("")
        button.setObjectName(name)

        return button

    def make_layout_widget_for_label(self):
        layout_widget_labels = QtWidgets.QWidget(self.option)
        layout_widget_labels.setGeometry(QtCore.QRect(60, 20, 165, 551))
        layout_widget_labels.setObjectName("layout_widget_labels")

        return layout_widget_labels

    def make_label(self, name, widget):
        label = QtWidgets.QLabel(widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        label.setFont(font)
        label.setObjectName(name)

        return label

    def make_button(self, name, geometry):
        button_browse = QtWidgets.QPushButton(self.option)
        button_browse.setGeometry(QtCore.QRect(geometry[0], geometry[1], 91, 32))
        button_browse.setCheckable(True)
        button_browse.setAutoExclusive(True)
        button_browse.setObjectName(name)

        return button_browse

    def make_lcd_display(self, name, geometry, height, width):
        display = QtWidgets.QLCDNumber(self.option)
        display.setGeometry(QtCore.QRect(geometry[0], geometry[1], height, width))
        display.setObjectName(name)

        return display

    def make_horizontal_slider(self, name, geometry, min_, max_):
        horizontal_slider = QtWidgets.QSlider(self.option)
        horizontal_slider.setGeometry(QtCore.QRect(geometry[0], geometry[1], 181, 32))
        font = QtGui.QFont()
        font.setPointSize(11)
        horizontal_slider.setFont(font)
        horizontal_slider.setMinimum(min_)
        horizontal_slider.setMaximum(max_)
        horizontal_slider.setProperty("value", 10)
        horizontal_slider.setOrientation(QtCore.Qt.Horizontal)
        horizontal_slider.setObjectName(name)

        return horizontal_slider

    def make_line(self, name, geometry):
        path = QtWidgets.QLineEdit(self.option)
        path.setGeometry(QtCore.QRect(geometry[0], geometry[1], 182, 32))
        font = QtGui.QFont()
        font.setPointSize(11)
        path.setFont(font)
        path.setObjectName(name)

        return path

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Screen Recorder", "Screen Recorder"))
        self.option_button.setText(_translate("Screen Recorder", "  Option"))
        self.video_button.setText(_translate("Screen Recorder", "  Video"))
        self.editor_button.setText(_translate("Screen Recorder", "  Video editor"))
        self.start_button.setText(_translate("Screen Recorder", "  Start"))
        self.capture_button.setText(_translate("Screen Recorder", "  Capture"))
        self.stop_button.setText(_translate("Screen Recorder", "  Stop"))
        self.exit_button.setText(_translate("Screen Recorder", "  Exit"))
        self.resolution_label.setText(_translate("Screen Recorder", "Resolution"))
        self.FPS_label.setText(_translate("Screen Recorder", "FPS"))
        self.extension_label.setText(_translate("Screen Recorder", "Video extension"))
        self.photo_extension_label.setText(_translate("Screen Recorder", "Photo extension"))
        self.v_hotkey.setText(_translate("Screen Recorder", "Video Hotkey"))
        self.s_hotkey.setText(_translate("Screen Recorder", "Screen Hotkey"))
        self.quality_label.setText(_translate("Screen Recorder", "Bitrate/Quality"))
        self.duration_label.setText(_translate("Screen Recorder", "Video duration (s)"))
        self.v_storage_label.setText(_translate("Screen Recorder", "Video storage path"))
        self.s_storage_label.setText(_translate("Screen Recorder", "Screen storage path"))
        self.display_label.setText(_translate("Screen Recorder", "Display"))
        self.v_storage_browse.setText(_translate("Screen Recorder", "Browse"))
        self.s_storage_browse.setText(_translate("Screen Recorder", "Browse"))
        self.reset_button.setText(_translate("Screen Recorder", "Reset"))
        self.save_button.setText(_translate("Screen Recorder", "Save"))
        self.ram_label.setText(_translate("Screen Recorder", "RAM requirements (MB)"))

    # ---------------------------------------------------------------------------------
    # Override events

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if not self.should_close:
            event.ignore()
            self.hide()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                event.ignore()
                self.hide()

    # ---------------------------------------------------------------------------------
    # Event methods

    def start_capturing(self):
        self.controller.start_capture()

    def stop_capturing(self):
        self.controller.stop_capture()

    def capture_video(self):
        self.controller.export_replay()

    def close_button_action(self):
        self.hide()

    def select_option_widget(self):
        self.main_stacked_widget.setCurrentIndex(0)

    def show_settings(self, settings):
        self.resolution_combo_box.clear()
        self.FPS_combo_box.clear()
        self.extension_combo_box.clear()
        self.photo_extension_combo_box.clear()
        self.display_combo_box.clear()

        self.resolution_combo_box.addItems(settings['resolution'])
        self.FPS_combo_box.addItems(settings['fps'])
        self.extension_combo_box.addItems(settings['codec'])
        self.photo_extension_combo_box.addItems(settings['p_ext'])
        self.display_combo_box.addItems(settings['display'])

        self.resolution_combo_box.setCurrentIndex(0)
        self.FPS_combo_box.setCurrentIndex(0)
        self.extension_combo_box.setCurrentIndex(0)
        self.photo_extension_combo_box.setCurrentIndex(0)
        self.display_combo_box.setCurrentIndex(0)

        self.ram_display.display(self.controller.get_ram_usage())

    def restart_settings(self):
        self.controller.set_default_config()

    def save_settings(self):
        self.controller.update_config_from_gui()

    def browse_v_storage(self):
        folder = QFileDialog.getExistingDirectory(QMainWindow(), "Wybierz folder")
        if folder:
            self.v_storage_line.setText(folder)

    def browse_s_storage(self):
        folder = QFileDialog.getExistingDirectory(QMainWindow(), "Wybierz folder")
        if folder:
            self.s_storage_line.setText(folder)
