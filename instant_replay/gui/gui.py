import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from instant_replay import values

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

    def __init__(self, verbose=False):
        super().__init__()
        self.verbose = verbose
        self.should_close = False

        self.setWindowIcon(QIcon(values.APP_ICON))
        self.setObjectName(values.APP_NAME)
        self.resize(875, 612)
        self.setMinimumSize(QtCore.QSize(875, 612))
        self.setMaximumSize(QtCore.QSize(875, 612))

        self.central_widget = self.make_central_widget()
        self.full_menu_widget = self.make_menu_widget()
        self.menu_vertical_layout = self.make_menu_layout()
        self.option_v_layout = self.make_vertical_layout("verticalLayout_4", self.full_menu_widget)

        self.option_button = self.make_menu_button("option_button", values.OPTIONS_ICON)
        self.video_button = self.make_menu_button("video_button", values.VIDEO_ICON)
        self.editor_button = self.make_menu_button("editor_button", values.EDITOR_ICON)
        spacerItem = QtWidgets.QSpacerItem(20, 130)
        self.start_button = self.make_menu_button("start_button", values.START_REC_ICON)
        self.capture_button = self.make_menu_button("capture_button", values.CAPTURE_ICON)
        self.screenshot_button = self.make_menu_button("screenshot_button", values.CAPTURE_ICON)
        self.stop_button = self.make_menu_button("stop_button", values.STOP_REC_ICON)
        spacerItem2 = QtWidgets.QSpacerItem(20, 220, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)

        self.menu_vertical_layout.addWidget(self.option_button)
        self.menu_vertical_layout.addWidget(self.video_button)
        self.menu_vertical_layout.addWidget(self.editor_button)
        self.menu_vertical_layout.addItem(spacerItem)
        self.menu_vertical_layout.addWidget(self.start_button)
        self.menu_vertical_layout.addWidget(self.capture_button)
        self.menu_vertical_layout.addWidget(self.screenshot_button)
        self.menu_vertical_layout.addWidget(self.stop_button)
        self.menu_vertical_layout.addItem(spacerItem2)

        self.option_v_layout.addLayout(self.menu_vertical_layout)

        self.option_button.clicked.connect(self.select_option_widget)

        self.exit_button = self.make_menu_button("exit_button", values.EXIT_ICON)

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
        self.v_storage_line.setReadOnly(True)

        self.s_storage_line = self.make_storage_line('s_storage_line', (270, 480))

        self.display_combo_box = self.make_combo_box('display_combo_box', (270, 530))
        self.s_storage_line.setReadOnly(True)

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

        self.save_button = self.make_button("save_button", (590, 570))

        self.duration_horizontal_slider = self.make_horizontal_slider("duration_slider", (270, 380), 10, values.MAX_LEN)

        self.v_dur_display = self.make_lcd_display("v_dur_display", (470, 380), 91, 32)

        self.video_hotkey = self.make_line("video_path", (270, 230))
        self.video_hotkey.keyPressEvent = self.line_press_event

        self.screen_hotkey = self.make_line("screen_path", (270, 280))
        self.screen_hotkey.keyPressEvent = self.line_press_event

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
        textOption = QTextOption()
        textOption.setFlags(textOption.flags() & ~Qt.TextEditable)
        textOption.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        text_line = QtWidgets.QLineEdit(self.option)
        text_line.setGeometry(QtCore.QRect(geometry[0], geometry[1], 182, 32))
        font = QtGui.QFont()
        font.setPointSize(11)
        text_line.setFont(font)
        text_line.setObjectName(name)

        return text_line

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate(values.APP_NAME, values.APP_NAME))
        self.option_button.setText(_translate(values.APP_NAME, "  Option"))
        self.video_button.setText(_translate(values.APP_NAME, "  Replay"))
        self.editor_button.setText(_translate(values.APP_NAME, "  Video editor"))
        self.start_button.setText(_translate(values.APP_NAME, "  Start"))
        self.capture_button.setText(_translate(values.APP_NAME, "  Replay"))
        self.screenshot_button.setText(_translate(values.APP_NAME, "  Screenshot"))
        self.stop_button.setText(_translate(values.APP_NAME, "  Stop"))
        self.exit_button.setText(_translate(values.APP_NAME, "  Exit"))
        self.resolution_label.setText(_translate(values.APP_NAME, "Resolution"))
        self.FPS_label.setText(_translate(values.APP_NAME, "FPS"))
        self.extension_label.setText(_translate(values.APP_NAME, "Replay extension"))
        self.photo_extension_label.setText(_translate(values.APP_NAME, "Screenshot extension"))
        self.v_hotkey.setText(_translate(values.APP_NAME, "Replay Hotkey"))
        self.s_hotkey.setText(_translate(values.APP_NAME, "Screenshot Hotkey"))
        self.quality_label.setText(_translate(values.APP_NAME, "Bitrate/Quality"))
        self.duration_label.setText(_translate(values.APP_NAME, "Replay duration (s)"))
        self.v_storage_label.setText(_translate(values.APP_NAME, "Replay storage path"))
        self.s_storage_label.setText(_translate(values.APP_NAME, "Photo storage path"))
        self.display_label.setText(_translate(values.APP_NAME, "Display"))
        self.v_storage_browse.setText(_translate(values.APP_NAME, "Browse"))
        self.s_storage_browse.setText(_translate(values.APP_NAME, "Browse"))
        self.reset_button.setText(_translate(values.APP_NAME, "Reset"))
        self.save_button.setText(_translate(values.APP_NAME, "Save"))
        self.ram_label.setText(_translate(values.APP_NAME, "RAM requirements (MB)"))

    # ---------------------------------------------------------------------------------
    # Override events

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if not self.should_close:
            event.ignore()
            self.hide()
        elif self.verbose:
            print("[GUI] Close event")

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                event.ignore()
                self.hide()

    def line_press_event(self, event):
        modifiers = {'alt', 'shift', 'ctrl'}
        pressed = set()

        for modifier in modifiers:
            if keyboard.is_pressed(modifier):
                pressed.add(modifier)
        key = keyboard.read_key()
        if key in modifiers or len(pressed) < 1:
            return

        line_text = self.video_hotkey if self.video_hotkey.hasFocus() else self.screen_hotkey

        text = ""
        if key:
            for mod in pressed:
                text += f"<{mod}>+"
        text += key.lower()
        if (self.video_hotkey is line_text and self.screen_hotkey.text() == text) or \
                (self.screen_hotkey is line_text and self.video_hotkey.text() == text):
            return

        line_text.setText(text)
        line_text.clearFocus()

    # ---------------------------------------------------------------------------------
    # Event methods

    def select_option_widget(self):
        self.main_stacked_widget.setCurrentIndex(0)

    @pyqtSlot()
    def browse_v_storage(self):
        folder = QFileDialog.getExistingDirectory(QMainWindow(), "Wybierz folder")
        if folder:
            self.v_storage_line.setText(folder)

    @pyqtSlot()
    def browse_s_storage(self):
        folder = QFileDialog.getExistingDirectory(QMainWindow(), "Wybierz folder")
        if folder:
            self.s_storage_line.setText(folder)
