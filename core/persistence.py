from abc import ABC
from typing import Optional, List


class CorePersistence(ABC):
    def filter(self, ids: List, group: str):
        pass

    def save(self, item):
        pass
