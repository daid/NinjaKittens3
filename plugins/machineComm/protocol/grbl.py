from typing import Optional

import serial
import logging
import queue
import re

from .serialProtocol import SerialProtocol


class Grbl(SerialProtocol):
    def __init__(self, ser: serial.Serial, status_callback) -> None:
        super().__init__(ser, status_callback)

        self.__firmware_version_string = ""
        self.__firmware_version = 0

        self._setMaxInFlightByteCount(127)
        self.__getVersionInfo(ser)

        self.__want_to_reset = False

    def isConnected(self) -> bool:
        return self.__firmware_version_string != ""

    def abort(self) -> None:
        self._abortQueue()
        self._write(b"!")  # feed hold, this pauses the machine.
        self.__want_to_reset = True  # When we are idle, request a soft reset.

    def jog(self, *, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> None:
        cmd = "$J=F600"
        if x is not None:
            cmd += " X%f" % x
        if y is not None:
            cmd += " Y%f" % y
        if z is not None:
            cmd += " Z%f" % z
        self.sendRaw(cmd)

    def zero(self, axis: str) -> None:
        for a in axis:
            self.queueRaw("G92 %s0" % (a))

    def __getVersionInfo(self, ser: serial.Serial) -> None:
        ser.timeout = 0.1
        ser.inter_byte_timeout = None
        ser.write(b"$I\n")
        info = ser.read(1024).decode("ascii", "replace").split()
        for line in info:
            if line.startswith("[VER:") and line.endswith("]"):
                self.__firmware_version_string = line.split(":")[1]
                m = re.match(r"([0-9]+)\.([0-9]+)([a-z])", self.__firmware_version_string)
                if m is not None:
                    version_tuple = m.groups()
                    self.__firmware_version = int(version_tuple[0]) << 16 | int(version_tuple[1]) << 8 | (ord(version_tuple[2]) - ord("a"))
            if line.startswith("[OPT:") and line.endswith("]"):
                data = line[5:-1].split(",")
                if len(data) >= 3:
                    self._setMaxInFlightByteCount(int(data[2]))
        logging.info("GRBL Firmware version: 0x%06x %s", self.__firmware_version, self.__firmware_version_string)

    def _processIncommingMessage(self, data: bytes) -> bool:
        line = data.decode("ascii", "replace").strip()
        if line == "ok":
            return True
        if line.startswith("<") and line.endswith(">"):
            # Status report.
            fields = line[1:-1].split("|")
            status = fields.pop(0)
            if status == "Idle" and self.__want_to_reset:
                self._write(b"\x18")  # Request a soft-reset
            return False
        if line.startswith("error:"):  # Error reported as result of a request.
            return True
        if line.startswith("ALARM:"):  # Machine error, machine is now halted.
            return False
        return False

    def _requestStatus(self) -> None:
        self._write(b"?")
