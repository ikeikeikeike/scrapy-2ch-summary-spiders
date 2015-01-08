# -*- coding: utf-8 -*-
import itertools

from scrapy import log
from scrapy.selector import Selector

from summaries.items import SummariesItem

import thread_float_bbs


class HimarinSpider(thread_float_bbs.ThreadFloatBbsSpider):
    """ for himarin.net
    """
    name = 'himarin'
    allowed_domains = ['himarin.net']
    start_urls = ['http://himarin.net/index.rdf']

    def spider_page(self, response):
        """ scraping page
        """
        sel = Selector(response)

        contents = []
        image_urls = []
        generator = itertools.izip(sel.css('.t_h'), sel.css('.t_b'))
        for index, (sub, body) in enumerate(generator):

            image_urls.extend(sub.css('img').xpath('@src').extract())
            image_urls.extend(body.css('img').xpath('@src').extract())

            contents.append({
                "index": index,
                "subject": sub.extract(),
                "body": body.extract()
            })

        item = dict(
            posted=False,
            source=self.extract_source(sel),
            url=response.url,
            title=self.get_text(sel.xpath('//h2')),
            tags=self.extract_tags(sel, response),
            contents=contents,
            image_urls=image_urls
        )
        # set title from source.
        return self.request_title(item['source'], SummariesItem(**item))

    def extract_source(self, selector):
        """ Sourceを抽出
        """
        try:
            return [
                href for href
                in selector.css('span > a').xpath('@href').extract()
                if href.find('2ch.net') != -1
                or href.find('2ch.sc') != -1
            ][0]
        except Exception as exc:
            log.msg(
                format=("Extract source (error): "
                        "Error selector %(selector)s "
                        "url `%(url)s`: %(errormsg)s"),
                level=log.WARNING,
                spider=self,
                selector=selector,
                url=selector.response.url,
                errormsg=str(exc))
        return None

    def extract_tags(self, selector, response):
        """ tagsを抽出
        """
        try:
            feed = self.get_feed(response.url)
            tag = [
                self.get_text(tag)
                for tag in selector.css('.article-info > a')
            ][-1]

            return list({feed['tags'][0]['term'], tag})
        except Exception as exc:
            log.msg(
                format=("Extract tags (error): "
                        "Error selector %(selector)s "
                        "url `%(url)s`: %(errormsg)s"),
                level=log.WARNING,
                spider=self,
                selector=selector,
                url=response.url,
                errormsg=str(exc))
        return []
