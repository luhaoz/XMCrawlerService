from core import CoreSpider
from scrapy import Spider, Request, FormRequest
import os
from core.setting import Settings
from scrapy.http.response.html import HtmlResponse
from .items import TaskMetaItem


class Script(CoreSpider):
    _engine = None

    @classmethod
    def settings(cls):
        return {
            # 'AUTOTHROTTLE_ENABLED': True,
            'CONCURRENT_REQUESTS': 30,
            # 'LOG_LEVEL': 'ERROR',
            'REDIRECT_ENABLED ': True,
            'LOG_ENABLED': True,
            'FILES_STORE': Settings.namespace("dlsite").space("products"),
            'DOWNLOADER_MIDDLEWARES': {
                'core.pipelines.ProxyMiddleware': 100,
            },
            'ITEM_PIPELINES': {
                'script.dlsite.pipelines.TaskPipeline': 90
            },
        }

    def start_requests(self):
        # self.persistence = PixivPersistence("pixiv_space")
        # cls._engine = DatabaseUtil.init("pixiv_space")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Accept-Language': 'zh-CN',
        }
        # print("qe")

        # _cookies = Setting.space("pixiv.runtime").parameter("cookies.json").json()
        _cookies = Settings.namespace("dlsite").runtime("cookies")
        #
        urls = [
            'https://www.dlsite.com/maniax/campaign/listen-asmr2101?genrekey=listenasmr202101',
            'https://www.dlsite.com/maniax/campaign/listen-asmr2101?page=2&genrekey=listenasmr202101#search_result_list'
        ]

        for _url in urls:
            self.logger.info("Task Url %s" % _url)
            # cls._logger.info("Task Url %s" % _url)
            yield Request(url=_url, callback=self.analysis, headers=headers, cookies=_cookies)

        # _user = 25013373
        # _authors = "https://www.pixiv.net/ajax/user/%s/following?offset=0&limit=24&rest=show&tag=&lang=zh" % _user
        # headers['Referer'] = 'https://www.pixiv.net/users/%s/following' % _user
        # yield Request(url=_authors, callback=cls.authors, headers=headers, cookies=_cookies, meta={
        #     "follow_user": _user
        # })

    # def authors(cls, response: HtmlResponse):
    #     _detail = demjson.decode(response.text)['body']
    #     _total = int(_detail['total'])
    #     _page_count = math.ceil(_total / 24)
    #     for _index in range(1, _page_count):
    #         _offset = _index * 24
    #         _author_page = "https://www.pixiv.net/ajax/user/%s/following?offset=%s&limit=24&rest=show&tag=&lang=zh" % (response.meta['follow_user'], _offset)
    #         yield Request(url=_author_page, callback=cls.author_work, meta=response.meta)
    #
    # def author_work(cls, response: HtmlResponse):
    #     _detail = demjson.decode(response.text)['body']
    #     for _user in _detail['users']:
    #         _work = 'https://www.pixiv.net/users/%s' % _user['userId']
    #         cls._logger.info("Task Url %s" % _work)
    #         yield Request(url=_work, callback=cls.analysis, meta=response.meta)

    def analysis(self, response: HtmlResponse):
        pass
        _products = response.xpath('//ul[@data-product_id]')

        limit = 3
        for _product in _products:
            _id = _product.xpath("./@data-product_id").extract_first()

            _url = "https://play.dlsite.com/?workno=%s" % _id
            # _url = "http://play.dlsite.com/#/work/%s" % _id
            response.meta['product_id'] = _id
            yield Request(url=_url, callback=self.work, meta=response.meta, dont_filter=True)

            # print(_url)
            # if limit <= 0:
            #     break
            #
            # limit -= 1

            # _href = _product.xpath("./@href").extract_first()
            # print(_product)

            # break

    def work(self, response: HtmlResponse):
        # pass
        # _title = response.xpath('//div[@class="workinfo"]').extract_first()
        # print(_title)
        # https://play.dlsite.com/api/download_token?workno=RJ313412
        # print(response.text)
        _url = "https://play.dlsite.com/api/download_token?workno=%s" % response.meta['product_id']
        print(_url)

        yield Request(url=_url, callback=self.download_wrok, meta=response.meta)

    def download_wrok(self, response: HtmlResponse):
        _json = response.json()
        # print(_json)
        _token = _json['params']
        _url = "%sziptree.json?token=%s&expiration=%s" % (_json['url'], _token['token'], _token['expiration'])
        response.meta['token'] = _json
        yield Request(url=_url, callback=self.download_detail, meta=response.meta)

    def download_detail(self, response: HtmlResponse):
        _json = response.json()
        # print(_json)
        _token = response.meta['token']

        def _childrens(_children_datas, path=""):
            for _children in _children_datas:
                print(_children)
                if _children["type"] == "folder":
                    yield from _childrens(_children['children'], os.path.join(path, _children['path']))

                if _children["type"] == "file":
                    _item = TaskMetaItem()
                    _item['id'] = response.meta['product_id']
                    _children['hashname'] = _children['hashname'].replace(".wav", ".mp3")
                    _item['url'] = "%soptimized/%s?token=%s&expiration=%s" % (_token['url'], _children['hashname'], _token['params']['token'], _token['params']['expiration'])
                    _item['space'] = os.path.join(response.meta['product_id'], path, _children['name'])
                    yield _item

        yield from _childrens(_json['tree'])


__script__ = Script
