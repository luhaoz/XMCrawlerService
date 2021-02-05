from .environment import Environments
import os
import json
from typing import AnyStr


class Setting(object):
    def __init__(self, namespace: str):
        self.__namespace = namespace

    def runtime(self, name: str) -> dict:
        _runtime_name = Environments.runtime(self.__namespace, '%s.json' % name)

        if os.path.isfile(_runtime_name) is False:
            with open(_runtime_name, 'w') as _init:
                _init.write(json.dumps({}))

        with open(_runtime_name, 'r') as _parameter:
            return json.loads(_parameter.read())

    def space(self, *paths: AnyStr) -> AnyStr:
        _space = Environments.space(self.__namespace, *paths)
        return _space


class Settings(object):
    __settings = dict()

    @classmethod
    def namespace(cls, name: str) -> Setting:
        if name not in cls.__settings:
            cls.__settings.setdefault(name, Setting(name))

        return cls.__settings.get(name)
