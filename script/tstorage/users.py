from core import CoreSpider
from scrapy import Spider, Request, FormRequest
import os
from scrapy.http.response.html import HtmlResponse
import demjson
from .items import AuthorItem, TaskWorkItem, TstorageSourceItem
from . import Runtime
import re
import math
from core.setting import Settings


class Script(CoreSpider):
    _engine = None

    @classmethod
    def settings(cls):
        return {
            # https://www.pixiv.net/users/46811099
            # 'AUTOTHROTTLE_ENABLED': True,
            'MEDIA_ALLOW_REDIRECTS': True,
            'CONCURRENT_REQUESTS': 50,
            'DOWNLOAD_FAIL_ON_DATALOSS': False,
            # 'LOG_LEVEL': 'ERROR',

            # 'LOG_ENABLED': True,
            'FILES_STORE': Settings.namespace("tstorages").space("users"),
            # 'DOWNLOADER_MIDDLEWARES': {
            #     'script.fanbox.pipelines.ProxyMiddleware': 100,
            # },
            'ITEM_PIPELINES': {
                'script.tstorage.pipelines.TaskPipeline': 90
            },
        }

    @classmethod
    def start_requests(cls):
        # cls._engine = DatabaseUtil.init("pixiv_space")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
            # 'Accept-Language': 'zh-CN',
            # 'origin': 'https://www.fanbox.cc',
            # 'referer': 'https://www.fanbox.cc/creators/supporting'
        }

        _users = [
            'http://tstorage.info/users/_Blob_',
            'http://tstorage.info/users/Jim944',
            'http://tstorage.info/users/MrJinSenpai',
            'http://tstorage.info/users/mmdlinuxdx',
            "http://tstorage.info/users/bigrussiantrap"
        ]

        for _user in _users:
            yield Request(url=_user, callback=cls.main_page, headers=headers)

    @classmethod
    def main_page(cls, response: HtmlResponse):
        pass

        page_data = re.search(r'setPagination\([\s\S]*({[\s\S]*})\)', response.text)
        page_data = demjson.decode(page_data.group(1))
        page_count = math.ceil(int(page_data['total']) / int(page_data['perpage']))
        for page in range(1, page_count + 1):
            yield FormRequest(
                url=response.url,
                formdata={
                    'op': page_data['op'],
                    'load_files_list': page_data['load_files_list'],
                    'page': str(page),
                    'fld_id': '',
                    'usr_login': page_data['usr_login'],
                    'token': page_data['token'],
                },
                callback=cls.analysis
            )

    @classmethod
    def analysis(cls, response: HtmlResponse):
        links = response.xpath("//div[@class='link']/a")
        for link in links:
            url = link.xpath(".//@href").extract_first()
            # print(url)
            meta = {
                "title": link.xpath('.//text()').extract_first()
            }
            yield Request(url=url, meta=meta, callback=cls.download_page)

    @classmethod
    def download_page(cls, response: HtmlResponse):
        _tabcontent = response.xpath('//*[@class="tabcontent"]//textarea//a')
        _tstorageSourceItem = TstorageSourceItem()
        _forms = response.xpath("//form//input")
        for _item in _forms:
            _item_name = _item.xpath('./@name').extract_first()
            _item_value = _item.xpath('./@value').extract_first()
            _tstorageSourceItem[_item_name] = _item_value

        _href = _tabcontent.xpath("./@href").extract_first()
        _name_value = _tabcontent.xpath("./text()").extract_first()
        _name_temp = re.search(r'(.*) - (\d*)', _name_value)
        _name = _name_temp.group(1)
        _file_name = "%s%s" % ("-".join([
            os.path.splitext(_name)[0],
            _name_temp.group(2),
            _tstorageSourceItem['id'],
        ]), os.path.splitext(_name)[-1])

        _tstorageSourceItem['url'] = response.url
        _tstorageSourceItem['file'] = _file_name
        yield _tstorageSourceItem


__script__ = Script
