from scrapy.crawler import CrawlerProcess

from core import CoreSpider
from multiprocessing import Process, freeze_support
from script.pixiv import author


def crawl_run(spider: CoreSpider):
    process = CrawlerProcess(spider.settings())
    process.crawl(spider)
    process.start()


if __name__ == '__main__':
    freeze_support()
    # while True:
    _run_process = Process(target=crawl_run, args=(author.Script,))
    _run_process.start()
    _run_process.join()
