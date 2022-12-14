from __future__ import annotations

from abc import ABC, abstractmethod, abstractstaticmethod
from typing import Generic, List, TypeVar, Protocol, Callable, Type

T = TypeVar('T')
BODY = TypeVar('BODY')

# class CallbackType(Generic[T], Protocol):
#     def __call__(self, body: BODY, ack: QueueACK[BODY]) -> None:
#         ...

class QueueACK(ABC, Generic[BODY]):
    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def success(self) -> None:
        ...
    
    @abstractmethod
    def failed(self, reason: str) -> None:
        ...


CallbackType = Callable[[T, QueueACK[T]], None]


class ChannelInterface(ABC, Generic[BODY]):    
    @abstractmethod
    def add_consumer(self, name: str, consumer: CallbackType[BODY]) -> None:
        ...

    @abstractmethod
    def publish(self, name: str, data: BODY):
        ...

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...

class QueueInterface(ABC, Generic[T, BODY]):
    @abstractmethod
    def __init__(self, conf: T) -> None:
        ...

    @abstractstaticmethod
    def get_configurer() -> Type[T]:
        ...

    @abstractmethod
    def declare_queue(self, name: str, **kwargs) -> ChannelInterface[BODY]:
        ...

