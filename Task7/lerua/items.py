# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

# переводим цену в float удаляя попутно пробел
def price_transform(price):
    return float(''.join(price.split()))

# из значений характеристик удаляем пробелы и переводы строк
def char_value_clean(value):
    return ''.join(value.split())

class LeruaItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    href = scrapy.Field(output_processor = TakeFirst())
    name = scrapy.Field(output_processor = TakeFirst())
    price = scrapy.Field(input_processor = MapCompose(price_transform), output_processor = TakeFirst())
    photos = scrapy.Field()
    char_name = scrapy.Field()
    char_value = scrapy.Field(input_processor = MapCompose(char_value_clean))
    characteristics = scrapy.Field()
