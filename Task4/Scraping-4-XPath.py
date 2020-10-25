'''
Урок 4. Парсинг HTML. XPath
Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости. 
Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
Сложить собранные данные в БД
'''
import requests
from lxml import html
from pprint import pprint
from pymongo import MongoClient
from datetime import datetime, date, time
#--------------------------------------------------------------------------------------------------------------
def new_news(dbcol, ident):
    '''
    ф-ция проверяет наличие записи в БД по совпадению строки-критерия
    :param dbcol: ссылка на коллекцию в БД MongoDB
    :param ident: строка-критерий
    '''
    if dbcol.find_one({'title':ident}) == None:
        return False
    else:
        return True
#--------------------------------------------------------------------------------------------------------------
print('\nНачало\n')

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.1.112 Yowser/2.5 Safari/537.36'}
#------------------------------------------------------------------------------------------
# Подключаемся к БД
client = MongoClient( 'localhost' , 27017 )
db = client['news_db']
# db.news.drop()
#---------------------------------------------------------------------------------------------------------------
news = []  # свежие новости будем записывать в ссписок, а затем записывать его в базу

# т.к. по каждому сайту мы выполняем практически однотипные операции, то будем обходить наши сайты в цикле, 
# а данные каждого сайта брать из списка словарей
news_sites = [
              {"site":"https://lenta.ru", 
               "title":"//div[@class='span4']/div[@class='item']/a/text() | //div[@class='first-item']/h2/a/text()",
               "link":"//div[@class='span4']/div[@class='item']/a/@href | //div[@class='first-item']/h2/a/@href",
               "date":"//div[@class='item']/a/time/@datetime | //div[@class='first-item']/h2/a/time/@datetime"},
              {"site":"https://news.mail.ru/",
               "title":"//td[@class='daynews__main']//span[1]/text() | //div[@class='daynews__item']//span/text() | //li[@class='list__item']/a/text()",
               "link":"//td[@class='daynews__main']//a/@href | //div[@class='daynews__item']/a/@href | //li[@class='list__item']/a/@href",
               "date":"//td[@class='daynews__main']//a/@href | //div[@class='daynews__item']/a/@href | //li[@class='list__item']/a/@href"},
              {"site":"https://yandex.ru/news/",
               "title":"//div[@class='mg-grid__row mg-grid__row_gap_8 news-top-stories news-app__top']//h2/text()",
               "link":"//div[@class='mg-grid__row mg-grid__row_gap_8 news-top-stories news-app__top']//span/a/@href",
               "date":"//div[@class='mg-grid__row mg-grid__row_gap_8 news-top-stories news-app__top']//span[@class='mg-card-source__time']/text()"}
             ]

for site in news_sites:
    main_link = site["site"]
    
    responce = requests.get(main_link, headers = headers)
    dom = html.fromstring(responce.text)

    title = dom.xpath(site["title"])
    link = dom.xpath(site["link"])
    date = dom.xpath(site["date"])

    # перебираем полученные с каждого сайта данные:
    i = 0
    for item in title:
        # даты на всех сайтах указывают по-разному, и нужно их привести к общему формату datetime
        if main_link == "https://lenta.ru":
            # тут месяц указан по-русски, и проще время взять с сайта а дату взять текущую (мы же берём свежие новости!;)
            date[i] = datetime.strptime(str(datetime.now().date()) + date[i].split(',')[0], "%Y-%m-%d %H:%M")
            # на этом сайте ссылки указываются без домена, но не всегда - скорректируем
            if not link[i].startswith('https'):
                link[i] = 'https://lenta.ru' + link[i]

        if main_link == "https://news.mail.ru/":
            # тут метку даты и времени вообще найти не удалось - ставим текущие
            date[i] = datetime.now()

        if main_link == "https://yandex.ru/news/":
            # тут указано только время - берём его, а дату текущую
            date[i] = datetime.strptime(str(datetime.now().date()) + str(date[i]), '%Y-%m-%d%H:%M')

        # заполняем словарь с данными по каждой новости
        news_data = {}
        news_data['title'] = title[i]
        news_data['link'] = link[i]
        news_data['date'] = date[i]
        news_data['site'] = main_link
        
        # проверяем есть ли такая новость в базе по уникальной ссылке, и если нет - добавляем в список 
        if new_news(db.news, news_data['title']) == False:
            news.append(news_data)

        i += 1

#---------------------------------------------------------------------------------------------------------------
# если новые новости есть - добавляем их в базу 
if news:
    pprint(news)
    db.news.insert_many(news)
#------------------------------------------------------------------------------------------

print('\nКонец\n')