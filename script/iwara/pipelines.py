# -*- mode: python -*-
# -*- coding: utf-8 -*-
from scrapy.pipelines.files import FileException, FilesPipeline, S3FilesStore
from .items import AuthorItem, TaskVideoItem, TaskMetaItem, FileSourceItem
from scrapy.pipelines.media import MediaPipeline
from core import CoreSpider
from scrapy import Spider, Request, FormRequest
from scrapy.exceptions import DropItem


class TaskPipeline(FilesPipeline):
    _engine = None

    # def open_spider(self, spider):
    #     self._engine = DatabaseUtil.init("pixiv_space")
    #     super().open_spider(spider)

    def get_media_requests(self, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        _spider.logger.info("Item : %s" % item)

        for _resource in item['datas']:
            yield Request(_resource['url'], meta={
                'item': item,
                'resource': _resource
            })

    def file_path(self, request, response=None, info=None, *, item=None):
        _item = request.meta['item']
        _resource = request.meta['resource']

        resource_path = "/".join([
            _item['space'],
            _resource['file']
        ])
        return resource_path

    def item_completed(self, results, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        for ok, result in results:
            if ok is False:
                _spider.logger.error("Error : %s-%s" % (item['title'], item['id']))
                raise DropItem("Error : %s-%s" % (item['title'], item['id']))

        # space = info.spider.settings.get('FILES_STORE')
        # os.makedirs(os.path.join(space, item['space']), exist_ok=True)
        # donwalod_space = os.path.join(space, item['space'], 'work.json')
        #
        # _meta = item
        # with open(donwalod_space, 'wb') as meta:
        #     meta.write(demjson.encode(dict(_meta), encoding="utf-8", compactly=False, indent_amount=4))

        # _spider._logger.info("Complate : %s-%s-%s" % (item['title'], item['id'], donwalod_space))
        _spider.logger.info("Complate : %s-%s" % (item['title'], item['id']))
