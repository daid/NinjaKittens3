import logging
import threading
import time
from typing import Any, List

from nk3.QObjectList import QObjectList
from nk3.document.node import DocumentNode
from nk3.machine.machineInstance import MachineInstance
from nk3.machine.tool.toolInstance import ToolInstance
from nk3.processor.collector import Collector
from nk3.processor.pathUtils import Move
from nk3.processor.processor import Processor

log = logging.getLogger(__name__.split(".")[-1])


class Dispatcher:
    def __init__(self, machine: MachineInstance, document_list: QObjectList[DocumentNode]) -> None:
        self.onMoveData = lambda moves: None
        self.__machine = machine
        self.__document_list = document_list

        self.__trigger = threading.Event()
        self.__thread = threading.Thread(target=self.__handler, daemon=True)
        self.__thread.start()

        self.__machine.tools.rowsInserted.connect(self.__toolInserted)
        self.__document_list.rowsInserted.connect(self.__documentInserted)

    def __toolInserted(self, parent: Any, first: int, last: int) -> None:
        for n in range(first, last+1):
            for setting in self.__machine.tools[n]:
                setting.valueChanged.connect(self.trigger)
                self.__machine.tools[n].operations.rowsInserted.connect(lambda parent, first, last: self.__operationInserted(self.__machine.tools[n], first, last))
            self.__operationInserted(self.__machine.tools[n], 0, len(self.__machine.tools[n].operations) - 1)

    def __operationInserted(self, tool: ToolInstance, first: int, last: int) -> None:
        for n in range(first, last+1):
            for setting in tool.operations[n]:
                setting.valueChanged.connect(self.trigger)

    def __documentInserted(self, parent: Any, first: int, last: int) -> None:
        for n in range(first, last + 1):
            for document in self.__document_list:
                self.__connectToDocumentNode(document)
        self.trigger()

    def __connectToDocumentNode(self, document: DocumentNode) -> None:
        document.operation_indexChanged.connect(self.trigger)
        for child in document:
            self.__connectToDocumentNode(child)

    def trigger(self) -> None:
        self.__trigger.set()

    def __handler(self) -> None:
        while True:
            self.__trigger.wait()
            time.sleep(0.01)
            self.__trigger.clear()

            try:
                self.__process()
            except:
                log.exception("Exception during processing")

    def __process(self) -> None:
        # Collect all paths from nodes and match them with the respective operations
        collector = Collector(self.__document_list, self.__machine)
        moves = []  # type: List[Move]
        for job in collector.getJobs():
            moves += Processor(job).process()
        # Notify the main application of new processed data.
        # The main application can display this and export it.
        self.onMoveData(moves)
