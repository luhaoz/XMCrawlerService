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
    space = scrapy.Field()
    count = scrapy.Field()


class TaskWorkItem(TaskMetaItem):
    source = scrapy.Field()


class SourceItem(CoreItem):
    sources = scrapy.Field()


class TaskNovelItem(TaskWorkItem):
    content = scrapy.Field()


class TaskIllustItem(TaskMetaItem):
    pass
