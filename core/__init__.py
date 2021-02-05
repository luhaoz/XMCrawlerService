from abc import ABC

from scrapy import Spider, Request, FormRequest
import sys
from .logging import logger
from logging import Logger
from pydispatch import dispatcher
from scrapy import signals
from .database import CoreDataSpace, DataSpaces
from .persistence import CorePersistence
from typing import Optional


class CoreSpider(Spider, ABC):

    def __init__(self):
        Spider.__init__(self, name=self.__class__.script_name())
        dispatcher.connect(self.__spider_opened, signals.spider_opened)
        dispatcher.connect(self.__spider_closed, signals.spider_closed)
        self.persistence: Optional[CorePersistence] = None

    @classmethod
    def arguments(cls, parser):
        pass

    @classmethod
    def script_name(cls):
        return cls.__module__

    @classmethod
    def settings(cls):
        return {}

    def __spider_closed(self, spider):
        self.logger.info("爬虫结束")

    def __spider_opened(self, spider):
        self.logger.info("爬虫开始")
