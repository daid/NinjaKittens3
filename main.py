import logging
import os
import sys

import nk3.logging
from nk3 import application
from nk3.crashHandler import CrashHandler


if __name__ == '__main__':
    os.putenv("QML_DISABLE_DISK_CACHE", "1")
    nk3.logging.setup()
    logging.info("Creating application")
    CrashHandler.register()
    app = application.Application()
    logging.info("Starting application")
    sys.exit(app.start())
