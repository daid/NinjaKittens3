import os
import logging
import sys
from nk3 import application
from nk3.crashHandler import CrashHandler

log = logging.getLogger(__name__.split(".")[-1])


if __name__ == '__main__':
    os.putenv("QML_DISABLE_DISK_CACHE", "1")
    logging.basicConfig(format="%(asctime)s:%(levelname)10s:%(name)20s:%(message)s", level=logging.INFO)
    CrashHandler.register()
    log.info("Creating application")
    app = application.Application()
    log.info("Starting application")
    sys.exit(app.start())
