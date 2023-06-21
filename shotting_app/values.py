import os

APP_NAME = "Instant Replay"
ROOT_DIR, _ = os.path.split(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE_NAME = "config.json"
CAPTURE_JPEG = "JPEG"
CAPTURE_PNG = "PNG"


DEFAULT_START_CAP = False
DEFAULT_RESOLUTION = '1920x1080'
DEFAULT_FPS = 15
DEFAULT_CODEC = "mp4"
DEFAULT_P_EXT = "png"
DEFAULT_DISPLAY = 1  # Main display
DEFAULT_V_HOTKEY = "<ctrl>+<shift>+p"
DEFAULT_P_HOTKEY = "<ctrl>+<shift>+o"
DEFAULT_W_SOUND = False  # Not implemented
DEFAULT_QUALITY = 80  # Range 0-95
DEFAULT_DURATION = 20  # Based on RAM
DEFAULT_V_PATH = "videos"
DEFAULT_P_PATH = "photos"
DEFAULT_RAM_USAGE = 500 * 1024 * 1024  # 500 * MB
DEFAULT_RUN_TRAY = True

DEFAULT_CONFIG = {
                  'start_capture': DEFAULT_START_CAP,
                  'resolution': DEFAULT_RESOLUTION,
                  'fps': DEFAULT_FPS,
                  'codec': DEFAULT_CODEC,
                  'p_ext': DEFAULT_P_EXT,
                  'display': DEFAULT_DISPLAY,
                  'video_hotkey': DEFAULT_V_HOTKEY,
                  'screen_hotkey': DEFAULT_P_HOTKEY,
                  'save_sound': DEFAULT_W_SOUND,
                  'quality': DEFAULT_QUALITY,
                  'duration': DEFAULT_DURATION,
                  'video_path': DEFAULT_V_PATH,
                  'screen_path': DEFAULT_P_PATH,
                  'ram_usage': DEFAULT_RAM_USAGE,
                  'tray': True
}


ALL_CONFIG_VALUES = {
                'resolution': ['3840x2160', '2560x1440', '1920x1080', '1280x720'],
                'fps': [10, 15, 20, 25, 30],
                'codec': ['mp4'],
                'p_ext': ["png", "jpeg"],
                'display': [1, 2],  # todo recognise how many displays on load
}


DEFAULT_SCREEN_SIZE = (1920, 1080)

TASK_KILL = "KILL"
TASK_TRIM = "TRIM"
TASK_SHOT = "SHOT"

APP_ICON = os.path.join(ROOT_DIR, "icons/application_icon.png")
CAPTURE_ICON = os.path.join(ROOT_DIR, "icons/capture_icon.png")
EDITOR_ICON = os.path.join(ROOT_DIR, "icons/editor_icon.png")
EXIT_ICON = os.path.join(ROOT_DIR, "icons/exit_icon.png")
OPTIONS_ICON = os.path.join(ROOT_DIR, "icons/options_icon.png")
START_REC_ICON = os.path.join(ROOT_DIR, "icons/start_recording_icon.png")
STOP_REC_ICON = os.path.join(ROOT_DIR, "icons/stop_recording_icon.png")
VIDEO_ICON = os.path.join(ROOT_DIR, "icons/video_icon.png")
