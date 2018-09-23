from abc import ABC, abstractmethod


class FileReader(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def load(self, filename: str):
        pass
