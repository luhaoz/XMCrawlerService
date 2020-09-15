from scrapy.crawler import CrawlerProcess

from core import CoreSpider
from multiprocessing import Process, freeze_support, Pool
# # from script.pixiv import author
# # from script.fanbox import author
# from script.tstorage import users
import script.pixiv.author
import script.fanbox.author
import script.tstorage.users


def crawl_run(spider: CoreSpider):
    process = CrawlerProcess(spider.settings())
    process.crawl(spider)
    process.start()


if __name__ == '__main__':
    freeze_support()
    _pool = Pool(processes=10)
    _scripts = [
        # script.pixiv.author,
        script.fanbox.author,
        script.tstorage.users,
    ]

    for _script in _scripts:
        _pool.apply_async(crawl_run, args=(_script.Script,))

    _pool.close()
    _pool.join()
