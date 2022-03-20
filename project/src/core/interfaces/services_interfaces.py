from abc import ABC, abstractmethod
from typing import Any, Optional


class InterfaceDelete(ABC):
    @abstractmethod
    def delete(self, value: Any) -> bool:
        pass


class InterfaceDetail(ABC):
    @abstractmethod
    def get_detail(self, value: Any) -> dict:
        pass


class InterfaceList(ABC):
    @abstractmethod
    def get_list(self, optional_filter: Optional[Any] = None) -> dict:
        pass


class InterfaceRegister(ABC):
    @abstractmethod
    def register(self, value: Any) -> dict:
        pass


class InterfaceUpdate(ABC):
    @abstractmethod
    def update(self, identity: str, updates: Any) -> dict:
        pass
