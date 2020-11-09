'''     Урок 8. Работа с данными
1)Написать приложение, которое будет проходиться по указанному списку двух и/или более пользователей и собирать данные об их подписчиках и подписках.
2) По каждому пользователю, который является подписчиком или на которого подписан исследуемый объект нужно извлечь
   имя, id, фото (остальные данные по желанию). Фото можно дополнительно скачать.
3) Собранные данные необходимо сложить в базу данных. Структуру данных нужно заранее продумать, чтобы:
4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

scrapy startproject insta .
scrapy genspider instaspider instagram.com
'''
import scrapy
from scrapy.http import HtmlResponse
from insta.items import InstaItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstaspiderSpider(scrapy.Spider):
    name = 'instaspider'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    insta_login = 'VasyaNonPu'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1604744379:AaRQAGoeGfH5NIvsXX/OxrSfJX+cfV36l0GOvDh0Qzj0BwYuwPmvOdVGjHEkvXDyb4mcuUcDHcgaknC8HsSPVXGygqVeqEOA/z1jEBQ+YzQmRMQC5pVxNwIVhE9ls9UT9e2/CrZJPSY70w8c30mS5V2fYA=='
    # userId	"44252839148"

    parse_user = 'ai_machine_learning'      #Пользователь, у которого собираем посты. Можно указать список

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = 'eddbde960fed6bde675388aac39a3657'     #hash для получения данных по постах с главной страницы


    def parse(self, response):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.insta_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username':self.insta_login, 'enc_password':self.insta_pwd},
            headers={'X-CSRFToken':csrf_token}
        )
    def user_parse(self, response:HtmlResponse):
        j_body = json.loads(response.text)
        print(j_body)
        if j_body['authenticated']:                 #Проверяем ответ после авторизации
            yield response.follow(                  #Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                f'/{self.parse_user}',
                callback= self.user_data_parse,
                cb_kwargs={'username':self.parse_user}
            )

    def user_data_parse(self, response:HtmlResponse, username):
        print()

    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')