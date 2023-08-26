import logging
import os
import sys

import nk3.qtlogging
from nk3 import application
from nk3.crashHandler import CrashHandler


if __name__ == '__main__':
    os.putenv("QML_DISABLE_DISK_CACHE", "1")
    os.putenv("QSG_RENDER_LOOP", "basic")
    nk3.qtlogging.setup()
    logging.info("Creating application")
    CrashHandler.register()
    app = application.Application()
    logging.info("Starting application")
    app.start()
