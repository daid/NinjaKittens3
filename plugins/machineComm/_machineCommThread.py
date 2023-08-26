import logging
import platform
import time
from typing import Optional

import serial
from PyQt5.QtCore import pyqtSignal, QThread
from serial.tools import list_ports

from plugins.machineComm.protocol.base import ProtocolBase
from .protocol.grbl import Grbl
from .protocol.marlin import Marlin, DaidFirmware

if serial.VERSION == "3.4" and platform.system() == "Windows":
    logging.warning("pyserial 3.4 on windows has a serious issue. Be warned, your devices will reset during discovery.")


# Thread responsible for communicating with a machine.
class MachineCommThread(QThread):
    STATE_DISCONNECT = 1
    STATE_CONNECTING = 2
    STATE_CONNECTED = 3

    onStatusUpdate = pyqtSignal(str, bool, bool)

    def __init__(self) -> None:
        super().__init__()
        self.__serial = None  # type: Optional[serial.Serial]
        self.__protocol_handler = None  # type: Optional[ProtocolBase]

    def run(self) -> None:
        while True:
            self.onStatusUpdate.emit("DISCONNECTED", False, False)

            try:
                port = self.__autoDetectPort()
                self.onStatusUpdate.emit(f"CONNECTING:{port}", False, False)
                self.__serial = serial.Serial(port)
                time.sleep(2.5)  # Normal bootloader timeout
                self.__protocol_handler = self.__autoDetectBaudrateAndFirmware()
                if self.__protocol_handler is None:
                    time.sleep(15)  # Some bootloaders just have extreme timeouts.
                    self.__protocol_handler = self.__autoDetectBaudrateAndFirmware()

                if self.__protocol_handler is not None:
                    self.onStatusUpdate.emit(f"CONNECTED:{self.__protocol_handler.__class__.__name__}", True, False)
                    self.__protocol_handler.run()
                else:
                    self.__serial.close()
            except:
                logging.exception("Exception in machine comm")

    def __autoDetectPort(self) -> str:
        self.onStatusUpdate.emit("AUTODETECT:DISCONNECT/RECONNECT DEVICE", False, False)
        previous_devices = set(info.device for info in list_ports.comports())
        while True:
            time.sleep(0.5)
            new_list = list_ports.comports()
            for info in new_list:
                if info.device not in previous_devices:
                    self.onStatusUpdate.emit(f"FOUND PORT: {info}", False, False)
                    logging.info(f"Found serial port: {info.description}")
                    return info.device
            previous_devices = set(info.device for info in new_list)

    def __autoDetectBaudrateAndFirmware(self) -> Optional[ProtocolBase]:
        assert self.__serial is not None
        # Ok, we need to detect what baudrate the firmware is talking, and what kind of firmware we are dealing with.
        # We have the following firmwares:
        # * grbl
        # * Smoothie
        # * Marlin
        # * TinyG
        # * Repetier
        # We don't want to look at startup messages, as there is no reason to assume that we can reset the target,
        # and we could have missed the startup message.

        # To detect grbl, it's best to send a "?", as grbl will respond with a status line.
        # Most likely, sending a "?\n" to the rest will report an error, but then we at least have a baudrate,
        # as well as some information about what to expect from the other side.

        self.__serial.timeout = 0.1
        for baudrate in [250000, 115200, 57600, 38400, 19200, 9600]:
            self.__serial.baudrate = baudrate
            self.onStatusUpdate.emit(f"CONNECTING:{self.__serial.port}:{self.__serial.baudrate}", False, False)
            self.__serial.flushInput()
            self.__serial.write(b"?\n")
            response = self.__serial.read(1024)
            logging.info(f"Attempting auto detect at {baudrate}, response: {response}")
            protocol_handler = None  # type: Optional[ProtocolBase]
            if b"<" in response and b">" in response:
                logging.info("Detected grbl status response...")
                protocol_handler = Grbl(self.__serial, lambda msg, connected, busy: self.onStatusUpdate.emit(msg, connected, busy))
            elif b"Unknown command: \"" in response:
                logging.info("Detected possible Marlin response...")
                protocol_handler = Marlin(self.__serial, lambda msg, connected, busy: self.onStatusUpdate.emit(msg, connected, busy))
            elif b"ok - ignored" in response:
                logging.info("Detected possible smoothie firmware...")
            elif b"error" in response:
                logging.info("Detected possible daid firmware...")
                protocol_handler = DaidFirmware(self.__serial, lambda msg, connected, busy: self.onStatusUpdate.emit(msg, connected, busy))
            if protocol_handler is not None and protocol_handler.isConnected():
                return protocol_handler
        self.onStatusUpdate.emit(f"CONNECT FAILED:{self.__serial.port}", False, False)
        logging.info(f"Failed detection on {self.__serial.port}")
        return None

    def queue(self, line: str) -> None:
        assert self.__protocol_handler is not None
        self.__protocol_handler.queueRaw(line)

    def abort(self) -> None:
        assert self.__protocol_handler is not None
        self.__protocol_handler.abort()

    def jog(self, x: Optional[float], y: Optional[float], z: Optional[float]) -> None:
        assert self.__protocol_handler is not None
        self.__protocol_handler.jog(x=x, y=y, z=z)

    def zero(self, axis: str) -> None:
        assert self.__protocol_handler is not None
        self.__protocol_handler.zero(axis)
