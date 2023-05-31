import logging

import shotting_app.values as values
import shotting_app.gui.controller as controller
import shotting_app.gui.settings as setting
import shotting_app.capture as capture
import shotting_app.video_encoders as video_encoders


def _init_logging():
    ...


def _instances_active() -> bool:
    ...


def _get_config(file_name):
    # if not found, create a new one

    return None


def _create_guis():
    ...


def _run_tray():
    ...


def _run_gui():
    ...


def _start_capture():
    ...


def _create_hotkeys():
    ...


def _launch_app():
    app_config = _get_config(values.CONFIG_FILE_NAME)
    _create_guis()

    if app_config.tray:
        _run_tray()
    else:
        _run_gui()

    if app_config.start_capture:
        _start_capture()

    _create_hotkeys()


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
    _init_logging()
    if _instances_active():
        # log "other instance running and exit
        pass
    _launch_app()

