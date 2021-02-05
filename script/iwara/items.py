# -*- mode: python -*-
import scrapy


class CoreItem(scrapy.Item):
    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value


class AuthorItem(CoreItem):
    name = scrapy.Field()


class TaskMetaItem(CoreItem):

    def __init__(self, *args, **kwargs):
        CoreItem.__init__(self, *args, **kwargs)
        self['datas'] = []

    id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    upload_date = scrapy.Field()
    space = scrapy.Field()
    datas = scrapy.Field()


class TaskVideoItem(TaskMetaItem):
    pass


#
#     def __init__(self, *args, **kwargs):
#         CoreItem.__init__(self, *args, **kwargs)
#         self['datas'] = []
#
#     datas = scrapy.Field()
#
#
class FileSourceItem(CoreItem):
    url = scrapy.Field()
    file = scrapy.Field()
#
#
# class ArticleTextSourceItem(CoreItem):
#     text = scrapy.Field()
