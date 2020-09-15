# -*- mode: python -*-
# -*- coding: utf-8 -*-
from scrapy.pipelines.files import FileException, FilesPipeline
from .items import AuthorItem, TaskWorkItem, TaskMetaItem, TstorageSourceItem
from scrapy.pipelines.media import MediaPipeline
from core import CoreSpider
from scrapy import Spider, Request, FormRequest
import os
from scrapy.exceptions import DropItem
import demjson


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        pass
        # request.meta['proxy'] = "http://127.0.0.1:10809"

    # def get_media_requests(self, item: TaskItem, info):
    #     yield FormRequest(
    #         url=item['url'],
    #         meta=item,
    #         formdata=item['post']
    #
    #     )
    #
    # def file_path(self, request, response=None, info=None):
    #     return request.meta['name']
    #
    # def item_completed(self, results, item, info):
    #     item_completed = super().item_completed(results, item, info)
    #     print(results)
    #     return item_completed


class TaskPipeline(FilesPipeline):
    _engine = None

    # def open_spider(self, spider):
    #     self._engine = DatabaseUtil.init("pixiv_space")
    #     super().open_spider(spider)

    def get_media_requests(self, item: TstorageSourceItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        _spider._logger.info("Item : %s" % item)

        yield FormRequest(
            url=item['url'],
            meta=item,
            formdata=dict(item)
        )

    # def file_path(self, request, response=None, info=None):

    def file_path(self, request, response=None, info=None):
        return request.meta['file']

    def item_completed(self, results, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        for ok, result in results:
            if ok is False:
                _spider._logger.error("Error : %s-%s" % (item['file'], item['url']))
                raise DropItem("Error : %s-%s" % (item['file'], item['url']))

        # space = info.spider.settings.get('FILES_STORE')
        # os.makedirs(os.path.join(space, item['space']), exist_ok=True)
        # donwalod_space = os.path.join(space, item['space'], 'work.json')
        #
        # _meta = item
        # with open(donwalod_space, 'wb') as meta:
        #     meta.write(demjson.encode(dict(_meta), encoding="utf-8", compactly=False, indent_amount=4))

        _spider._logger.info("Complate : %s-%s" % (item['file'], item['url']))
