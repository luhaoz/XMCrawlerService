import os
from core.util import path_format
from core.runtime import App


def author_space(item):
    author_path = "%s_%s_%s" % (item['author']['name'], item['author']['creator'], item['author']['id'])
    return path_format(author_path)


def item_space(item):
    illust_path = "%s_%s" % (item['title'], item['id'])
    return path_format(illust_path)


def file_space(item):
    return os.path.join(
        author_space(item),
        item_space(item),
    )


class Runtime(object):
    @classmethod
    def path(cls):
        _root = os.path.join(App.path().get("root"))
        return {
            "FILES_STORE": os.path.join(_root, "space", 'fanbox')
        }
