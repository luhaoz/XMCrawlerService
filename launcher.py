from scrapy.crawler import CrawlerProcess

from core import CoreSpider
from multiprocessing import Process, freeze_support
import spider


def crawl_run(spider: CoreSpider):
    process = CrawlerProcess({})
    process.crawl(spider)
    process.start()


if __name__ == '__main__':
    freeze_support()
    # while True:
    _run_process = Process(target=crawl_run, args=(spider.Script,))
    _run_process.start()
    _run_process.join()
