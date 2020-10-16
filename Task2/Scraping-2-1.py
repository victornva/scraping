'''
Урок 2. Парсинг HTML. BeautifulSoup

Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайтов Superjob и HH. 
Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы). 
Получившийся список должен содержать в себе минимум:
Наименование вакансии.
Предлагаемую зарплату (отдельно минимальную и максимальную).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия. 
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). 
Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
'''
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup as bs
import os
import json
from pprint import pprint

#------------------------------------------------------------------------------------------
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.1.112 Yowser/2.5 Safari/537.36'}

print('\nНачало\n')

q_vacancy = 'врач'#'killer'#input("ВВедите искомую вакансию: ")

hh_link = 'https://hh.ru'
hh_vac_search_link = '/search/vacancy'
hh_vac_par = {'text':q_vacancy, 'st':'searchVacancy', 'enable_snippets':'true', 'area':'1', 'clusters':'true'}

#------------------------------------------------------------------------------------------
responce = requests.get(hh_link + hh_vac_search_link, params = hh_vac_par, headers = headers)

soup = bs(responce.text, 'html.parser')

vacancy_list = soup.findAll('div', {'class':'vacancy-serp-item'}) 

vacancies = []
for vacancy in vacancy_list:
    vacancy_data = {}
    
    vacancy_name = vacancy.find('div', {'class':'vacancy-serp-item__info'}).getText()
    
    vacancy_sal = vacancy.find('div', {'class':'vacancy-serp-item__sidebar'}).getText()
    if not vacancy_sal:                            # ЗП не указана - работа за еду (или рабство...)
        salary_min = None
        salary_max = None
        currency = None
    else:
        vacancy_sal = "".join(vacancy_sal.split()) # убираем пробелы
        if vacancy_sal.endswith('руб.'):           # определяем валюту (по идее надо делать список валют, но некогда)
            currency = 'руб'
        if vacancy_sal.endswith('USD'):
            currency = 'USD'
        vacancy_sal = vacancy_sal.split(currency)[0] # отрезаем обозначение валюты

        if vacancy_sal.startswith('от'):             # указана мин. ЗП
            salary_min = float(vacancy_sal.split('от')[1])
            salary_max = None
        if vacancy_sal.find('-') != -1:              # указан диапазон ЗП
            salary_min = float(vacancy_sal.split('-')[0])
            salary_max = float(vacancy_sal.split('-')[1])
    #print(vacancy_sal, salary_min, salary_max, currency)
    
    vacancy_corp = hh_link + vacancy.find('a', {'class':'bloko-link bloko-link_secondary'})['href']

    vacancy_href = vacancy.find('a', {'class':'bloko-link HH-LinkModifier'})['href']

    #print('- ', vacancy_name, ' - ', vacancy_sal, ' - ', vacancy_corp, ' - ', vacancy_href)

    vacancy_data['name'] = vacancy_name
    vacancy_data['min_salary'] = salary_min
    vacancy_data['max_salary'] = salary_max
    vacancy_data['currency'] = currency
    vacancy_data['employer'] = vacancy_corp
    vacancy_data['link'] = vacancy_href
    vacancy_data['site'] = hh_link
    #print(vacancy_data)
    vacancies.append(vacancy_data)

#------------------------------------------------------------------------------------------
# https://www.superjob.ru/vakansii/vrach.html?geo%5Bt%5D%5B0%5D=4&page=1

sj_link = 'https://www.superjob.ru' # на суперджобе другая структура запроса
sj_vac_search_link = '/vakansii/'
q_vacancy = 'vrach' # и нужна транслитерация для запросов на русском - не будем с этим тут заморачиваться

max_lists = 1
i = 1
while i < max_lists+1:

    vac_par = {'geo%5Bt%5D%5B0%5D':'4', 'page':str(i)}

    responce = requests.get(sj_link + sj_vac_search_link + q_vacancy + '.html', params = vac_par, headers = headers)

    soup = bs(responce.text, 'html.parser')
    # ищем кол-во страниц:
    lists_num = soup.find('div', {'class':'_3zucV L1p51 undefined _1Fty7 _2tD21 _3SGgo'}) #.find('span', {'class':'qTHqo _1mEoj _2h9me DYJ1Y _2FQ5q _2GT-y'})
    for lists in lists_num:
        l = str(lists.find('span', {'class':'_3IDf-'}))
        if l != 'None':
            l2 = l.split('<span class="_3IDf-">')[1].split('</span>')[0]
            if l2.isdigit():
                l2 = int(l2)
                if l2 > max_lists: max_lists = l2
    print(f'\n-------- Страница {i} из {max_lists} -------------\n')
    
    # обрабатываем вакансии на каждой странице:
    vacancy_list = soup.findAll('div', {'class':'Fo44F QiY08 LvoDO'}) 

    for vacancy in vacancy_list:

        vacancy_name = vacancy.find('div', {'class':'_3mfro PlM3e _2JVkc _3LJqf'}).getText()
        
        vacancy_sal = vacancy.find('span', {'class':'_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'}).getText()
        if vacancy_sal == 'По договорённости':                           
            salary_min = None
            salary_max = None
            currency = None
        else:
            vacancy_sal = "".join(vacancy_sal.split()) # убираем пробелы
            if vacancy_sal.endswith('руб.'):           # определяем валюту (по идее надо делать список валют, но некогда)
                currency = 'руб'
            if vacancy_sal.endswith('USD'):
                currency = 'USD'
            vacancy_sal = vacancy_sal.split(currency)[0] # отрезаем обозначение валюты

            if vacancy_sal.startswith('от'):             # указана мин. ЗП
                salary_min = float(vacancy_sal.split('от')[1])
                salary_max = None
            if vacancy_sal.startswith('до'):             # указана макс. ЗП
                salary_min = None
                salary_max = float(vacancy_sal.split('до')[1])

        try:
            vacancy_corp = sj_link + vacancy.find('div', {'class':'_3_eyK _3P0J7 _9_FPy'}).find('a')['href']
        except:
            vacancy_corp = None

        vacancy_href = sj_link + vacancy.find('a')['href']

        vacancy_data['name'] = vacancy_name
        vacancy_data['min_salary'] = salary_min
        vacancy_data['max_salary'] = salary_max
        vacancy_data['currency'] = currency
        vacancy_data['employer'] = vacancy_corp
        vacancy_data['link'] = vacancy_href
        vacancy_data['site'] = sj_link
        print('------------------------\n', vacancy_data)
        
        vacancies.append(vacancy_data)
    i += 1

#pprint(vacancies)

#------------------------------------------------------------------------------------------
# фреймы не проходили - просто запишем в файл в json
work_dir = os.path.join(os.path.dirname(__file__), "vacancies.json")
with open(work_dir, 'w', encoding="utf-8") as f:
    json.dump(vacancies,f)

print('\nКонец\n')