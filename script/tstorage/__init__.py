import os
from core.runtime import App


class Runtime(object):
    @classmethod
    def path(cls):
        _root = os.path.join(App.path().get("root"))
        return {
            "FILES_STORE": os.path.join(_root, "space", "tstorages")
        }
