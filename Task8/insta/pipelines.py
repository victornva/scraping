# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class InstaPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.instaDB = client.InstaAccounts

    def process_item(self, item, spider):
        collection = self.instaDB[item['account']]
        collection.insert_one({'type':item['type'], 'user_id':item['user_id'], 'user_name':item['username'],
                               'full_name':item['full_name'], 'photo':item['photo']})
        #collection.insert_one(item)

        # Такие данные удобнее хранить в реляционной БД, но мы используем MongoDB.
        # Напишем отдельную программку для запросов на питоне, чтобы поиск данных был отделён от скрапинга,
        # или можно из консоли MongoDB:
        # use InstaAccounts
        # список подписчиков только указанного пользователя
        # db.pupkin5257.find({type:'followed'},{'user_name':1});
        # список профилей, на кого подписан указанный пользователь
        # db.pupkin5257.find({type:'following'},{'user_name':1});
        # список подписчиков только указанного пользователя
        # db.pupkin1021.find({type:'followed'},{'user_name':1});
        # список профилей, на кого подписан указанный пользователь
        # db.pupkin1021.find({type:'following'},{'user_name':1});

        #print(item)
        return item


class instaUserPhotoPipeLine(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['photo']:
            try:
                yield scrapy.Request(item['photo'])
            except Exception as e:
                print(e)
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"{item['account']}/{item['username']}.jpg"
