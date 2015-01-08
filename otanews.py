# -*- coding: utf-8 -*-
import re
import itertools

from scrapy import log
from scrapy.selector import Selector

from summaries.items import SummariesItem

from thread_float_bbs import (
    SequenceAppend,
    ThreadFloatBbsSpider
)


class OtanewsSpider(ThreadFloatBbsSpider):
    """ for otanews.livedoor.biz
    """
    name = 'otanews'
    allowed_domains = ['otanews.livedoor.biz']
    start_urls = ['http://otanews.livedoor.biz/index.rdf']

    def spider_page(self, response):
        """ scraping page
        """
        sel = Selector(response)

        image_urls = []
        contents = SequenceAppend({
            "index": int,
            "subject": '',
            "body": ''
        })

        # Main
        main = sel.css('div.main')
        for sub, body in itertools.izip(main.css('.t_h'), main.css('.t_b')):

            image_urls.extend(sub.css('img').xpath('@src').extract())
            image_urls.extend(body.css('img').xpath('@src').extract())

            contents.append({
                "subject": sub.extract(),
                "body": body.extract()
            })

        # Mainmore
        mainmore = sel.css('div.mainmore')

        # If image list in first elements, Add to contents.
        first = mainmore.xpath('div')[0].css('[align="center"]')
        for first_sel in first:

            image_urls.extend(first_sel.css('img').xpath('@src').extract())

            contents.append({
                "subject": 'Images',
                "body": first_sel.extract()
            })

        for sub, body in itertools.izip(mainmore.css('.t_h'), mainmore.css('.t_b')):

            image_urls.extend(sub.css('img').xpath('@src').extract())
            image_urls.extend(body.css('img').xpath('@src').extract())

            contents.append({
                "subject": sub.extract(),
                "body": body.extract()
            })

        item = dict(
            posted=False,
            source=self.extract_source(sel),
            url=response.url,
            title=self.get_text(sel.xpath('//h2/a')),
            tags=self.extract_tags(sel, response),
            contents=contents.result(),
            image_urls=image_urls)

        # set title from source.
        return self.request_title(item['source'], SummariesItem(**item))

    def extract_source(self, selector):
        """ Sourceを抽出
        """
        try:
            url = [
                text for text
                in selector.css('div').xpath('text()').extract()
                if text.find('2ch.net') != -1
                or text.find('2ch.sc') != -1
            ][0]
            return re.search("(?P<url>https?://[^\s]+)", url).group("url")
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
            return list({feed['tags'][0]['term']})
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
