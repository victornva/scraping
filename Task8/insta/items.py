# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaItem(scrapy.Item):
    # define the fields for your item here like:
    account = scrapy.Field()
    type = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    photo = scrapy.Field()
    _id = scrapy.Field()
