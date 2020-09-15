from core import CoreSpider
from scrapy import Spider, Request, FormRequest
import os
from core.runtime import Setting
from scrapy.http.response.html import HtmlResponse
import demjson
from .items import AuthorItem, TaskWorkItem, FileSourceItem, ArticleTextSourceItem
from . import Runtime, file_space


class Script(CoreSpider):
    _engine = None

    @classmethod
    def settings(cls):
        return {
            #https://www.pixiv.net/users/46811099
            # 'AUTOTHROTTLE_ENABLED': True,
            'CONCURRENT_REQUESTS': 10,
            # 'LOG_LEVEL': 'ERROR',

            # 'LOG_ENABLED': True,
            'FILES_STORE': os.path.join(Runtime.path().get("FILES_STORE"), 'author'),
            # 'DOWNLOADER_MIDDLEWARES': {
            #     'script.fanbox.pipelines.ProxyMiddleware': 100,
            # },
            'ITEM_PIPELINES': {
                'script.fanbox.pipelines.TaskPipeline': 90
            },
        }

    @classmethod
    def start_requests(cls):
        # cls._engine = DatabaseUtil.init("pixiv_space")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
            'Accept-Language': 'zh-CN',
            'origin': 'https://www.fanbox.cc',
            'referer': 'https://www.fanbox.cc/creators/supporting'
        }
        _cookies = Setting.space("fanbox.runtime").parameter("cookies.json").json()
        _url = "https://api.fanbox.cc/plan.listSupporting"
        yield Request(url=_url, callback=cls.authors, cookies=_cookies, headers=headers)

        _url = "https://api.fanbox.cc/creator.listFollowing"
        yield Request(url=_url, callback=cls.authors, cookies=_cookies, headers=headers)

    @classmethod
    def authors(cls, response: HtmlResponse):
        _detail = demjson.decode(response.text)['body']
        for _author in _detail:
            _creator_id = _author['creatorId']
            _author_url = "https://www.fanbox.cc/@%s" % _creator_id
            response.meta['creator_id'] = _creator_id
            _author_list_creator = "https://api.fanbox.cc/post.listCreator?creatorId=%s&limit=10" % _creator_id
            yield Request(url=_author_list_creator, callback=cls.analysis, meta=response.meta, headers={
                'origin': 'https://www.fanbox.cc',
                'referer': _author_url
            })

    @classmethod
    def analysis(cls, response: HtmlResponse):
        _detail = demjson.decode(response.text)['body']
        _space = cls.settings().get('FILES_STORE')
        _creator_id = response.meta['creator_id']
        for _item in _detail['items']:
            _author_item = AuthorItem()
            _author_item['id'] = _item['user']['userId']
            _author_item['name'] = _item['user']['name']
            _author_item['creator'] = _item['creatorId']

            _task_work_item = TaskWorkItem()
            _task_work_item['id'] = _item['id']
            _task_work_item['title'] = _item['title']
            _task_work_item['author'] = _author_item
            _task_work_item['description'] = _item['excerpt']
            _task_work_item['upload_date'] = _item['updatedDatetime']
            _task_work_item['type'] = _item['type']
            _task_work_item['count'] = 0
            _task_work_item['tag'] = _item['tags']
            _task_work_item['space'] = file_space(_task_work_item)

            if _item['coverImageUrl'] is not None:
                _task_work_item['datas'].append(FileSourceItem(url=_item['coverImageUrl']))
            if _item['body'] is not None:
                if _item['type'] == 'image':
                    for _image in _item['body']['images']:
                        _task_work_item['datas'].append(FileSourceItem(url=_image['originalUrl']))
                        _task_work_item['count'] += 1
                if _item['type'] == 'file':
                    for _file in _item['body']['files']:
                        _file_name = "%s_%s" % (_file['name'], _file.get("url").split('/')[-1])

                        _task_work_item['datas'].append(FileSourceItem(url=_file['url'], file=_file_name))
                        _task_work_item['count'] += 1
                if _item['type'] == "article":
                    _images = _item['body']['imageMap']
                    for _block in _item['body']['blocks']:
                        if _block['type'] == "p":
                            _task_work_item['datas'].append(ArticleTextSourceItem(text=_block['text']))

                        if _block['type'] == "image":
                            _text_image = _images[_block['imageId']]
                            _file_item = FileSourceItem(url=_text_image['originalUrl'])
                            _task_work_item['datas'].append(_file_item)

            yield _task_work_item

        if _detail['nextUrl'] is not None:
            yield Request(url=_detail['nextUrl'], callback=cls.analysis, meta=response.meta, headers={
                'origin': 'https://www.fanbox.cc',
                'referer': "https://www.fanbox.cc/@%s" % _creator_id
            })


__script__ = Script
