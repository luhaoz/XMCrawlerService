# -*- mode: python -*-
from scrapy.pipelines.files import FileException, FilesPipeline
from .items import AuthorItem, TaskMetaItem, TaskNovelItem
from scrapy.pipelines.media import MediaPipeline
from logging import Logger
from scrapy import Spider, Request, FormRequest
import os
from scrapy.exceptions import DropItem
import demjson
from ..pixiv import novel_format, novel_bind_image, novel_html


class TaskPipeline(FilesPipeline):
    pass

    def get_media_requests(self, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider = info.spider
        _spider._logger.info("Item : %s" % item)

        for resource in item['source']['sources']:
            yield Request(resource, meta={
                'item': item,
                'resource': resource
            }, headers={
                'Referer': 'https://www.pixiv.net/artworks/%s' % item['id']
            })

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        resource = request.meta['resource']
        resource_path = os.path.join(
            item['space'],
            resource.split('/')[-1]
        )
        return resource_path

    def item_completed(self, results, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        # print(results)
        _spider = info.spider
        for ok, result in results:
            if ok is False:
                _spider._logger.error("Error : %s-%s" % (item['title'], item['id']))
                raise DropItem("Error : %s-%s" % (item['title'], item['id']))

        space = info.spider.settings.get('FILES_STORE')
        os.makedirs(os.path.join(space, item['space']), exist_ok=True)
        donwalod_space = os.path.join(space, item['space'], 'illust.json')

        _meta = item
        with open(donwalod_space, 'wb') as meta:
            meta.write(demjson.encode(dict(_meta), encoding="utf-8", compactly=False, indent_amount=4))

        if isinstance(item, TaskNovelItem):
            content = os.path.join(space, item['space'], 'novel.html')
            with open(content, 'w', encoding='utf-8') as meta:
                meta.write(novel_html(item['title'], item['content']))

        _spider._logger.info("Complate : %s-%s-%s" % (item['title'], item['id'], donwalod_space))



        # _databaseItem = DatabaseNovelItem(_databaseItem)
        # _databaseItem['content'] = item['content']
        # _databaseItem['path'] = content
        # _meta = TaskMetaResultItem(item)
        # _meta['results'] = [
        #     _result for _ok, _result in results
        # ]

        # space = info.spider.settings.get('FILES_STORE')

        # for ok, result in results:
        #     if ok is False:
        #         info.spider.spider_log.error("Error : %s-%s" % (item['title'], item['id']))
        #         raise DropItem("Error : %s-%s" % (item['title'], item['id']))
        #
        # space = info.spider.settings.get('FILES_STORE')
        #
        # os.makedirs(os.path.join(space, item['space']), exist_ok=True)
        # donwalod_space = os.path.join(space, item['space'], 'illust.json')
        #
        # _meta = TaskMetaResultItem(item)
        # _meta['results'] = [
        #     _result for _ok, _result in results
        # ]
        #
        # # DatabaseIllustItem, DatabaseNovelItem
        # _databaseItem = DatabaseIllustItem(_meta)
        #
        # with open(donwalod_space, 'wb') as meta:
        #     meta.write(demjson.encode(dict(_meta), encoding="utf-8", compactly=False, indent_amount=4))
        #
        # if isinstance(item, TaskNovelItem):
        #     content = os.path.join(space, item['space'], 'novel.html')
        #     with open(content, 'w', encoding='utf-8') as meta:
        #         meta.write(novel_html(item['title'], item['content']))
        #     _databaseItem = DatabaseNovelItem(_databaseItem)
        #     _databaseItem['content'] = item['content']
        #     _databaseItem['path'] = content
        #
        # _root_space = os.path.dirname(item['space'])
        # _database = os.path.join(space, _root_space, '%s_main.db' % info.spider.__class__.script_name())
        # info.spider.space.get(_database).mark_complete(_databaseItem)
        # info.spider.spider_log.info("Complate : %s-%s-%s" % (item['title'], item['id'], donwalod_space))

        # from scrapy.pipelines.files import FileException, FilesPipeline
        # from scrapy.http.response.html import HtmlResponse
        # from scrapy import Spider, Request, FormRequest
        # import os
        # from core.util import path_format, db_space
        # import demjson
        # from .items import AuthorItem, TaskItem, SourceItem, TaskNovelItem, TaskMetaItem, TaskMetaResultItem, DatabaseIllustItem, DatabaseNovelItem
        # from scrapy.pipelines.media import MediaPipeline
        # from ..pixiv import novel_format, novel_bind_image, novel_html, author_space, file_space
        # from tinydb import Query
        # from scrapy.exceptions import DropItem
        #
        #
        # class ProxyPipeline(object):
        #     def process_request(self, request, spider):
        #         request.meta['proxy'] = "http://127.0.0.1:10809"
        #
        #
        # class TaskPipeline(FilesPipeline):
        #
        #     def get_media_requests(self, item: TaskItem, info: MediaPipeline.SpiderInfo):
        #         spider = info.spider
        #         spider.spider_log.info("Item : %s" % item)
        #
        #         for resource in item['source']['sources']:
        #             yield Request(resource, meta={
        #                 'item': item,
        #                 'resource': resource
        #             }, headers={
        #                 'Referer': 'https://www.pixiv.net/artworks/%s' % item['id']
        #             })
        #
        #     def file_path(self, request, response=None, info=None):
        #         item = request.meta['item']
        #         resource = request.meta['resource']
        #         resource_path = os.path.join(
        #             item['space'],
        #             resource.split('/')[-1]
        #         )
        #         return resource_path
        #
        #     def item_completed(self, results, item, info: MediaPipeline.SpiderInfo):
        #         # print(results)
        #
        #         for ok, result in results:
        #             if ok is False:
        #                 info.spider.spider_log.error("Error : %s-%s" % (item['title'], item['id']))
        #                 raise DropItem("Error : %s-%s" % (item['title'], item['id']))
        #
        #         space = info.spider.settings.get('FILES_STORE')
        #
        #         os.makedirs(os.path.join(space, item['space']), exist_ok=True)
        #         donwalod_space = os.path.join(space, item['space'], 'illust.json')
        #
        #         _meta = TaskMetaResultItem(item)
        #         _meta['results'] = [
        #             _result for _ok, _result in results
        #         ]
        #
        #         # DatabaseIllustItem, DatabaseNovelItem
        #         _databaseItem = DatabaseIllustItem(_meta)
        #
        #         with open(donwalod_space, 'wb') as meta:
        #             meta.write(demjson.encode(dict(_meta), encoding="utf-8", compactly=False, indent_amount=4))
        #
        #         if isinstance(item, TaskNovelItem):
        #             content = os.path.join(space, item['space'], 'novel.html')
        #             with open(content, 'w', encoding='utf-8') as meta:
        #                 meta.write(novel_html(item['title'], item['content']))
        #             _databaseItem = DatabaseNovelItem(_databaseItem)
        #             _databaseItem['content'] = item['content']
        #             _databaseItem['path'] = content
        #
        #         _root_space = os.path.dirname(item['space'])
        #         _database = os.path.join(space, _root_space, '%s_main.db' % info.spider.__class__.script_name())
        #         info.spider.space.get(_database).mark_complete(_databaseItem)
        #         info.spider.spider_log.info("Complate : %s-%s-%s" % (item['title'], item['id'], donwalod_space))
