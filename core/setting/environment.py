import os
from typing import AnyStr


class Environments(object):
    @classmethod
    def runtime(cls, *paths: AnyStr):
        _path = os.path.join(os.environ.get("SPIDER_RUNTIME"), *paths)
        _space_path = os.path.dirname(_path)
        os.makedirs(_space_path, exist_ok=True)
        return _path

    @classmethod
    def space(cls, *paths: AnyStr):
        _path = os.path.join(os.environ.get("SPIDER_SPACE"), *paths)
        os.makedirs(_path, exist_ok=True)
        return _path
