# -*- mode: python -*-
from scrapy.pipelines.files import FileException, FilesPipeline
from .items import AuthorItem, TaskMetaItem, TaskNovelItem
from scrapy.pipelines.media import MediaPipeline
from scrapy import Request
import os
from scrapy.exceptions import DropItem
import demjson
from ..pixiv import novel_html
from core import CoreSpider
import time
from core.pipelines import CacheZipFilesPipeline, CacheZipPool
from .utils import Space, Novel
from core.ziputil import ZipUtil
from zipfile import ZipFile, ZIP_LZMA


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "http://host.docker.internal:10809"


class TaskPipeline(CacheZipFilesPipeline):
    def get_media_requests(self, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        _spider.logger.info("Item : %s" % item)

        for resource in item['sources']:
            yield Request(resource, meta={
                'item': item,
                'resource': resource
            }, headers={
                'Referer': 'https://www.pixiv.net/artworks/%s' % item['id']
            })

    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta['item']
        resource = request.meta['resource']
        resource_path = os.path.join(
            Space.space(item),
            resource.split('/')[-1]
        )
        return resource_path

    def __completed(self, results, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _package_path = "%s.zip" % Space.space(item)
        _spider: CoreSpider = info.spider

        _meta = item
        _meta_data = demjson.encode(dict(_meta), encoding="utf-8", compactly=False, indent_amount=4)

        space = info.spider.settings.get('FILES_STORE')

        _space = os.path.join(space, _package_path)
        donwalod_space = os.path.abspath(_space)
        _cache_zip = CacheZipPool.use(_space)
        with ZipFile(_cache_zip, 'a') as _zip_file:
            if isinstance(item, TaskNovelItem):
                _zip_file.writestr("novel.html", novel_html(item['title'], item['content']))
            _zip_file.writestr("work.json", _meta_data)

        with open(donwalod_space, 'wb') as _save_file:
            _save_file.write(_cache_zip.getvalue())
            CacheZipPool.remove(_space)
        # last = 10
        # while zipfile.is_zipfile(donwalod_space) is False:
        #     print("%s is no zip " % donwalod_space)
        #     time.sleep(1)
        #     last -= 1
        #     if last <= 0:
        #         raise DropItem("Error : %s-%s" % (item['title'], item['id']))
        #
        # with ZipUtil(donwalod_space) as _zip_file:
        #     if isinstance(item, TaskNovelItem):
        #         _zip_file.replace("novel.html", novel_html(item['title'], item['content']))
        #     _zip_file.replace("work.json", _meta_data)
        #     _spider.logger.info("ZIP File : %s-Test" % donwalod_space)
        _spider.persistence.save(item)
        return _spider.logger.info("Complate : %s-%s-%s" % (item['title'], item['id'], donwalod_space))

    def item_completed(self, results, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
        _spider: CoreSpider = info.spider
        for ok, result in results:
            if ok is False:
                _spider.logger.error("Error : %s-%s" % (item['title'], item['id']))
                raise DropItem("Error : %s-%s" % (item['title'], item['id']))
        self.__completed(results, item, info)
        # threads.deferToThread(self.__completed, results, item, info)

#
# class TaskPipeline2(FilesPipeline):
#     _engine = None
#
#     def open_spider(self, spider):
#         self._engine = DatabaseUtil.init("pixiv_space")
#         super().open_spider(spider)
#
#     def get_media_requests(self, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
#         _spider: CoreSpider = info.spider
#         _spider._logger.info("Item : %s" % item)
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
#     def item_completed(self, results, item: TaskMetaItem, info: MediaPipeline.SpiderInfo):
#
#         # print(results)
#         _spider: CoreSpider = info.spider
#         for ok, result in results:
#             if ok is False:
#                 _spider._logger.error("Error : %s-%s" % (item['title'], item['id']))
#                 raise DropItem("Error : %s-%s" % (item['title'], item['id']))
#
#         space = info.spider.settings.get('FILES_STORE')
#         os.makedirs(os.path.join(space, item['space']), exist_ok=True)
#         donwalod_space = os.path.join(space, item['space'], 'work.json')
#
#         _meta = item
#         with open(donwalod_space, 'wb') as meta:
#             meta.write(demjson.encode(dict(_meta), encoding="utf-8", compactly=False, indent_amount=4))
#
#         if isinstance(item, TaskNovelItem):
#             content = os.path.join(space, item['space'], 'novel.html')
#             with open(content, 'w', encoding='utf-8') as meta:
#                 meta.write(novel_html(item['title'], item['content']))
#
#         with self._engine.connect() as _connect:
#             # author
#             insert_session = insert(AuthorTable).values(
#                 primary="author_%s" % item['author']['id'],
#                 id=item['author']['id'],
#                 name=item['author']['name']
#             )
#             duplicate_key_session = insert_session.on_duplicate_key_update(
#                 is_del=False,
#             )
#             _connect.execute(duplicate_key_session)
#
#             # works
#             _time = time.mktime(
#                 time.strptime(item['upload_date'].replace("T", " ").replace("+00:00", ""), "%Y-%m-%d %H:%M:%S"))
#             insert_session = insert(WorkTable).values(
#                 primary="works_%s" % item['id'],
#                 id=item['id'],
#                 name=item['title'],
#                 author_id=item['author']['id'],
#                 description=item['description'],
#                 upload_date=_time,
#                 count=item['count'],
#                 type=item['type']
#             )
#             duplicate_key_session = insert_session.on_duplicate_key_update(
#                 is_del=False,
#                 upload_date=_time,
#             )
#             _connect.execute(duplicate_key_session)
#             # tags
#             for _tag_name in item['tags']:
#                 insert_session = insert(TagTable).values(
#                     primary="tags_%s_%s" % (item['id'], md5(_tag_name)),
#                     id=md5(_tag_name),
#                     work_id=item['id'],
#                     name=_tag_name,
#                 )
#                 duplicate_key_session = insert_session.on_duplicate_key_update(
#                     is_del=False,
#                 )
#                 _connect.execute(duplicate_key_session)
#
#             # illusts
#             for _resource in item['source']['sources']:
#                 insert_session = insert(IllustTable).values(
#                     primary="illust_%s_%s" % (item['id'], md5(_resource)),
#                     id=md5(_resource),
#                     work_id=item['id'],
#                     source=_resource,
#                     path=os.path.join(
#                         item['space'],
#                         _resource.split('/')[-1]
#                     )
#                 )
#                 duplicate_key_session = insert_session.on_duplicate_key_update(
#                     is_del=False,
#                 )
#                 _connect.execute(duplicate_key_session)
#
#             if isinstance(item, TaskNovelItem):
#                 content = os.path.join(space, item['space'], 'novel.html')
#                 with open(content, 'w', encoding='utf-8') as meta:
#                     meta.write(novel_html(item['title'], item['content']))
#
#                 insert_session = insert(NovelTable).values(
#                     primary="novel_%s" % item['id'],
#                     id=item['id'],
#                     work_id=item['id'],
#                     content=item['content'],
#                     path=os.path.join(
#                         item['space'],
#                         'novel.html'
#                     )
#                 )
#                 duplicate_key_session = insert_session.on_duplicate_key_update(
#                     is_del=False,
#                 )
#                 _connect.execute(duplicate_key_session)
#
#         _spider._logger.info("Complate : %s-%s-%s" % (item['title'], item['id'], donwalod_space))
