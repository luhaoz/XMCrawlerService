from core import CoreSpider
from scrapy import Request
from scrapy.http.response.html import HtmlResponse
from scrapy import Spider, Request, FormRequest


class Script(Spider):
    name = 'test'

    @classmethod
    def settings(cls):
        return {
            'AUTOTHROTTLE_ENABLED': True,
            'CONCURRENT_REQUESTS': 24,
            'LOG_LEVEL': 'ERROR',
            'LOG_ENABLED': True,
            'FILES_STORE': 'N:\\pixiv\\space\\author',
            'DOWNLOADER_MIDDLEWARES': {
                # 'script.pixiv.pipelines.ProxyPipeline': 350,
                # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
                # 'app.pixiv.core.pipelines.DuplicatesPipeline': 90
                # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1,
                # 'app.pixiv.pipelines.HttpbinProxyMiddleware': 2,
            },
            'ITEM_PIPELINES': {
                # 'script.pixiv.pipelines.TaskPipeline': 90
            },
        }

    @classmethod
    def start_requests(cls):
        pass
        yield Request(url='https://www.pixiv.net/', callback=cls.analysis)

    @classmethod
    def analysis(cls, response: HtmlResponse):
        print(response.status)


__script__ = Script
