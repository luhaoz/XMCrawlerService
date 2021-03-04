# -*- mode: python -*-
# -*- coding: utf-8 -*-
from scrapy.pipelines.files import FileException, FilesPipeline, S3FilesStore
from .items import AuthorItem, TaskVideoItem, TaskMetaItem, FileSourceItem
from scrapy.pipelines.media import MediaPipeline
from core import CoreSpider
from scrapy import Spider, Request, FormRequest
from scrapy.exceptions import DropItem
from urllib.parse import urlparse, parse_qsl
import os
from core.util import path_format
import demjson


class TaskPipeline(FilesPipeline):
    _engine = None

    # def open_spider(self, spider):
    #     self._engine = DatabaseUtil.init("pixiv_space")
    #     super().open_spider(spider)

    def get_media_requests(self, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        _spider.logger.info("Item : %s" % item)

        for _resource in item['sources']:
            yield Request(_resource, meta={
                'item': item,
                'resource': _resource
            })

    def file_path(self, request, response=None, info=None, *, item=None):
        _item = request.meta['item']
        _resource = request.meta['resource']
        _parse = urlparse(_resource)
        _query = dict(parse_qsl(_parse.query))
        _file = "%s%s" % (_item['title'], os.path.splitext(_query['file'])[-1])

        resource_path = "/".join([
            path_format(_item['author']['name']),
            path_format(_item['title']),
            _file
        ])
        return resource_path

    def item_completed(self, results, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        for ok, result in results:
            if ok is False:
                _spider.logger.error("Error : %s-%s" % (item['title'], item['id']))
                raise DropItem("Error : %s-%s" % (item['title'], item['id']))
        _space = info.spider.settings.get('FILES_STORE')
        donwalod_space = os.path.join(_space, path_format(item['author']['name']), path_format(item['title']), 'work.json')
        #
        # _meta = item
        with open(donwalod_space, 'wb') as meta:
            meta.write(demjson.encode(dict(item), encoding="utf-8", compactly=False, indent_amount=4))

        _spider.persistence.save(item)
        _spider.logger.info("Complate : %s-%s" % (item['title'], item['id']))
