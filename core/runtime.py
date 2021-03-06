import os
import json


class App(object):
    @classmethod
    def runtime(cls):
        _path = os.environ.get("XM_SPIDER_RUNTIME")
        return _path

    @classmethod
    def space(cls):
        _path = os.environ.get("XM_SPIDER_SPACE")
        return _path


# class Config(object):
#     runtime = os.path.join(App.path().get("root"), "runtime")


class Parameter(object):
    _data = None

    def __init__(self, data):
        self._data = data

    def json(self):
        return json.loads(self._data)

    def data(self):
        return self._data


class Space(object):
    _space = None

    def __init__(self, space):
        self._space = space

    #
    def parameter(self, file):
        _space_file = os.path.join(self._space, file)
        if os.path.isfile(_space_file) is False:
            with open(_space_file, 'w') as _init:
                _init.write(json.dumps({}))
        with open(_space_file, 'r') as _parameter:
            return Parameter(_parameter.read())


class Setting(object):

    @classmethod
    def space(cls, name):
        _space = os.path.join(Config.runtime, name)
        os.makedirs(_space, exist_ok=True)
        return Space(_space)
