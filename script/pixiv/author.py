from core import CoreSpider
from scrapy import Spider, Request, FormRequest
import os
from core.setting import Settings
from scrapy.http.response.html import HtmlResponse
from urllib.parse import urlparse, parse_qsl, urlencode
import demjson
from .items import AuthorItem, TaskMetaItem, TaskNovelItem, TaskIllustItem
import demjson
from core.util import list_chunks
from ..pixiv import file_space, novel_format, novel_bind_image, Runtime
import re
import math
from .persistence import PixivPersistence


class Script(CoreSpider):
    _engine = None

    @classmethod
    def settings(cls):
        return {
            # 'AUTOTHROTTLE_ENABLED': True,
            'CONCURRENT_REQUESTS': 10,
            'LOG_LEVEL': 'DEBUG',

            'LOG_ENABLED': True,
            'FILES_STORE': Settings.namespace("pixiv").space("author"),
            'DOWNLOADER_MIDDLEWARES': {
                'core.pipelines.ProxyMiddleware': 100,
            },
            'ITEM_PIPELINES': {
                'script.pixiv.pipelines.TaskPipeline': 90
            },
        }

    def start_requests(self):
        self.persistence = PixivPersistence("pixiv_space")
        # cls._engine = DatabaseUtil.init("pixiv_space")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Accept-Language': 'zh-CN',
        }
        # print("qe")

        # _cookies = Setting.space("pixiv.runtime").parameter("cookies.json").json()
        _cookies = Settings.namespace("pixiv").runtime("cookies")
        #
        urls = [
            'https://www.pixiv.net/users/45847523',
            'https://www.pixiv.net/users/20037523',
            'https://www.pixiv.net/users/6916534',
            'https://www.pixiv.net/users/19295557',
            'https://www.pixiv.net/users/17918526',
            'https://www.pixiv.net/users/30853870',
            'https://www.pixiv.net/users/40739400',
            'https://www.pixiv.net/users/2078727',
            'https://www.pixiv.net/users/29537',
            'https://www.pixiv.net/users/53812',
            'https://www.pixiv.net/users/3741778',
            'https://www.pixiv.net/users/16058450',
            'https://www.pixiv.net/users/580728',
            'https://www.pixiv.net/users/580728',
            'https://www.pixiv.net/users/2023765',
            'https://www.pixiv.net/users/19245146',
            'https://www.pixiv.net/users/5037083',
            'https://www.pixiv.net/users/84752',
            'https://www.pixiv.net/users/4213659',
            'https://www.pixiv.net/users/1793667',
            'https://www.pixiv.net/users/17922136',
            'https://www.pixiv.net/users/4383806',
            'https://www.pixiv.net/users/31084738',
            'https://www.pixiv.net/users/4635235',
            'https://www.pixiv.net/users/39887185',
            'https://www.pixiv.net/users/35825050',
            'https://www.pixiv.net/users/35825050',
            'https://www.pixiv.net/users/16712573',
            'https://www.pixiv.net/users/1285568',
            'https://www.pixiv.net/users/6289657',
            'https://www.pixiv.net/users/671225',
            'https://www.pixiv.net/users/1412853',
            'https://www.pixiv.net/users/361705',
            'https://www.pixiv.net/users/45168768',
            'https://www.pixiv.net/users/16186617',
            'https://www.pixiv.net/users/680161',
            'https://www.pixiv.net/users/343981',
            'https://www.pixiv.net/users/5397444',
            'https://www.pixiv.net/users/4042011',
            'https://www.pixiv.net/users/16274829',
            'https://www.pixiv.net/users/45847523',
            'https://www.pixiv.net/users/28617557',
            'https://www.pixiv.net/users/6916534',
            'https://www.pixiv.net/users/471249',
            'https://www.pixiv.net/users/24414324',
            'https://www.pixiv.net/users/687125',
            'https://www.pixiv.net/users/15436076',
            'https://www.pixiv.net/users/14440528',
            'https://www.pixiv.net/users/8969258',
            'https://www.pixiv.net/users/17801188',
            'https://www.pixiv.net/users/45847523',
            'https://www.pixiv.net/users/11022194',
            'https://www.pixiv.net/users/18261283',
            'https://www.pixiv.net/users/26495687',
            'https://www.pixiv.net/users/8587823',
            'https://www.pixiv.net/users/18638215'
        ]

        for _url in urls:
            self.logger.info("Task Url %s" % _url)
            # cls._logger.info("Task Url %s" % _url)
            yield Request(url=_url, callback=self.analysis, headers=headers, cookies=_cookies)

        _user = 25013373
        _authors = "https://www.pixiv.net/ajax/user/%s/following?offset=0&limit=24&rest=show&tag=&lang=zh" % _user
        headers['Referer'] = 'https://www.pixiv.net/users/%s/following' % _user
        yield Request(url=_authors, callback=self.authors, headers=headers, cookies=_cookies, meta={
            "follow_user": _user
        })

    def authors(self, response: HtmlResponse):
        _detail = demjson.decode(response.text)['body']
        _total = int(_detail['total'])
        _page_count = math.ceil(_total / 24)
        for _index in range(1, _page_count):
            _offset = _index * 24
            _author_page = "https://www.pixiv.net/ajax/user/%s/following?offset=%s&limit=24&rest=show&tag=&lang=zh" % (response.meta['follow_user'], _offset)
            yield Request(url=_author_page, callback=self.author_work, meta=response.meta)

    def author_work(self, response: HtmlResponse):
        _detail = demjson.decode(response.text)['body']
        for _user in _detail['users']:
            _work = 'https://www.pixiv.net/users/%s' % _user['userId']
            self.logger.info("Task Url %s" % _work)
            yield Request(url=_work, callback=self.analysis, meta=response.meta)

    def analysis(self, response: HtmlResponse):
        url = urlparse(response.url)
        id = url.path.replace('/users/', '')
        self.logger.info("Author Id : %s" % id)
        data_all = 'https://www.pixiv.net/ajax/user/%s/profile/all' % id
        self.logger.info("Item Url  : %s" % data_all)
        _meta_content = response.xpath('//meta[@id="meta-preload-data"]/@content').extract_first()
        _meta = demjson.decode(_meta_content)
        yield Request(url=data_all, callback=self.works, meta={
            "id": id
        })

    def works(self, response: HtmlResponse):
        _detail = demjson.decode(response.text)['body']

        # _space = cls.settings().get('FILES_STORE')

        illusts = list(_detail['illusts'])
        mangas = list(_detail['manga'])
        novels = list(_detail['novels'])

        self.logger.info("Illusts    Total :%s" % len(illusts))
        self.logger.info("Mangas     Total :%s" % len(mangas))
        self.logger.info("Novels     Total :%s" % len(novels))
        self.logger.info("ALL        Total :%s" % (len(illusts) + len(mangas) + len(novels)))

        # _diff_illusts = set(illusts)
        # _diff_mangas = set(mangas)
        # _diff_novels = set(novels)

        _diff_illusts = self.persistence.filter(illusts, 'illust')
        _diff_mangas = self.persistence.filter(mangas, 'illust')
        _diff_novels = self.persistence.filter(novels, 'novel')

        # print(_illusts_ids)
        # print(_mangas_ids)
        # print(_novels_ids)

        # self.persistence.

        # with cls._engine.connect() as _connect:
        #     _has = select([WorkTable.columns.id]).where(WorkTable.columns.id.in_(illusts)).where(WorkTable.columns.is_del == 0).where(WorkTable.columns.type == "illust")
        #     _data = _connect.execute(_has)
        #     _diff_illusts = set(illusts).difference([item[0] for item in _data])
        #     cls._logger.info("Illusts  Skip  Total :%s" % _diff_illusts)
        #
        # with cls._engine.connect() as _connect:
        #     _has = select([WorkTable.columns.id]).where(WorkTable.columns.id.in_(mangas)).where(WorkTable.columns.is_del == 0).where(WorkTable.columns.type == "illust")
        #     _data = _connect.execute(_has)
        #     _diff_mangas = set(mangas).difference([item[0] for item in _data])
        #
        #     cls._logger.info("Mangas  Skip    Total :%s" % mangas)
        #
        # with cls._engine.connect() as _connect:
        #     _has = select([WorkTable.columns.id]).where(WorkTable.columns.id.in_(novels)).where(WorkTable.columns.is_del == 0).where(WorkTable.columns.type == "novel")
        #     _data = _connect.execute(_has)
        #     _diff_novels = set(novels).difference([item[0] for item in _data])
        #
        #     cls._logger.info("Novels   Skip  Total :%s" % _diff_novels)

        for illust_indexs in list_chunks(list(_diff_illusts), 48):
            params = {
                'ids[]': illust_indexs,
                'work_category': 'illust',
                'is_first_page': 0
            }
            work_meta = 'https://www.pixiv.net/ajax/user/%s/profile/illusts?%s' % (
                response.meta['id'],
                urlencode(params, True)
            )
            yield Request(url=work_meta, callback=self.work_meta, meta=response.meta)
            
        for manga_indexs in list_chunks(list(_diff_mangas), 48):
            params = {
                'ids[]': manga_indexs,
                'work_category': 'manga',
                'is_first_page': 0
            }
            work_meta = 'https://www.pixiv.net/ajax/user/%s/profile/illusts?%s' % (
                response.meta['id'],
                urlencode(params, True)
            )
            yield Request(url=work_meta, callback=self.work_meta, meta=response.meta)
            

        for novel_indexs in _diff_novels:
            novel_url = 'https://www.pixiv.net/ajax/novel/%s' % novel_indexs

            response.meta['id'] = novel_indexs
            yield Request(url=novel_url, callback=self.novels_meta, meta=response.meta)
            

    def work_meta(self, response: HtmlResponse):
        work_meta = demjson.decode(response.text)['body']['works']

        for _item in work_meta.values():
            artworks = 'https://www.pixiv.net/ajax/illust/%s' % _item['id']
            referer = 'https://www.pixiv.net/artworks/%s' % _item['id']
            self.logger.info("Illust Title :%s" % _item['title'])
            yield Request(url=artworks, callback=self.work_detail, meta=response.meta, headers={
                'Referer': referer
            })

    #
    def work_detail(self, response: HtmlResponse):
        work_detail = demjson.decode(response.text)['body']
        _work_task_item = TaskIllustItem()
        _work_task_item['id'] = work_detail['illustId']
        _work_task_item['title'] = work_detail['illustTitle']
        _work_task_item['description'] = work_detail['description']
        _work_task_item['upload_date'] = work_detail['uploadDate']
        _work_task_item['count'] = work_detail['pageCount']
        _work_task_item['tags'] = [
            tag['tag']
            for tag in work_detail['tags']['tags']
        ]
        #
        _author_item = AuthorItem()
        _author_item['id'] = work_detail['userId']
        _author_item['name'] = work_detail['userName']

        _work_task_item['author'] = _author_item

        # self.logger.info(_work_task_item)
        # print(_work_task_item['sources'])

        # _work_task_item['source'] = SourceItem()
        # _work_task_item['space'] = file_space(_work_task_item)
        response.meta['task'] = _work_task_item
        #
        if work_detail['illustType'] == 2:
            _work_task_item['type'] = 'ugoira'
            _work_url = 'https://www.pixiv.net/ajax/illust/%s/ugoira_meta' % work_detail['illustId']
            yield Request(url=_work_url, meta=response.meta, callback=self.ugoira_source)

        if work_detail['illustType'] != 2:
            _work_task_item['type'] = 'illust'

            _work_url = 'https://www.pixiv.net/ajax/illust/%s/pages' % work_detail['illustId']
            yield Request(url=_work_url, meta=response.meta, callback=self.illust_source)

    #
    def illust_source(self, response: HtmlResponse):
        source_datas = demjson.decode(response.text)['body']
        item = response.meta['task']
        item['sources'] = [
            source['urls']['original']
            for source in source_datas
        ]
        yield item

    #
    def ugoira_source(self, response: HtmlResponse):
        source_data = demjson.decode(response.text)['body']
        item = response.meta['task']
        item['sources'] = [
            source_data['originalSrc'],
            source_data['src']
        ]
        yield item

    #
    def novels_meta(self, response: HtmlResponse):
        _novel_meta = demjson.decode(response.text)['body']
        _author_item = AuthorItem()
        _author_item['id'] = _novel_meta['userId']
        _author_item['name'] = _novel_meta['userName']

        _work_task_item = TaskNovelItem()
        _work_task_item['id'] = _novel_meta['id']
        _work_task_item['title'] = _novel_meta['title']
        _work_task_item['description'] = _novel_meta['description']
        _work_task_item['author'] = _author_item
        _work_task_item['content'] = novel_format(_novel_meta['content'])
        _work_task_item['upload_date'] = _novel_meta['uploadDate']
        _work_task_item['count'] = 1
        _work_task_item['type'] = 'novel'
        _work_task_item['tags'] = [
            tag['tag']
            for tag in _novel_meta['tags']['tags']
        ]

        _work_task_item['sources'] = [
            _novel_meta['coverUrl']
        ]

        _search_pixiv_images = re.search(r'\[pixivimage:(.*?)\]', _novel_meta['content'], re.M | re.I)
        if _search_pixiv_images is not None:
            params = {
                'id[]': _search_pixiv_images.groups(),
                'lang': 'zh'
            }
            pixivimage_meta = 'https://www.pixiv.net/ajax/novel/%s/insert_illusts?%s' % (
                _novel_meta['id'],
                urlencode(params, True)
            )
            headers = {
                'referer': 'https://www.pixiv.net/novel/show.php?id=%s' % _novel_meta['id']
            }
            response.meta['task'] = _work_task_item
            yield Request(url=pixivimage_meta, callback=self.novels_detail, meta=response.meta, headers=headers)
        else:
            yield _work_task_item
        # self.logger.info(_work_task_item)
        # source_item = SourceItem()
        # source_item['type'] = 'novel'
        # source_item['url'] = response.url
        # source_item['sources'] = [
        #     _novel_meta['coverUrl']
        # ]
        # _work_task_item['source'] = source_item
        # _work_task_item['space'] = file_space(_work_task_item)
        # _search_pixiv_images = re.search(r'\[pixivimage:(.*?)\]', _novel_meta['content'], re.M | re.I)
        # if _search_pixiv_images is not None:
        #     params = {
        #         'id[]': _search_pixiv_images.groups(),
        #         'lang': 'zh'
        #     }
        #     pixivimage_meta = 'https://www.pixiv.net/ajax/novel/%s/insert_illusts?%s' % (
        #         _novel_meta['id'],
        #         urlencode(params, True)
        #     )
        #     headers = {
        #         'referer': 'https://www.pixiv.net/novel/show.php?id=%s' % _novel_meta['id']
        #     }
        #     response.meta['item'] = _work_task_item
        #     yield Request(url=pixivimage_meta, callback=self.novels_detail, meta=response.meta, headers=headers)
        # else:
        #     yield _work_task_item

    #
    # @classmethod
    def novels_detail(self, response: HtmlResponse):
        _novel_meta = demjson.decode(response.text)['body']
        _work_task_item = response.meta['task']
        _bind_images = {}
        for id, _detail in _novel_meta.items():
            if _detail['illust'] is not None:
                _bind_images[id] = _detail['illust']['images']['original'].split('/')[-1]
                _work_task_item['sources'].append(_detail['illust']['images']['original'])
        _work_task_item['content'] = novel_bind_image(_work_task_item['content'], _bind_images)
        yield _work_task_item


__script__ = Script
