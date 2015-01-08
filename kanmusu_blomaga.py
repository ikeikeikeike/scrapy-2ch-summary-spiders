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


class KanmusuBlomagaSpider(ThreadFloatBbsSpider):
    """ for kanmusu.blomaga.jp
    """
    name = 'kanmusu_blomaga'
    allowed_domains = ['kanmusu.blomaga.jp']
    start_urls = ['http://kanmusu.blomaga.jp/index.rdf']

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
        main = sel.css('div.bodymore')
        generator = itertools.izip(main.css('.t_h'), main.css('.t_b'))
        for sub, body in generator:

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
            title=self.get_text(sel.css('h1 span')),
            tags=self.extract_tags(sel, response),
            contents=contents.result(),
            image_urls=image_urls
        )

        # set title from source.
        return self.request_title(item['source'], SummariesItem(**item))

    def extract_source(self, selector):
        """ Sourceを抽出
        """
        try:
            url = [
                text for
                text in selector.css('div.bodymore span').xpath('text()').extract()
                if text.find('2ch.net') != -1
                or text.find('2ch.sc') != -1
                or text.find('www.logsoku.com') != -1
            ][0]
            return re.search(u"(?P<url>https?://[^\s][^」]+)", url).group("url").strip()
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
            tag = [self.get_text(tag) for tag in selector.css('[class^=category_] > a')][-1]

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
