# -*- mode: python -*-
import scrapy


class CoreItem(scrapy.Item):
    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value


class TaskMetaItem(CoreItem):
    id = scrapy.Field()
    url = scrapy.Field()
    space = scrapy.Field()
