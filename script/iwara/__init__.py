import os
from core.util import path_format
from core.runtime import App
from .items import TaskMetaItem
from urllib.parse import urlparse, parse_qsl

# def author_space(item):
#     return path_format(item['author']['name'])
#
#
# def item_space(item):
#     illust_path = "%s_%s" % (item['title'], item['id'])
#     return path_format(illust_path)


#
# def file_space(item):
#     return "/".join([
#         author_space(item),
#         item_space(item),
#     ])

# def file_space(item: TaskMetaItem):
#     _parse = urlparse(_resource)
#     _query = dict(parse_qsl(_parse.query))
#     _file = "%s%s" % (_item['title'], os.path.splitext(_query['file'])[-1])


class Runtime(object):
    @classmethod
    def path(cls):
        _root = os.path.join(App.path().get("root"))
        return {
            "FILES_STORE": os.path.join(_root, "space", "iwara")
        }
