# -*- coding: utf-8 -*-
import re
import itertools

from scrapy.selector import Selector

from summaries.items import SummariesItem

import thread_float_bbs


class PioncooSpider(thread_float_bbs.ThreadFloatBbsSpider):
    """ for pioncoo.net
    """
    name = 'pioncoo'
    allowed_domains = ['pioncoo.net']
    start_urls = ['http://pioncoo.net/index.rdf']

    def spider_page(self, response):
        """ scraping page
        """
        sel = Selector(response)

        source = [
            href for href
            in sel.css('p').xpath('text()').extract()
            if href.find('2ch.net') != -1
            or href.find('2ch.sc') != -1
        ][0]
        source = re.search(u"(?P<url>https?://[^\s][^」\"]+)", source).group("url").strip()

        feed = self.get_feed(response.url)
        tags = [self.get_text(tag) for tag in sel.css('p.tag > a') if self.get_text(tag)]

        contents = []
        image_urls = []
        for index, (sub, body) in enumerate(itertools.izip(sel.css('.t_h'), sel.css('.t_b'))):

            image_urls.extend(sub.css('img').xpath('@src').extract())
            image_urls.extend(body.css('img').xpath('@src').extract())

            contents.append({
                "index": index,
                "subject": sub.extract(),
                "body": body.extract()
            })

        item = dict(
            posted=False,
            source=source,
            url=response.url,
            title=self.get_text(sel.xpath('//h1/span')),
            tags=list(set([feed['tags'][0]['term']] + tags)),
            contents=contents,
            image_urls=image_urls
        )

        # set title from source.
        return self.request_title(item['source'], SummariesItem(**item))
