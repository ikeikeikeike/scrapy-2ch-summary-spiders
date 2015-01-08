# -*- coding: utf-8 -*-
import itertools

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http.request import Request

import feedparser

from scrapy_mongodb import MongoDBPipeline


collection = None


def _request_ignores(url, settings=None):
    """ すでに登録済みはリクエストしない
    """
    global collection

    if not collection and settings:
        collection = MongoDBPipeline(settings).collection

    row = collection.find_one({'url': url})

    return row and len(row.get('contents', [])) > 0


class ThreadFloatBbsSpider(BaseSpider):
    """ For 2ch summary site.
    """
    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)

        self.feeds = None

    def parse(self, response):
        """ main
        """
        return self._parse_response(response, self._rdf_to_links)

    def _rdf_to_links(self, response):
        """ rdf fileからlinkを抽出する
        """
        self.feeds = feedparser.parse(response.url)
        for feed in self.feeds['entries']:
            yield feed['link']

    def _parse_response(self, response, rdf_to_links):
        """ 処理を単体にする
        """
        links = rdf_to_links(response)
        for link in links:
            if not _request_ignores(link, self.settings):
                yield self._move_to_spider_page(response, link)

    def _move_to_spider_page(self, response, link):
        """ move to spider page(scrape page)
        """
        return Request(link, callback=self.spider_page, method="GET")

    def request_title(self, url, item):
        """ Request url with item.
        """
        if url:
            request = Request(url, callback=self._parse_title,
                              method="GET", dont_filter=True)
            request.meta['item'] = item
            yield request
        else:
            yield item

    def _parse_title(self, response):
        """ Scraping title from url.
        """
        sel = Selector(response)
        item = response.request.meta['item']
        item['source_title'] = self.get_text(sel.xpath('//h1'))
        yield item

    def get_text(self, selector):
        """ textが存在すれば値を返す
        """
        text = selector.xpath('text()').extract()
        if len(text) < 1:
            return
        elif not text[0]:
            return
        else:
            return text[0].strip()

    def get_feed(self, url):
        """ feedを返す
        """
        predicate = lambda f: f['link'] == url
        return itertools.ifilter(predicate, self.feeds['entries']).next()


class SequenceAppend(object):
    """ 数字の場合indexを進める
    """
    def __init__(self, template):
        self.template = template
        self.items = []

    def append(self, item):
        if not self.items:
            base = self.template.copy()
        else:
            base = self.items[-1].copy()

        self._sequence_loop(base, base)

        self.items.append(dict(base, **item))

    def result(self):
        return self.items

    def _sequence_loop(self, base, item):
        for key, value in item.iteritems():
            if value is int:
                value = 0
            elif isinstance(value, int):
                value += 1
            elif isinstance(value, long):
                value += 1L
            base.update({key: value})
