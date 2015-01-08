# -*- coding: utf-8 -*-
from scrapy.spider import BaseSpider
from scrapy.http.request import Request
from scrapy.utils.response import open_in_browser


class TestSpider(BaseSpider):
    """ Testing Spider
    """
    name = 'test'

    allowed_domains = [
        'miru-navi.com',
        # 'map-fuzoku.com'
    ]

    start_urls = [
        'http://miru-navi.com',
        # 'http://map-fuzoku.com'
    ]

    links = [
        'http://miru-navi.com/stores'
    ]

    def parse(self, response):
        """ main
        """
        # print
        # print
        # print response.headers
        # open_in_browser(response)

        print response.headers
        print 'parse'
        print 'parse'
        print 'parse'
        print 'parse'
        print 'parse'
        print 'parse'
        print 'parse'
        print 'parse'

        for link in self.links:
            yield Request(link, method="GET", callback=self.spider_page)

    def spider_page(self, response):
        print response.headers
        print
        print
        print
        print 'spider_page'
        print 'spider_page'
        print 'spider_page'
        print 'spider_page'
        print 'spider_page'
        print 'spider_page'
        print 'spider_page'
        print 'spider_page'
        print 'spider_page'
        print 'spider_page'
        # print response.headers
        # open_in_browser(response)
