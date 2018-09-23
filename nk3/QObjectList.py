from PyQt5.QtCore import Qt, QAbstractListModel, QVariant, QModelIndex, pyqtProperty, pyqtSlot, QObject
from typing import List, TypeVar

from nk3.QObjectBase import QObjectBaseMeta, qtSlot

T = TypeVar('T')


class QObjectList(QAbstractListModel, metaclass=QObjectBaseMeta):
    RoleItem = Qt.UserRole + 1

    def __init__(self):
        super().__init__()
        self.__entries = []  # type: List[T]

    def roleNames(self):  ## Part of QAbstractListModel
        return {
            self.RoleItem: b"item",
        }

    def rowCount(self, parent):  ## Part of QAbstractListModel
        return len(self.__entries)

    def data(self, index, role):  ## Part of QAbstractListModel
        if not index.isValid():
            return QVariant()
        if role == self.RoleItem:
            return self.__entries[index.row()]
        return QVariant()

    @qtSlot
    def size(self) -> int:
        return len(self.__entries)

    @qtSlot
    def get(self, index: int) -> QObject:
        return self.__entries[index]

    def append(self, item: T) -> None:
        item.setParent(self)
        self.insert(len(self.__entries), item)

    def remove(self, index: int) -> None:
        self.beginRemoveRows(QModelIndex(), index, index)
        del self.__entries[index]
        self.endRemoveRows()

    def insert(self, index: int, item: T) -> None:
        self.beginInsertRows(QModelIndex(), index, index)
        self.__entries.insert(index, item)
        self.endInsertRows()

    def __iter__(self):
        return iter(self.__entries)

    def __len__(self) -> int:
        return len(self.__entries)

    def __getitem__(self, index: int) -> T:
        return self.__entries[index]
