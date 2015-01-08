# -*- coding: utf-8 -*-
import re
# import itertools

from scrapy import log
from scrapy.selector import Selector

from summaries.items import SummariesItem

from thread_float_bbs import (
    SequenceAppend,
    ThreadFloatBbsSpider
)


class SecondGigenchanSpider(ThreadFloatBbsSpider):
    """ for 2gigenchan.blog.fc2.com
    """
    name = '2gigenchan'
    allowed_domains = ['2gigenchan.blog.fc2.com']
    start_urls = ['http://2gigenchan.blog.fc2.com/?xml']

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

        # Main: FIXME: dt tagが一括でとれてしまう
        for body in sel.css('div.entry-body > dl > dt'):

            image_urls.extend(body.css('img').xpath('@src').extract())

            contents.append({
                "subject": '',
                "body": body.extract()
            })

        item = dict(
            posted=False,
            source=(
                self.extract_source(sel) or
                self.extract_source(sel, 'div.entry-body')
            ),
            url=response.url,
            title=self.get_text(sel.css('h2')),
            tags=self.extract_tags(sel, response),
            contents=contents.result(),
            image_urls=image_urls
        )

        # set title from source.
        return self.request_title(item['source'], SummariesItem(**item))

    def extract_source(self, selector, css_target='div.entry-body a'):
        """ Sourceを抽出
        """
        try:
            url = [
                text for
                text in selector.css(css_target).xpath('text()').extract()
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
            tag = [self.get_text(tag) for tag in selector.css('div.entry-footer a')][0]

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
