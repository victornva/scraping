import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D1%84%D0%B8%D0%B7%D0%B8%D0%BA%D0%B0/?stype=0']

    # страницы
    def parse(self, response):
        links = response.xpath("//a[@class='cover']/@href").extract()
        next_page = response.xpath("//a[@class='pagination-next__text']/@href").extract_first()
        #print()
        for link in links:
            yield response.follow(link, callback=self.book_parse)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    # ссылки на книги
    def book_parse(self, response: HtmlResponse):
        href = response.url
        title = response.xpath("//div[@id='product-info']/@data-name").extract()
        authors = response.xpath("//div/a[@data-event-label='author']/text()").extract()
        price = response.xpath("//div/span[@class='buying-pricenew-val-number']/text()").extract()
        fake_price = response.xpath("//div/span[@class='buying-priceold-val-number']/text()").extract()
        rate = response.xpath("//div[@id='rate']/text()").extract()

        yield BookparserItem(href=href, title=title[0], authors=authors[0],
                             price=float(price[0]), fake_price=float(fake_price[0]), rate=float(rate[0]))
