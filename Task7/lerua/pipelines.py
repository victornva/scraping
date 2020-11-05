# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy

class LeruaPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.leruaDB = client.goods

    def process_item(self, item, spider):
        # запишем данные в базу, перед этим характеристики скомпонуем в словарь для наглядности
        # (хотя мне кажется для машинной обработки удобнее оставить два списка отдельно)
        item['characteristics'] = dict(zip(item['char_name'], item['char_value']))

        collection = self.leruaDB[spider.name]
        collection.insert_one({'href':item['href'], 'name':item['name'], 'price':item['price'],
                               'photos':item['photos'], 'characteristics':item['characteristics']})
        #collection.insert_one(item)

        return item

class leruaPhotoPipeLine(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        dir = item['name']
        image_guid = request.url.split('/')[-1]
        return f'{dir}/img{image_guid}'

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
