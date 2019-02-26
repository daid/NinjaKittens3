import logging
import threading
import time

from nk3.machine.machineInstance import MachineInstance
from nk3.processor.collector import Collector
from nk3.processor.export import Export
from nk3.processor.processor import Processor

log = logging.getLogger(__name__.split(".")[-1])


class Dispatcher:
    def __init__(self, machine: MachineInstance, document_list) -> None:
        self.onMoveData = lambda moves: None
        self.__machine = machine
        self.__document_list = document_list

        self.__trigger = threading.Event()
        self.__thread = threading.Thread(target=self.__handler, daemon=True)
        self.__thread.start()

        self.__machine.tools.rowsInserted.connect(self.__toolInserted)
        self.__document_list.rowsInserted.connect(self.__documentInserted)

    def __toolInserted(self, parent, first, last):
        for n in range(first, last+1):
            for setting in self.__machine.tools[n]:
                setting.valueChanged.connect(self.trigger)
                self.__machine.tools[n].operations.rowsInserted.connect(lambda parent, first, last: self.__operationInserted(self.__machine.tools[n], first, last))
            self.__operationInserted(self.__machine.tools[n], 0, len(self.__machine.tools[n].operations) - 1)

    def __operationInserted(self, tool, first, last):
        for n in range(first, last+1):
            for setting in tool.operations[n]:
                setting.valueChanged.connect(self.trigger)

    def __documentInserted(self, parent, first, last):
        for n in range(first, last + 1):
            for document in self.__document_list:
                self.__connectToDocumentNode(document)
        self.trigger()

    def __connectToDocumentNode(self, document):
        document.operation_indexChanged.connect(self.trigger)
        for child in document:
            self.__connectToDocumentNode(child)

    def trigger(self):
        self.__trigger.set()

    def __handler(self):
        while True:
            self.__trigger.wait()
            time.sleep(0.01)
            self.__trigger.clear()

            try:
                self.__process()
            except:
                log.exception("Exception during processing")

    def __process(self):
        # Collect all paths from nodes and match them with the respective operations
        # Convert paths to pyclipper
        collector = Collector(self.__document_list, self.__machine)
        moves = []
        for job in collector.getJobs():
            moves += Processor(job).process()
        # Notify the main application of new processed data.
        # The main application can display this and export it.
        self.onMoveData(moves)
