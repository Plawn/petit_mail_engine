from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, Callable, get_args
import yaml
import json

T = TypeVar('T')


class Configurer(Generic[T], ABC):
    def __init__(self):
        self.did_init = False
        self._content = None

    @abstractmethod
    def _init(self) -> None:
        ...

    def ensure_inited(self) -> None:
        if not self.did_init:
            self._init()

    def content(self) -> T:
        self.ensure_inited()
        return self._content


class FileConfigurer(Generic[T], Configurer[T]):
    def __init__(self, filename: str, loader: Callable[[str], T]):
        super().__init__()
        self.filename = filename
        self.loader = loader

    def _init(self) -> None:
        with open(self.filename, 'r') as f:
            content = self.loader(f.read())
            type_t = get_args(self.__orig_class__)[0]
            self._content = type_t(**content) 

class JsonConfigurer(Generic[T], FileConfigurer[T]):
    def __init__(self, filename: str) :
        super().__init__(filename, json.loads)


class YamlConfigurer(Generic[T], FileConfigurer[T]):
    def __init__(self, filename: str) :
        super().__init__(filename, yaml.safe_load)

