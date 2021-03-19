import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from eurex.items import Article


class EurexSpider(scrapy.Spider):
    name = 'eurex'
    start_urls = ['https://www.eurex.com/ec-en/find/news/']
    page = 0
    pages = 100000

    def parse(self, response):
        links = response.xpath('//h3/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)
        if response.url == 'https://www.eurex.com/ec-en/find/news/':
            self.pages = int(response.xpath('//li[@class="dbx-pagination__pages"]/button/@value').getall()[-2])

        if self.page < self.pages:
            self.page += 1
            next_page_link = 'https://www.eurex.com/ec-en/find/news/4138!search?state=H4sIAAAAAAAAADWOsQoCMRAFf0W2TqFtarGy' \
                             'CCj24fKigTXB3Q1yHPfvBiHdG2aKt1GKhou0N_namd2f721SjgtMyW_72EXUrjCDTP0qpgES4hPkT0dHpS7cE27FoDNql' \
                             f'deQMvkcWeHo0yEreSJHAu1sj4LvjLWJDafnceOQoAvtP8CH51ukAAAA&pageNum={self.page}'
            yield response.follow(next_page_link, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="dbx-tagline-date "]//span/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="dbx-col-sm-12 dbx-col-md-12 dbx-col-xl-10"]//p//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
