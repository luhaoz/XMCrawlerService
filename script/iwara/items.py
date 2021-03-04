# -*- mode: python -*-
import scrapy


class CoreItem(scrapy.Item):
    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value


class AuthorItem(CoreItem):
    id = scrapy.Field()
    name = scrapy.Field()


class TaskMetaItem(CoreItem):

    def __init__(self, *args, **kwargs):
        CoreItem.__init__(self, *args, **kwargs)
        self['sources'] = []

    id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    upload_date = scrapy.Field()
    sources = scrapy.Field()
    type = scrapy.Field()


class TaskVideoItem(TaskMetaItem):
    pass


class FileSourceItem(CoreItem):
    url = scrapy.Field()
    file = scrapy.Field()
