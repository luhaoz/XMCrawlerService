from core import CoreSpider
from scrapy import Spider, Request, FormRequest
import os
from core.runtime import Setting
from scrapy.http.response.html import HtmlResponse
from urllib.parse import urlparse, parse_qs, urlencode
import demjson
from .items import AuthorItem, TaskMetaItem, TaskNovelItem, TaskWorkItem, SourceItem
import demjson
from core.util import list_chunks
from ..pixiv import file_space, novel_format, novel_bind_image
import re


class Script(CoreSpider):
    @classmethod
    def settings(cls):
        return {
            # 'AUTOTHROTTLE_ENABLED': True,
            'CONCURRENT_REQUESTS': 24,
            # 'LOG_LEVEL': 'ERROR',
            # 'LOG_ENABLED': True,
            'FILES_STORE': os.path.join("/", 'data', 'space'),
            'ITEM_PIPELINES': {
                'script.pixiv.pipelines.TaskPipeline': 90
            },
        }

    @classmethod
    def start_requests(cls):
        # _url = 'https://www.pixiv.net/users/154438'
        _url = 'https://www.pixiv.net/users/18638215'
        _cookies = Setting.space("pixiv.runtime").parameter("cookies.json").json()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
            'Accept-Language': 'zh-CN',
        }
        cls._logger.info("Task Url %s" % _url)
        yield Request(url=_url, callback=cls.analysis, headers=headers, cookies=_cookies)

    @classmethod
    def analysis(cls, response: HtmlResponse):
        # print(response.text)
        url = urlparse(response.url)
        id = url.path.replace('/users/', '')
        cls._logger.info("Author Id : %s" % id)
        data_all = 'https://www.pixiv.net/ajax/user/%s/profile/all' % id
        cls._logger.info("Item Url  : %s" % data_all)
        # author_item = AuthorItem()
        _meta_content = response.xpath('//meta[@id="meta-preload-data"]/@content').extract_first()
        _meta = demjson.decode(_meta_content)
        # author_item['id'] = _meta['user'][id]['userId']
        # author_item['name'] = _meta['user'][id]['name']

        _space = cls.settings().get('FILES_STORE')

        yield Request(url=data_all, callback=cls.works, meta={
            "id": id
        })

    @classmethod
    def works(cls, response: HtmlResponse):
        _detail = demjson.decode(response.text)['body']

        _space = cls.settings().get('FILES_STORE')

        illusts = list(_detail['illusts'])
        mangas = list(_detail['manga'])
        novels = list(_detail['novels'])

        cls._logger.info("Illusts    Total :%s" % len(illusts))
        cls._logger.info("Mangas     Total :%s" % len(mangas))
        cls._logger.info("Novels     Total :%s" % len(novels))
        cls._logger.info("ALL        Total :%s" % (len(illusts) + len(mangas) + len(novels)))

        for illust_indexs in list_chunks(list(illusts), 48):
            params = {
                'ids[]': illust_indexs,
                'work_category': 'illust',
                'is_first_page': 0
            }
            work_meta = 'https://www.pixiv.net/ajax/user/%s/profile/illusts?%s' % (
                response.meta['id'],
                urlencode(params, True)
            )
            yield Request(url=work_meta, callback=cls.work_meta, meta=response.meta)

        for manga_indexs in list_chunks(list(mangas), 48):
            params = {
                'ids[]': manga_indexs,
                'work_category': 'manga',
                'is_first_page': 0
            }
            work_meta = 'https://www.pixiv.net/ajax/user/%s/profile/illusts?%s' % (
                response.meta['id'],
                urlencode(params, True)
            )
            yield Request(url=work_meta, callback=cls.work_meta, meta=response.meta)
        for novel_indexs in novels:
            novel_url = 'https://www.pixiv.net/ajax/novel/%s' % novel_indexs

            response.meta['id'] = novel_indexs
            yield Request(url=novel_url, callback=cls.novels_meta, meta=response.meta)

    @classmethod
    def work_meta(cls, response: HtmlResponse):
        work_meta = demjson.decode(response.text)['body']['works']

        for _item in work_meta.values():
            artworks = 'https://www.pixiv.net/ajax/illust/%s' % _item['illustId']
            referer = 'https://www.pixiv.net/artworks/%s' % _item['illustId']
            cls._logger.info("Illust Title :%s" % _item['illustTitle'])
            yield Request(url=artworks, callback=cls.work_detail, meta=response.meta, headers={
                'Referer': referer
            })

    @classmethod
    def work_detail(cls, response: HtmlResponse):
        work_detail = demjson.decode(response.text)['body']
        _work_task_item = TaskWorkItem()
        _work_task_item['id'] = work_detail['illustId']
        _work_task_item['title'] = work_detail['illustTitle']
        _work_task_item['description'] = work_detail['description']
        _work_task_item['upload_date'] = work_detail['uploadDate']
        _work_task_item['count'] = work_detail['pageCount']
        _work_task_item['tags'] = [
            tag['tag']
            for tag in work_detail['tags']['tags']
        ]

        _author_item = AuthorItem()
        _author_item['id'] = work_detail['userId']
        _author_item['name'] = work_detail['userName']

        _work_task_item['author'] = _author_item
        _work_task_item['source'] = SourceItem()
        _work_task_item['space'] = file_space(_work_task_item)
        response.meta['task'] = _work_task_item

        if work_detail['illustType'] == 2:
            _work_task_item['type'] = 'ugoira'
            _work_url = 'https://www.pixiv.net/ajax/illust/%s/ugoira_meta' % work_detail['illustId']
            yield Request(url=_work_url, meta=response.meta, callback=cls.ugoira_source)

        if work_detail['illustType'] != 2:
            _work_task_item['type'] = 'illust'

            _work_url = 'https://www.pixiv.net/ajax/illust/%s/pages' % work_detail['illustId']
            yield Request(url=_work_url, meta=response.meta, callback=cls.illust_source)

    @classmethod
    def illust_source(cls, response: HtmlResponse):
        source_datas = demjson.decode(response.text)['body']
        item = response.meta['task']
        item['source']['sources'] = [
            source['urls']['original']
            for source in source_datas
        ]
        yield item

    @classmethod
    def ugoira_source(cls, response: HtmlResponse):
        source_data = demjson.decode(response.text)['body']
        item = response.meta['task']
        item['source']['sources'] = [
            source_data['originalSrc'],
            source_data['src']
        ]
        yield item

    @classmethod
    def novels_meta(cls, response: HtmlResponse):
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

        source_item = SourceItem()
        source_item['type'] = 'novel'
        source_item['url'] = response.url
        source_item['sources'] = [
            _novel_meta['coverUrl']
        ]
        _work_task_item['source'] = source_item
        _work_task_item['space'] = file_space(_work_task_item)
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
            response.meta['item'] = _work_task_item
            yield Request(url=pixivimage_meta, callback=cls.novels_detail, meta=response.meta, headers=headers)
        else:
            yield _work_task_item

    @classmethod
    def novels_detail(cls, response: HtmlResponse):
        _novel_meta = demjson.decode(response.text)['body']
        _work_task_item = response.meta['item']
        _bind_images = {}
        for id, _detail in _novel_meta.items():
            if _detail['illust'] is not None:
                _bind_images[id] = _detail['illust']['images']['original'].split('/')[-1]
                _work_task_item['source']['sources'].append(_detail['illust']['images']['original'])
        _work_task_item['content'] = novel_bind_image(_work_task_item['content'], _bind_images)
        yield _work_task_item


__script__ = Script
