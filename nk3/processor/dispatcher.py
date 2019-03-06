import logging
import threading
import time
from typing import List, Optional

from PyQt5.QtCore import QModelIndex

from nk3.document.node import DocumentNode
from nk3.machine.machineInstance import MachineInstance
from nk3.machine.tool import Tool
from nk3.processor.collector import Collector
from nk3.processor.pathUtils import Move
from nk3.processor.processor import Processor
from nk3.qt.QObjectList import QObjectList
from nk3.settingInstance import SettingInstance

log = logging.getLogger(__name__.split(".")[-1])


class Dispatcher:
    def __init__(self, document_list: QObjectList[DocumentNode]) -> None:
        self.onMoveData = lambda moves: None
        self.__machine = None  # type: Optional[MachineInstance]
        self.__document_list = document_list

        self.__trigger = threading.Event()
        self.__thread = threading.Thread(target=self.__handler, daemon=True)
        self.__thread.start()

        self.__document_list.rowsInserted.connect(self.__documentInserted)
        self.__document_list.rowsAboutToBeRemoved.connect(self.__documentRemoved)

    def setActiveMachine(self, machine: MachineInstance) -> None:
        if self.__machine is not None:
            self.__disconnectTrigger(self.__machine)
        self.__machine = machine
        self.__connectTrigger(machine)

    def __connectTrigger(self, object: QObjectList[SettingInstance]) -> None:
        for setting in object:
            setting.valueChanged.connect(self.trigger)
        if isinstance(object, MachineInstance):
            object.tools.onAdd.connect(self.__connectTrigger)
            object.tools.onRemove.connect(self.__disconnectTrigger)
            for tool in object.tools:
                self.__connectTrigger(tool)
        if isinstance(object, Tool):
            object.operations.onAdd.connect(self.__connectTrigger)
            object.operations.onRemove.connect(self.__disconnectTrigger)
            for operation in object.operations:
                self.__connectTrigger(operation)

    def __disconnectTrigger(self, object: QObjectList[SettingInstance]) -> None:
        for setting in object:
            setting.valueChanged.disconnect(self.trigger)
        if isinstance(object, MachineInstance):
            for tool in object.tools:
                self.__disconnectTrigger(tool)
        if isinstance(object, Tool):
            for operation in object.operations:
                self.__disconnectTrigger(operation)

    def __documentInserted(self, parent: QModelIndex, first: int, last: int) -> None:
        for n in range(first, last + 1):
            for document in self.__document_list:
                self.__connectToDocumentNode(document)
        self.trigger()

    def __documentRemoved(self, parent: QModelIndex, first: int, last: int) -> None:
        for n in range(first, last + 1):
            for document in self.__document_list:
                self.__disconnectFromDocumentNode(document)
        self.trigger()

    def __connectToDocumentNode(self, document: DocumentNode) -> None:
        document.operation_indexChanged.connect(self.trigger)
        for child in document:
            self.__connectToDocumentNode(child)

    def __disconnectFromDocumentNode(self, document: DocumentNode) -> None:
        document.operation_indexChanged.disconnect(self.trigger)
        for child in document:
            self.__disconnectFromDocumentNode(child)

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
        moves = []  # type: List[Move]
        machine = self.__machine
        if machine is not None:
            collector = Collector(self.__document_list, machine)
            for job in collector.getJobs():
                moves += Processor(job).process()
        # Notify the main application of new processed data.
        # The main application can display this and export it.
        self.onMoveData(moves)
