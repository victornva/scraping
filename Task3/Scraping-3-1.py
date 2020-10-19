'''
Урок 3. Системы управления базами данных MongoDB и SQLite в Python
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
'''
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup as bs
import json
from pprint import pprint
from pymongo import MongoClient
#--------------------------------------------------------------------------------------------------------------
def new_vacancy(dbcol, vac_item):
    '''
    ф-ция добавляет в базу новую запись в случае если такой там уже нет
    :param dbcol: ссылка на коллекцию в БД MongoDB
    :param vac_item: dict, данные вакансии
    '''
    try:
        if dbcol.find({'_id':vac_item['_id']})[0]:
            print(f"уже есть вакансия c id {vac_item['_id']} - пропускаем")
            return False
    except:
        print(f"вакансия c id {vac_item['_id']} отсутствует - вставляем в БД!!")
        dbcol.insert_one(vac_item)
        return True
#--------------------------------------------------------------------------------------------------------------
def find_salary(dbcol, salary):
    '''
    ф-ция производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы,
    проверяются поля как мин. так и макс. ЗП - хотя бы одно из них не должно быть меньше введённого значения
    Возвращаем не все данные а только некоторые (для примера), упорядочиваем по мин. и макс. ЗП.
    :param dbcol: ссылка на коллекцию в БД MongoDB
    :param salary: float, минимальная искомая ЗП
    '''
    query = dbcol.find(
                        {'$or':[{'min_salary':{'$gte':salary}}, 
                        {'max_salary':{'$gte':salary}}]}, 
                        {'_id':1,'name':1,'max_salary':1,'min_salary':1}
                        ).sort([('min_salary',1), ('max_salary', 1)])
    #for vac_item in query: print(vac_item)
    return query
#--------------------------------------------------------------------------------------------------------------
print('\nНачало\n')

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.1.112 Yowser/2.5 Safari/537.36'}

q_vacancy = 'врач'#'killer'#input("ВВедите искомую вакансию: ")

#------------------------------------------------------------------------------------------
# Подключаемся к БД
client = MongoClient( 'localhost' , 27017 )
db = client['vacancy_db']
# db.vac.drop()
#---------------------------------------------------------------------------------------------------------------
# https://hh.ru/search/vacancy?area=1187&clusters=true&enable_snippets=true&search_field=name&text=Врач&page=1
hh_link = 'https://hh.ru'
hh_vac_search_link = '/search/vacancy'
#---------------------------------------------------------------------------------------------------------------
vacancies = []

i = 0 # начальная страница на HH

