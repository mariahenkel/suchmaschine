from scrapy.contrib.spiders import CrawlSpider
from config import TOP1M_LIMIT
from basic_crawler.items import Website
from link_collector import get_top_1million_websites


class Website_spider(CrawlSpider):
    name = "basic_spider"
    # we 'start' with the top 1 million websites from the file.
    start_urls = get_top_1million_websites(
        TOP1M_LIMIT)
    print 'start crawling...'

    def parse(self, response):
        # we parse the website as an website item with title, link and body
        item = Website()
        title_resp = response.selector.xpath(
            '//title/text()').extract()
        item['title'] = title_resp[0] if len(title_resp) > 0 else None
        item['link'] = response.url
        item['body'] = response.body.decode(response.encoding)
        yield item
