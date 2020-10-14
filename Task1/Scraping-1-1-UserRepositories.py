'''
Урок 1. Основы клиент-серверного взаимодействия. Парсинг API
1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.
'''
import requests
from requests.exceptions import HTTPError
import os
import json

#curl https://api.github.com/search/repositories?q=user:victornva
link = 'https://api.github.com/search/repositories'
name = input("ВВедите имя вашего аккаута на github: ")
user = {'q': 'user:' + name}

try:
    response = requests.get(link, params = user,)

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')

else:
    #print('Status Code : ', response.status_code)
    if response.status_code == 200:

        j_data = response.json()

        work_dir = os.path.join(os.path.dirname(__file__), "repositories.json")
        with open(work_dir, 'w', encoding="utf-8") as f:
            json.dump(j_data,f)

        print(f'У пользователя {user["q"].split("user:", 1)[1]} всего {j_data["total_count"]} репозитория:')
        n = 0
        while n < j_data["total_count"]:
            print(f' - {j_data["items"][n]["name"]} ')
            n += 1
    else:
        print(f'Список репозиториев получить не удалось, получен код {response.status_code}')