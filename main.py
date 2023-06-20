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


# Main app script
if __name__ == "__main__":
    """
    create logging object
    check if there are no other instances of this app
    create the Capture
    launch the controller(capture)
    run tray AND optionally run gui app
    listen for the shortcuts
    """
    _init_logging()
    if _instances_active():
        # log "other instance running and exit
        sys.exit(1)

    controller = Controller()

