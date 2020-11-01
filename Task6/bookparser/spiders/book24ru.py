import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    page = '1'
    start_urls = ['https://book24.ru/search/?q=%D1%84%D0%B8%D0%B7%D0%B8%D0%BA%D0%B0']

    # страницы
    def parse(self, response):
        # смотрим общее кол-во страниц по запросу
        last_page = int(response.xpath("//a[@class='catalog-pagination__item js-pagination-catalog-item']/text()").extract()[-1])

        links = response.xpath("//a[@class='book__image-link js-item-element ddl_product_link']/@href").extract()

        for link in links:
            yield response.follow(link, callback=self.book_parse)

        # перебираем страницы пока не дойдём до последней
        if int(self.page) < last_page:
            self.page = str(int(self.page) + 1)
            next_page = 'https://book24.ru/search/page-'+self.page+'/?q=%D1%84%D0%B8%D0%B7%D0%B8%D0%BA%D0%B0'
            yield response.follow(next_page, callback=self.parse)

    # ссылки на книги
    def book_parse(self, response: HtmlResponse):
        # мы вызываем этот метод и передаём в него ссылку, но где она тут? что то не нашёл 
        href = response.xpath("//link[@rel='amphtml']/@href").extract()
        title = response.xpath("//h1[@class='item-detail__title']/text()").extract()
        authors = response.xpath("//span/a[@class='item-tab__chars-link js-data-link']/text()").extract()
        price = response.xpath("//div/b[@itemprop='price']/text()").extract()
        fake_price = response.xpath("//div/b[@itemprop='price']/text()").extract()
        rate = response.xpath("//div/span[@class='rating__rate-value']/text()").extract()
        try:
            r = float(rate[0].replace(',', '.'))
        except:
            r = 0

        yield BookparserItem(href=href[0], title=title[0], authors=authors[0],
                             price=float(price[0]), fake_price=float(fake_price[0]), rate=r)