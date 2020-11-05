import scrapy
from scrapy.http import HtmlResponse
from lerua.items import LeruaItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']
    #start_urls = ['https://leroymerlin.ru/search/?q=шуруповерт')#%D1%88%D1%83%D1%80%D1%83%D0%BF%D0%BE%D0%B2%D0%B5%D1%80%D1%82']
    page = 1
    #search = ''

    def __init__(self, search):
        self.search = search
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']
        #https: // leroymerlin.ru / search /?page = 1 & q = % D1 % 88 % D1 % 83 % D1 % 80 % D1 % 83 % D0 % BF % D0 % BE % D0 % B2 % D0 % B5 % D1 % 80 % D1 % 82

    # перебор страниц
    def parse(self, response):
        # собираем товары с текущей страницы
        links = response.xpath("//a[@slot='name']")#/@href").extract()
        # и переходим по ним в методе goods_parse
        for link in links:
            print(link)
            yield response.follow(link, callback=self.goods_parse)

        # проверяем есть ли следующая гл.страница и если есть идём туда и т.д. пока не кончатся страницы
        next_button = response.xpath("//div[@class='plp-card-list__show-more']")
        if next_button:
            self.page += 1
            next_page = 'https://leroymerlin.ru/search/?q=' + self.search + '&page=' + str(self.page)
            print(next_page)
            yield response.follow(next_page, callback=self.parse)

    # страница товара
    def goods_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=LeruaItem(), response=response)
        loader.add_value('href', response.url)
        loader.add_xpath('name', "//h1[@itemprop='name']/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('photos', "//img[@alt='product image']/@src")
        loader.add_xpath('char_name', "//dt[@class='def-list__term']/text()")
        loader.add_xpath('char_value', "//dd[@class='def-list__definition']/text()")
        loader.add_value('characteristics', {}) # это словарь для записи характеристик в базу в наглядном виде
        yield loader.load_item()

        #href = response.url
        #name = response.xpath("//h1[@itemprop='name']/text()").extract_first()
        #price = response.xpath("//span[@slot='price']/text()").extract()
        #photos = response.xpath("//img[@alt='product image']/@src").extract()
        #char_name = response.xpath("//dt[@class='def-list__term']/text()").extract()
        #char_value = response.xpath("//dd[@class='def-list__definition']/text()").extract()
        #print(name, price, chars)
        #yield LeruaItem(href=href, name=name, price=price, photos=photos, char_name=char_name, char_value=char_value)
