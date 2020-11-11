'''     Урок 8. Работа с данными
1)Написать приложение, которое будет проходиться по указанному списку двух и/или более пользователей
  и собирать данные об их подписчиках и подписках.
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

    # Пользователь, у которого собираем посты. Можно указать список
    parse_user = ['pupkin5267', 'pupkin1021']

    graphql_url = 'https://www.instagram.com/graphql/query/?'

    followers_hash = 'c76146de99bb02f6415203be841dd25a' # hash VasyaNonPu для получения данных подписчиков
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076' # hash VasyaNonPu для получения данных подписок

    # ------------------------------------------------------------------------------------------------------------------

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
        if j_body['authenticated']:          # Проверяем ответ после авторизации
            for pu in self.parse_user:
                yield response.follow(       # Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                    f'/{pu}',
                    callback= self.user_data_parse,
                    cb_kwargs={'username':pu}
                )

    def user_data_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)       # Получаем id пользователя
        variables={
                    'id':user_id,                                    # Формируем словарь для передачи даных в запрос
                    'first':12
                   }

        # Формируем ссылку для получения данных о подписчиках
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'username':username,
                       'user_id':user_id,
                       'variables':deepcopy(variables)}         # variables ч/з deepcopy во избежание гонок
        )

        # Формируем ссылку для получения данных о подписках
        url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
        yield response.follow(
            url_following,
            callback=self.user_following_parse,
            cb_kwargs={'username':username,
                       'user_id':user_id,
                       'variables':deepcopy(variables)}
        )

    # ------------------------------------------------------------------------------------------------------------------
    #   Подписчики
    def user_followers_parse(self, response:HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')

        if page_info.get('has_next_page'):                     # Если есть следующая страница
            variables['after'] = page_info['end_cursor']       # Новый параметр для перехода на след. страницу
            url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_followers,
                callback=self.user_followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')  # Сами подписчики

        for follower in followers:            # Перебираем подписчиков, собираем данные
            item = InstaItem(
                account=username,
                type='followed',
                user_id = user_id,
                username = follower['node']['username'],
                full_name = follower['node']['full_name'],
                photo = follower['node']['profile_pic_url'],
            )

        yield item   # -> pipelines.py

    # ------------------------------------------------------------------------------------------------------------------
    #   Подписки
    def user_following_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')

        if page_info.get('has_next_page'):                # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            yield response.follow(
                url_following,
                callback=self.user_following_parse,
                cb_kwargs={'username': username,
                            'user_id': user_id,
                            'variables': deepcopy(variables)}
            )

        following = j_data.get('data').get('user').get('edge_follow').get('edges')  # Сами подписчики

        for follow in following:  # Перебираем подписки, собираем данные
            item = InstaItem(
                account=username,
                type='following',
                user_id=user_id,
                username=follow['node']['username'],
                full_name=follow['node']['full_name'],
                photo=follow['node']['profile_pic_url'],
            )

        yield item  # -> pipelines.py

    # ------------------------------------------------------------------------------------------------------------------

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