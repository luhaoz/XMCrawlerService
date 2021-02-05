# -*- mode: python -*-
import scrapy


class CoreItem(scrapy.Item):
    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value


class AuthorItem(CoreItem):
    id = scrapy.Field()
    name = scrapy.Field()
    creator = scrapy.Field()


class TaskMetaItem(CoreItem):
    id = scrapy.Field()
    title = scrapy.Field()
    tags = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    upload_date = scrapy.Field()
    type = scrapy.Field()
    space = scrapy.Field()
    count = scrapy.Field()


class TaskWorkItem(TaskMetaItem):

    def __init__(self, *args, **kwargs):
        CoreItem.__init__(self, *args, **kwargs)
        self['datas'] = []

    datas = scrapy.Field()
    cookie = scrapy.Field()


class FileSourceItem(CoreItem):

    def __init__(self, *args, **kwargs):
        CoreItem.__init__(self, *args, **kwargs)
        if "file" not in kwargs:
            self['file'] = _file = kwargs.get("url").split('/')[-1]

    url = scrapy.Field()
    file = scrapy.Field()


class ArticleTextSourceItem(CoreItem):
    text = scrapy.Field()
