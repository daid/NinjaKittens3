import queue
import time
import abc
import logging
from typing import Optional, List, TYPE_CHECKING

import serial

from .base import ProtocolBase

if TYPE_CHECKING:
    Queue = queue.Queue[bytes]
else:
    Queue = queue.Queue


# Base class for any protocol that uses serial communication
# This class facilitates keeping multiple commands in flight towards the target, to maximize throughput.
# It has a normal queue for a sequence of commands, as well as a priority queue that bypasses the normal queue.
# The priority queue can be used for status requests as well as abort commands.
class SerialProtocol(ProtocolBase, abc.ABC):
    def __init__(self, ser: serial.Serial, status_callback) -> None:
        super().__init__(status_callback)
        self.__max_in_flight_data = 0

        self.__serial = ser

        self.__want_to_transmit = None  # type: Optional[bytes]
        self.__priority_queue = Queue()
        self.__transmit_queue = Queue()
        self.__in_flight_data = []  # type: List[int]
        self.__received_data = b''

        self._status_interval = 0.2

    def _getIncommingMessageLength(self, data: bytes) -> Optional[int]:
        index = data.find(b"\n")
        if index > -1:
            return index + 1
        return None

    def _processIncommingMessage(self, data: bytes) -> bool:
        raise NotImplementedError

    def _requestStatus(self) -> None:
        raise NotImplementedError

    def _stringToDataPacket(self, message: str) -> bytes:
        return message.encode("ascii", "replace") + b"\n"

    def _setMaxInFlightByteCount(self, count: int) -> None:
        self.__max_in_flight_data = count

    def _write(self, data: bytes) -> None:
        self.__serial.write(data)

    def _abortQueue(self) -> None:
        self.__priority_queue = Queue()
        self.__transmit_queue = Queue()

    def run(self) -> None:
        self.__serial.timeout = 0.5
        self.__serial.inter_byte_timeout = 0
        last_status_request = time.monotonic()
        while True:
            try:
                input_data = self.__serial.read(4096)
            except serial.SerialException as e:
                logging.error(f"Serial error: {e}")
                return
            if input_data != b"":
                self.__received_data += input_data
                while True:
                    message_length = self._getIncommingMessageLength(self.__received_data)
                    if message_length is None:
                        break
                    msg = self.__received_data[:message_length]
                    self.__received_data = self.__received_data[message_length:]
                    logging.info(f"Reply: {msg}")
                    if self._processIncommingMessage(msg):
                        try:
                            self.__in_flight_data.pop(0)
                        except IndexError:
                            pass
            while self.__tryToTransmit():
                pass
            busy = not self.__transmit_queue.empty() or not self.__priority_queue.empty()
            if busy:
                self.onStatusUpdate(f"BUSY:{self.__transmit_queue.qsize()}", True, True)
            else:
                self.onStatusUpdate("IDLE", True, False)
            if time.monotonic() - last_status_request > self._status_interval:
                last_status_request += self._status_interval
                self._requestStatus()

    def __tryToTransmit(self) -> bool:
        # We take a local reference of the queue, in case _abortQueue is called we need to make sure that empty()
        # and get() are called on the same instance.
        pq = self.__priority_queue
        if self.__want_to_transmit is None and not pq.empty():
            self.__want_to_transmit = pq.get()
            pq.task_done()

        # We take a local reference of the queue, in case _abortQueue is called we need to make sure that empty()
        # and get() are called on the same instance.
        tq = self.__transmit_queue
        if self.__want_to_transmit is None and not tq.empty():
            self.__want_to_transmit = tq.get()
            self.__transmit_queue.task_done()

        in_flight = sum(self.__in_flight_data)
        if self.__want_to_transmit is not None and (in_flight == 0 or in_flight + len(self.__want_to_transmit) <= self.__max_in_flight_data):
            self.__serial.write(self.__want_to_transmit)
            self.__in_flight_data.append(len(self.__want_to_transmit))
            logging.info(f"Sending {self.__want_to_transmit}:{sum(self.__in_flight_data)}")
            self.__want_to_transmit = None
            return True
        return False

    def sendRaw(self, raw_command: str) -> None:
        self.__priority_queue.put(self._stringToDataPacket(raw_command))

    def queueRaw(self, raw_command: str) -> None:
        self.__transmit_queue.put(self._stringToDataPacket(raw_command))
