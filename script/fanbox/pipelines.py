# -*- mode: python -*-
# -*- coding: utf-8 -*-
from scrapy.pipelines.files import FileException, FilesPipeline
from .items import AuthorItem, TaskWorkItem, TaskMetaItem, FileSourceItem
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


class TaskPipeline(FilesPipeline):
    _engine = None

    # def open_spider(self, spider):
    #     self._engine = DatabaseUtil.init("pixiv_space")
    #     super().open_spider(spider)

    def get_media_requests(self, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        _spider._logger.info("Item : %s" % item)

        def _datas_enumerate(datas):
            _index = 0
            for _item in datas:
                if isinstance(_item, FileSourceItem):
                    yield _index, _item
                    _index += 1

        for _index, _resource in _datas_enumerate(item['datas']):
            yield Request(_resource['url'], meta={
                'index': str(_index).zfill(4),
                'item': item,
                'resource': _resource
            })

    def file_path(self, request, response=None, info=None):
        _index = request.meta['index']
        _item = request.meta['item']
        _resource = request.meta['resource']

        resource_path = os.path.join(
            _item['space'],
            "%s_%s" % (_index, _resource['file'])
        )
        return resource_path

    def item_completed(self, results, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        for ok, result in results:
            if ok is False:
                _spider._logger.error("Error : %s-%s" % (item['title'], item['id']))
                raise DropItem("Error : %s-%s" % (item['title'], item['id']))

        space = info.spider.settings.get('FILES_STORE')
        os.makedirs(os.path.join(space, item['space']), exist_ok=True)
        donwalod_space = os.path.join(space, item['space'], 'work.json')

        _meta = item
        with open(donwalod_space, 'wb') as meta:
            meta.write(demjson.encode(dict(_meta), encoding="utf-8", compactly=False, indent_amount=4))

        _spider._logger.info("Complate : %s-%s-%s" % (item['title'], item['id'], donwalod_space))
