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
    id = scrapy.Field()
    title = scrapy.Field()
    tags = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    upload_date = scrapy.Field()
    type = scrapy.Field()


class TaskNovelItem(TaskMetaItem):
    def __init__(self):
        TaskMetaItem.__init__(self)
        self['sources'] = []

    content = scrapy.Field()
    sources = scrapy.Field()
    count = scrapy.Field()
    total = scrapy.Field()


class TaskIllustItem(TaskMetaItem):
    def __init__(self):
        TaskMetaItem.__init__(self)
        self['sources'] = []

    sources = scrapy.Field()
    count = scrapy.Field()
