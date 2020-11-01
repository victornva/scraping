'''Урок 6. Scrapy.
II вариант
1) Создать двух пауков по сбору данных о книгах с сайтов labirint.ru и book24.ru
2) Каждый паук должен собирать:
* Ссылку на книгу
* Наименование книги
* Автор(ы)
* Основную цену
* Цену со скидкой
* Рейтинг книги
3) Собранная информация дожная складываться в базу данных
'''
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from bookparser import settings
from bookparser.spiders.labirintru import LabirintruSpider
from bookparser.spiders.book24ru import Book24ruSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)

    process.crawl(Book24ruSpider)
    process.crawl(LabirintruSpider)

    process.start()
