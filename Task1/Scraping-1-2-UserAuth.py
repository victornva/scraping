'''
Урок 1. Основы клиент-серверного взаимодействия. Парсинг API
2.  Изучить список открытых API (https://www.programmableweb.com/category/all/apis). 
    Найти среди них любое, требующее авторизацию (любого типа). 
    Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
    Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide). 
    Сделайте запрос, чтб получить список всех сообществ на которые вы подписаны.
'''
import requests
from requests.exceptions import HTTPError
import os
import json
from pprint import pprint

#https://api.vk.com/method/groups.get?v=5.124&extended=1&access_token=
link = 'https://api.vk.com/method/groups.get'
v = '5.124'    # версия api vk
extended = '1' # возвращать подробную иформацию 
access_token = 'а сюда вставляем свой токен - как получить https://zen.yandex.ru/media/kakprosto/kak-poluchit-accesstoken-vkontakte-5d72243d06cc4600ad8cb5f3'
par = {'v':v, 'extended':extended, 'access_token':access_token}

try:
    response = requests.get(link, params = par,)

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')

else:
    #print('Status Code : ', response.status_code)
    if response.status_code == 200:

        community_data = response.json()
        #pprint(community_data)

        work_dir = os.path.join(os.path.dirname(__file__), "community.json")
        with open(work_dir, 'w', encoding="utf-8") as f:
            json.dump(community_data,f)

        print(f'Всего {community_data["response"]["count"]} подписки:')
        for comm in community_data["response"]["items"]:
            print(f' - {comm["name"]}')
    
    else:
        print(f'Список подписок получить не удалось, получен код {response.status_code}')