while True:
    print(f'\nHH.ru --- cтраница {i+1} ---\n')

    hh_vac_par = {'page':str(i),'text':q_vacancy,'area':'1187','clusters':'true','from':'cluster_area','L_save_area':'true','st':'searchVacancy', 'enable_snippets':'true'}

    responce = requests.get(hh_link + hh_vac_search_link, params = hh_vac_par, headers = headers)

    soup = bs(responce.text, 'html.parser') # вся страница

    vacancy_list = soup.findAll('div', {'class':'vacancy-serp-item'}) 

    for vacancy in vacancy_list:

        vacancy_data = {} # в каждой итерации очищаем словарь перед записью
        # название 
        vacancy_name = vacancy.find('div', {'class':'vacancy-serp-item__info'}).getText()
        # ЗП
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
        # работодатель
        try:
            vacancy_corp = hh_link + vacancy.find('a', {'class':'bloko-link bloko-link_secondary'})['href']
        except:
            vacancy_corp = None
        # ссылка
        vacancy_href = vacancy.find('a', {'class':'bloko-link HH-LinkModifier'})['href']
        # уникальный id вакансии - чтобы не дублировать записи в базе
        vacancy_id = vacancy.find('a', {'class':'bloko-link bloko-link_dimmed HH-VacancyResponsePopup-Link'})
        vacancy_id = vacancy_id.find('script')['data-params']
        vacancy_id = json.loads("".join(vacancy_id.split())).get('vacancyId')

        vacancy_data['_id'] = vacancy_id
        vacancy_data['name'] = vacancy_name
        vacancy_data['min_salary'] = salary_min
        vacancy_data['max_salary'] = salary_max
        vacancy_data['currency'] = currency
        vacancy_data['employer'] = vacancy_corp
        vacancy_data['link'] = vacancy_href
        vacancy_data['site'] = hh_link

        new_vacancy(db.vac, vacancy_data)
        #vacancies.append(vacancy_data)
    #---------------------------------------------------------------------------------------------
    # смотрим наличие кнопки Дальше
    next_button = soup.find('a', {'class':'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
    if next_button == None: break # последняя страница - выходим

    i += 1 # следующая страница

#------------------------------------------------------------------------------------------
# https://www.superjob.ru/vakansii/vrach.html?geo%5Bo%5D%5B0%5D=8
#
sj_link = 'https://www.superjob.ru' # на суперджобе другая структура запроса
sj_vac_search_link = '/vakansii/'
q_vacancy = 'vrach' # и нужна транслитерация для запросов на русском - не будем с этим тут заморачиваться
#
#------------------------------------------------------------------------------------------
max_lists = 1
i = 1

while i < max_lists + 1:

    vac_par = {'geo%5Bo%5D%5B0%5D':'8', 'page':str(i)}

    responce = requests.get(sj_link + sj_vac_search_link + q_vacancy + '.html', params = vac_par, headers = headers)

    soup = bs(responce.text, 'html.parser')
    # листаем страницы другим способом - ищем общее кол-во страниц на кнопке:
    lists_num = soup.find('div', {'class':'_3zucV L1p51 undefined _1Fty7 _2tD21 _3SGgo'})
    for lists in lists_num:
        l = str(lists.find('span', {'class':'_3IDf-'}))
        if l != 'None': 
            l2 = l.split('<span class="_3IDf-">')[1].split('</span>')[0]
            if l2.isdigit(): 
                l2 = int(l2)
                if l2 > max_lists: max_lists = l2
    print(f'\nsuperjob.ru --- Страница {i} из {max_lists} ---\n')
    
    # обрабатываем вакансии на каждой странице:
    vacancy_list = soup.findAll('div', {'class':'Fo44F QiY08 LvoDO'}) 

    for vacancy in vacancy_list:

        vacancy_data = {}

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
        # уникальный ид вакансии - извлечём его из ссылки на сайт
        vacancy_id = vacancy_href.split('-')[-1].split('.')[0]

        vacancy_data['_id'] = vacancy_id
        vacancy_data['name'] = vacancy_name
        vacancy_data['min_salary'] = salary_min
        vacancy_data['max_salary'] = salary_max
        vacancy_data['currency'] = currency
        vacancy_data['employer'] = vacancy_corp
        vacancy_data['link'] = vacancy_href
        vacancy_data['site'] = sj_link
        
        new_vacancy(db.vac, vacancy_data)
        #vacancies.append(vacancy_data)

    i += 1 # следующая страница

#------------------------------------------------------------------------------------------
# Вставка данных собранным заранее списком - тут не используем т.к. нужна предварительная проверка на существование записи в базе,
# а это удобнее делать для каждой отдельной записи, чем удалять существующие записи из списка, а затем этот список целиком записывать.
#client = MongoClient( 'localhost' , 27017 )
#db = client['vacancy_db']
#db.vac.insert_many(vacancies)
#------------------------------------------------------------------------------------------
# Ищем ЗП не ниже введённой:
min_sal = float(input("\n\nВведите минимальный уровень зарплаты: "))
print("\nВакансии с минимальным искомым уровнем ЗП:", min_sal)

for item in find_salary(db.vac, min_sal):
    print(f"- от {item['min_salary']} до {item['max_salary']} - {item['name']}")

#------------------------------------------------------------------------------------------
print('\nКонец\n')