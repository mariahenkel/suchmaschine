from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from config import TXT_PATH
from basic_crawler.items import Website
from link_collector import get_websites_from_txt


class Website_spider(CrawlSpider):
    name = "basic_spider_unusability"
    # we 'start' with the top 1 million websites from the file.
    start_urls = get_websites_from_txt(TXT_PATH)
    # regex only matches base urls
    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )
    print 'start crawling...'

    def parse_item(self, response):
        # we parse the website as an website item with title, link and body
        item = Website()
        title_resp = response.selector.xpath(
            '//title/text()').extract()
        item['title'] = title_resp[0] if len(title_resp) > 0 else None
        item['link'] = response.url
        item['body'] = response.body.decode(response.encoding)
        yield item
