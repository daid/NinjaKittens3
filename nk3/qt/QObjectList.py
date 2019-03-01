from PyQt5.QtCore import Qt, QAbstractListModel, QVariant, QModelIndex, QObject, pyqtSignal
from typing import List, TypeVar, Generic, Dict, Any, Iterator, TYPE_CHECKING

from nk3.qt.QObjectBase import QObjectBaseMeta, qtSlot

T = TypeVar('T', bound=QObject)

if not TYPE_CHECKING:
    # Workaround for python < 3.7, Generic[] has a metaclass, which conflicts with our QObjectBaseMeta
    # So replace it with an empty class at runtime.
    Generic = {T: type("Generic[T]", (), {})}

class QObjectList(Generic[T], QAbstractListModel, metaclass=QObjectBaseMeta):
    RoleItem = Qt.UserRole + 1

    onAdd = pyqtSignal(QObject)
    onRemove = pyqtSignal(QObject)

    def __init__(self, entry_name: str) -> None:
        super().__init__()
        self.__entries = []  # type: List[T]
        self.__entry_name = entry_name.encode("utf-8")

    def roleNames(self) -> Dict[int, bytes]:  ## Part of QAbstractListModel
        return {
            self.RoleItem: self.__entry_name,
        }

    def rowCount(self, parent: QObject) -> int:  ## Part of QAbstractListModel
        return len(self.__entries)

    def data(self, index: QModelIndex, role: int) -> Any:  ## Part of QAbstractListModel
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
        self.onRemove.emit(self.__entries[index])
        del self.__entries[index]
        self.endRemoveRows()

    def insert(self, index: int, item: T) -> None:
        self.beginInsertRows(QModelIndex(), index, index)
        self.onAdd.emit(item)
        self.__entries.insert(index, item)
        self.endInsertRows()

    def __iter__(self) -> Iterator[T]:
        return iter(self.__entries)

    def __len__(self) -> int:
        return len(self.__entries)

    def __getitem__(self, index: int) -> T:
        return self.__entries[index]
