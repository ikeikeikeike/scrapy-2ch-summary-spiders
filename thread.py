# -*- coding: utf-8 -*-
# from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.selector import Selector
# from scrapy.http.request import Request

# import feedparser
from summaries.items import SummariesItem

# from summaries.items import SummariesItem


class ThreadSpider(BaseSpider):
    """ スレッドを取得する
    """
    name = 'thread'
    # allowed_domains = ['localhost:8000', 'hamusoku.com', 'kanasoku.info']
    # start_urls = ['http://localhost:8000/kanasoku.info/index.rdf']

    # def parse(self, response):
        # """ main
        # """
        # return self._parse_response(response, self.rdf_to_links)

    # def _parse_response(self, response, rdf_to_links):
        # """ 処理を単体にする
        # """
        # links = rdf_to_links(response)
        # for link in links:
            # yield self.move_to_spider_page(response, link)

    # def rdf_to_links(self, response):
        # """ rdf fileからlinkを抽出する
        # """
        # feeds = feedparser.parse(response.url)
        # for feed in feeds['entries']:
            # yield feed['link']

    # def move_to_spider_page(self, response, link):
        # """ spider page(scrape page)へ移動する
        # """
        # return Request(link, method="GET", callback=self.spider_page)

    allowed_domains = ['miru-navi.com']
    start_urls = [
        'http://miru-navi.com',
    ]

    def parse(self, response):
        """ main
        """
        return self.spider_page(response)

    def spider_page(self, response):
        from urlparse import urljoin
        sel = Selector(response)

        image_urls = map(lambda url: urljoin('http://miru-navi.com', url), sel.css('img').xpath('@src').extract())

        yield SummariesItem(
            url=response.url,
            image_urls=image_urls
        )
