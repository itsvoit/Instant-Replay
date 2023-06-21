
CONFIG_FILE_NAME = "config.json"
CAPTURE_JPEG = "JPEG"


DEFAULT_START_CAP = False
DEFAULT_RESOLUTION = None
DEFAULT_FPS = 15
DEFAULT_CODEC = "mp4"
DEFAULT_DISPLAY = 1  # Main display
DEFAULT_V_HOTKEY = None
DEFAULT_P_HOTKEY = None
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
                'resolution': ['1920x1080'],
                'fps': [10, 15, 20, 25, 30],
                'codec': ['mp4'],
                'display': [1, 2],
}


DEFAULT_SCREEN_SIZE = (1920, 1080)

TASK_KILL = "KILL"
TASK_TRIM = "TRIM"

