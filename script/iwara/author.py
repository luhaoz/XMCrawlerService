from core import CoreSpider
from scrapy import Spider, Request, FormRequest
import os
from core.setting import Settings
from scrapy.http.response.html import HtmlResponse
import demjson
from .items import AuthorItem, TaskVideoItem, TaskMetaItem
from urllib.parse import urlparse, parse_qsl
from .persistence import IwaraPersistence
from core.util import md5
import re
import time


class Script(CoreSpider):
    _engine = None

    @classmethod
    def settings(cls):
        return {
            # 'AUTOTHROTTLE_ENABLED': True,
            'CONCURRENT_REQUESTS': 10,
            'LOG_LEVEL': 'DEBUG',
            'LOG_ENABLED': True,
            'FILES_STORE': Settings.namespace("iwara").space("author"),
            # 'DOWNLOADER_MIDDLEWARES': {
            #     'core.pipelines.ProxyMiddleware': 100,
            # },
            'ITEM_PIPELINES': {
                'script.iwara.pipelines.TaskPipeline': 90
            },
        }

    def start_requests(self):
        self.persistence = IwaraPersistence("iwara_space")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
        }

        _cookies = Settings.namespace("iwara").runtime("cookies")
        _users = [
            "delta2018w",
            "Ciel_xxx",
            "erenarin",
            "黑叶冥",
            "xiaodidi09",
            "deepkiss",
            "aniMMage",
            "StrangerMMD",

        ]

        for _user in _users:
            _url = "https://ecchi.iwara.tv/users/%s/videos" % _user
            yield Request(url=_url, callback=self.authors, cookies=_cookies, headers=headers)
            break

        # _following = "https://ecchi.iwara.tv/users/luhaoz/following"
        # yield Request(url=_following, callback=cls.following, cookies=_cookies, headers=headers)

    def following(self, response: HtmlResponse):
        _users = response.xpath('//*[contains(@class,"username")]/@href').extract()
        for _user in _users:
            _user_url = "https://ecchi.iwara.tv%s" % _user
            yield Request(url=_user_url, callback=self.authors)

        _next_page = response.xpath('//*[contains(@class,"pager-next")]/a/@href').extract_first()
        if _next_page is not None:
            _user_next_url = "https://ecchi.iwara.tv%s" % _next_page
            yield Request(url=_user_next_url, callback=self.following)

    def authors(self, response: HtmlResponse):
        # print(response.text)
        _nodes_element = response.xpath('//*[contains(@class,"node-video")]')
        _works = []
        for _item in _nodes_element:
            _has_public = _item.xpath('.//*[contains(@class,"private-video")]').extract_first() is None
            if _has_public is False:
                continue
            _id = _item.xpath(".//h3/a/@href").extract_first().replace("/videos/", "")
            _works.append(_id)
        _diff_ids = self.persistence.filter(_works, "video")

        for _id in _diff_ids:
            print(_id)
            _item_url = "https://ecchi.iwara.tv/videos/%s" % _id
            print(_item_url)
            yield Request(url=_item_url, callback=self.detail)

        _next_page = response.xpath('//*[contains(@class,"pager-next")]/a/@href').extract_first()
        if _next_page is not None:
            _url = "https://ecchi.iwara.tv%s" % _next_page
            yield Request(url=_url, callback=self.authors)

    def detail(self, response: HtmlResponse):
        _urlparse = urlparse(response.url)
        # print(_urlparse
        _api_url = "https://ecchi.iwara.tv/api%s" % _urlparse.path.replace("videos", "video")
        _id = _urlparse.path.replace("/videos/", "")
        _item = TaskVideoItem()

        _author = AuthorItem()

        _author['name'] = response.xpath('//a[contains(@class,"username")]/text()').extract_first()
        _author['id'] = md5(_author['name'])

        _item['id'] = _id
        _item['author'] = _author
        _item['title'] = response.xpath('//h1[contains(@class,"title")]/text()').extract_first()
        _description = response.xpath("//*[contains(@class,'field-name-body')]//text()").extract()
        _item['description'] = "".join(_description)
        _text = response.xpath("//*[contains(@class,'node-info')]//*[contains(@class,'submitted')]/text()").extract()
        _search = re.search(r"在([0-9-: ]*)提交", "".join(_text))
        _item['upload_date'] = _date = _search.group(1).strip()
        _item['type'] = "video"

        yield Request(url=_api_url, callback=self.resource, headers={
            "Referer": 'https://ecchi.iwara.tv%s' % _urlparse.path
        }, meta={
            "item": _item
        })

    def resource(self, response: HtmlResponse):
        _sources = demjson.decode(response.text)
        _item = response.meta['item']
        for _source in _sources:
            if _source['resolution'] == 'Source':
                _resource_url = "https:%s" % _source['uri']
                # # _file_item['url'] = "https:%s" % _source['uri']
                # #
                # _parse = urlparse(_resource_url)
                # _query = dict(parse_qsl(_parse.query))
                #
                # _file = "%s%s" % (_item['title'], os.path.splitext(_query['file'])[-1])
                # print(_file)
                #
                # _file_item['file'] = "%s%s" % (_item['title'], os.path.splitext(_query['file'])[-1])
                _item['sources'].append(_resource_url)

        yield _item


__script__ = Script
