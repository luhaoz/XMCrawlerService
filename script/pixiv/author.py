from core import CoreSpider
from scrapy import Spider, Request, FormRequest
import os
from core.runtime import Setting
from scrapy.http.response.html import HtmlResponse
from urllib.parse import urlparse, parse_qs, urlencode
import demjson
from .items import AuthorItem, TaskMetaItem, TaskNovelItem
import demjson

class Script(CoreSpider):
    @classmethod
    def settings(cls):
        return {
            # 'AUTOTHROTTLE_ENABLED': True,
            'CONCURRENT_REQUESTS': 24,
            'LOG_LEVEL': 'ERROR',
            'LOG_ENABLED': True,
            'FILES_STORE': os.path.join("/", 'data', 'space'),
            'ITEM_PIPELINES': {
                # 'script.pixiv.pipelines.TaskPipeline': 90
            },
        }

    @classmethod
    def start_requests(cls):
        _url = 'https://www.pixiv.net/users/154438'
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
        author_item = AuthorItem()
        _meta_content = response.xpath('//meta[@id="meta-preload-data"]/@content').extract_first()
        _meta = demjson.decode(_meta_content)
        author_item['id'] = _meta['user'][id]['userId']
        author_item['name'] = _meta['user'][id]['name']

        _space = cls.settings().get('FILES_STORE')

        yield Request(url=data_all, callback=cls.works, meta={
            "id": id,
            "author": author_item
        })

    @classmethod
    def works(cls, response: HtmlResponse):
        _detail = demjson.decode(response.text)

        _space = cls.settings().get('FILES_STORE')

        illusts = list(_detail['body']['illusts'])
        mangas = list(_detail['body']['manga'])
        novels = list(_detail['body']['novels'])

        cls._logger.info("Illusts    Total :%s" % len(illusts))
        cls._logger.info("Mangas     Total :%s" % len(mangas))
        cls._logger.info("Novels     Total :%s" % len(novels))
        cls._logger.info("ALL        Total :%s" % (len(illusts) + len(mangas) + len(novels)))


__script__ = Script
