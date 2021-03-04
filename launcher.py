from scrapy.crawler import CrawlerProcess
import os

from core import CoreSpider
from multiprocessing import Process, freeze_support, Pool
# # from script.pixiv import author
# # from script.fanbox import author
# from script.tstorage import users
import script.pixiv.author
# import script.dlsite.asmr
import script.iwara.author
# import script.xiami.favorites
# import script.fanbox.author
# import script.fanbox_subscribe.author
# import script.tstorage.users

from core.util import service_ready
import time
from script.pixiv.core.databases import DatabaseUtil
import os


def crawl_run(spider: CoreSpider):
    process = CrawlerProcess(spider.settings())

    process.crawl(spider)
    process.start()


if __name__ == '__main__':
    os.environ["SPIDER_RUNTIME"] = "runtime"
    os.environ["SPIDER_SPACE"] = os.path.join("space")
    os.environ["MYSQL_SERVICE"] = "127.0.0.1"

    # DatabaseUtil.init("pixiv")
    #
    freeze_support()
    # while service_ready(os.environ.get('MYSQL_SERVICE'), 3306) is False:
    #     time.sleep(1)

    _pool = Pool(processes=10)
    _scripts = [
        # script.pixiv.author,
        script.pixiv.author,
        # script.dlsite.asmr
        # script.fanbox_subscribe.author,
        script.iwara.author,
        # script.xiami.favorites,
        # script.tstorage.users,
    ]

    for _script in _scripts:
        _pool.apply_async(crawl_run, args=(_script.Script,))

    _pool.close()
    _pool.join()
