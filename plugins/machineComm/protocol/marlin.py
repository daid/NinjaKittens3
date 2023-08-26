from typing import Optional, Callable

import serial
import logging
import time

from .serialProtocol import SerialProtocol


class Marlin(SerialProtocol):
    def __init__(self, ser: serial.Serial, status_callback: Callable[[str, bool, bool], None]) -> None:
        super().__init__(ser, status_callback)

        self.__firmware_version_string = ""

        self._setMaxInFlightByteCount(64)
        self.__getVersionInfo(ser)

    def isConnected(self) -> bool:
        return self.__firmware_version_string != ""

    def abort(self) -> None:
        self._abortQueue()
        self._write(b"M410\n")  # Abort all moves

    def jog(self, *, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> None:
        self.queueRaw("G91")
        cmd = "G1"
        if x is not None:
            cmd += " X%f" % x
        if y is not None:
            cmd += " Y%f" % y
        if z is not None:
            cmd += " Z%f" % z
        self.queueRaw(cmd)
        self.queueRaw("G90")

    def zero(self, axis: str) -> None:
        for a in axis:
            self.queueRaw("G92 %s0" % (a))

    def __getVersionInfo(self, ser: serial.Serial) -> None:
        ser.timeout = 0.5
        ser.inter_byte_timeout = None
        ser.write(b"\nM115\n")
        info = ser.read(1024).decode("ascii", "replace").split()
        for line in info:
            if line.startswith("FIRMWARE_NAME:"):
                self.__firmware_version_string = line
        logging.info("Marlin Firmware: %s", self.__firmware_version_string)

    def _processIncommingMessage(self, data: bytes) -> bool:
        line = data.decode("ascii", "replace").strip()
        if line == "ok":
            return True
        return False

    def _requestStatus(self) -> None:
        pass


class DaidFirmware(SerialProtocol):
    def __init__(self, ser: serial.Serial, status_callback: Callable[[str, bool, bool], None]) -> None:
        super().__init__(ser, status_callback)

        self._setMaxInFlightByteCount(64)
        ser.timeout = 0.5
        ser.inter_byte_timeout = None

    def isConnected(self) -> bool:
        return True

    def abort(self) -> None:
        self._abortQueue()

    def jog(self, *, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> None:
        self.queueRaw("G91")
        cmd = "G1"
        if x is not None:
            cmd += " X%f" % x
        if y is not None:
            cmd += " Y%f" % y
        if z is not None:
            cmd += " Z%f" % z
        self.queueRaw(cmd)
        self.queueRaw("G90")

    def zero(self, axis: str) -> None:
        for a in axis:
            self.queueRaw("G92 %s0" % (a))

    def _processIncommingMessage(self, data: bytes) -> bool:
        line = data.decode("ascii", "replace").strip()
        if line == "ok" or line == "error":
            return True
        return False

    def _requestStatus(self) -> None:
        pass
