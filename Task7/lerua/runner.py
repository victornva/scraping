'''     Урок 7. Scrapy - фото, файлы
1) Взять любую категорию товаров на сайте Леруа Мерлен. Собрать с использованием ItemLoader следующие данные:
● название;
● все фото;
● параметры товара в объявлении;
● ссылка;
● цена.
С использованием output_processor и input_processor реализовать очистку и преобразование данных.
  Цены должны быть в виде числового значения.
2)Написать универсальный обработчик параметров объявлений, который будет формировать данные
  вне зависимости от их типа и количества.
3)Реализовать хранение скачиваемых файлов в отдельных папках, каждая из которых должна соответствовать
  собираемому товару

scrapy startproject lerua .
scrapy genspider leroymerlinru leroymerlin.ru
'''
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lerua import settings
from lerua.spiders.leroymerlinru import LeroymerlinruSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    #search_item = input('Введите ... ')
    search_item = 'шуруповерт'
    process.crawl(LeroymerlinruSpider, search=search_item)

    process.start()
