import logging

from typing import Dict, Tuple

from nk3.document.node import DocumentNode
from nk3.document.vectorNode import DocumentVectorNode
from nk3.processor.job import Job

log = logging.getLogger(__name__.split(".")[-1])


class Collector:
    def __init__(self, document_list, tool_list):
        self.__result = {}  # type: Dict[Tuple[int, int], Job]
        self.__tool_list = tool_list
        for document in document_list:
            self.__collect(document, (-1, -1))

    def __collect(self, document: DocumentNode, collection_index: Tuple[int, int]) -> None:
        if document.operation_index > -1:
            collection_index = (document.tool_index, document.operation_index)
        if collection_index[0] > -1 and collection_index[1] > -1 and isinstance(document, DocumentVectorNode):
            if collection_index not in self.__result:
                tool_instance = self.__tool_list[collection_index[0]]
                operation_instance = tool_instance.operations[collection_index[1]]
                self.__result[collection_index] = Job(operation_instance)
            for path in document.getPaths():
                if path.closed:
                    self.__result[collection_index].addClosed(path)
                else:
                    self.__result[collection_index].addOpen(path)
        for child in document:
            self.__collect(child, collection_index)

    def getJobs(self):
        return map(lambda n: n[1], sorted(self.__result.items()))