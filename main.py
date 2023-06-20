import json
import sys
import time
from copy import copy

import shotting_app.values as values
from shotting_app.gui.controller import Controller
import shotting_app.capture as capture


def _init_logging():
    ...


def _instances_active() -> bool:
    return False


def _get_config(file_name):
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


def _save_config(config, file_name):
    with open(file_name, 'w') as file:
        json.dump(config, file, indent=4)


def _create_guis():
    ...


def _run_tray():
    ...


def _run_gui():
    controller = Controller()


def _create_hotkeys(app_config):
    ...


def conf_test(cap):
    cap.verbose = True
    cap.start_recording()
    time.sleep(15)
    cap.get_recording()
    time.sleep(5)
    cap.get_recording()
    time.sleep(20)
    cap.stop_recording()


def _launch_app():
    app_config = _get_config(values.CONFIG_FILE_NAME)
    try:
        capture.ENCODERS[app_config['codec']]
    except KeyError:
        app_config['codec'] = 'mp4'
    finally:
        encoder = capture.ENCODERS[app_config['codec']]

    _save_config(app_config, values.CONFIG_FILE_NAME)
    cap = capture.Capture.from_config(app_config, encoder(app_config['fps']))

    _create_guis()

    if app_config['tray']:
        _run_tray()
    else:
        _run_gui()

    _create_hotkeys(app_config)

    if app_config['start_capture']:
        cap.start_recording()


# Main app script
if __name__ == "__main__":
    """
    create logging object
    check if there are no other instances of this app
    launch the app
        -  get initial config
        -  create all necessary guis
                o  connect them with a controller
                o  display all information needed
        -  run tray OR run gui app
        -  create the Capture
        -  start the Capture OR wait for user to start it
        -  listen for the shortcuts
    """
    # _init_logging()
    # if _instances_active():
    #     # log "other instance running and exit
    #     sys.exit(1)
    # _launch_app()
    _run_gui()
