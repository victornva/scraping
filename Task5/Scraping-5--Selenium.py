''' Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и 
    сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172
'''
#---------------------------------------------------------------------------------------------------------------
import time
from pprint import pprint
from pymongo import MongoClient

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#---------------------------------------------------------------------------------------------------------------
print('Начало\n')

chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://mail.ru/')

login = driver.find_element_by_id('mailbox:login-input')
login.send_keys('study.ai_172')
login.send_keys(Keys.ENTER)

time.sleep(1)

passw = driver.find_element_by_id('mailbox:password-input')
passw.send_keys('NextPassword172')
passw.send_keys(Keys.ENTER)

time.sleep(3) # тут проще подобрать задержку т.к. это единичная оперция 

#---------------------------------------------------------------------------------------------------------------
mail_links = set() # множество для добавления ссылок на письма:
                   # т.к. при скроллинге к последнему письму на странице список писем обновляется не полностью (странно но это так)
                   # дабы исключить дублирование мы пишем их в множество

emails = []        # список куда будем заносить данные писем для последующей записи в базу

last_letter = ''
pages = 1

while True: #pages == 1:

    letters = driver.find_elements_by_class_name('js-letter-list-item')
    # проверяем совпадает ли последнее письмо на текущей странице с последним на предыдущей - если да то это последняя, выходим из цикла
    if last_letter == letters[-1].text:
        print('THE END')
        break
    #print('\n----------------------- Страница: ', pages)
    # перебираем письма на открывшейся странице Входящие и считываем ссылки на каждое письмо
    for letter in letters:
        #print(letter.text)
        mail_links.add(letter.get_attribute('href')) # добавляем в множество

    # запоминаем последнее письмо на странице - сравним его с последним письмом на следующей
    last_letter = letters[-1].text
    # переходим на последнее письмо вызывая сдвиг страницы     
    actions = ActionChains(driver)
    actions.move_to_element(letters[-1]).perform()

    pages += 1

# открываем каждое письмо по сохранённой в множестве уникальной ссылке и считываем данные
for em in mail_links:
    # берём ссылку и подгружаем письмо
    driver.get(em)
    # словарь для собранных данных
    email_data = {}
    # Писем может быть много, а на скорость открытия каждой ссылки влияет скорость интернета, скорость компьютера 
    # на котором запускается наш скрапер, нагрузка на сайт и много ещё чего...
    # Я терял много времени с отладкой на не очень быстром ноутбуке с интернетом через телефон, но потом решил эту проблему
    # перенеся отладку на мощную виртуалку с гигабитным каналом в дата-центре - всё понеслось со страшной силой!
    # Тем не менее в этом месте задержки лучше минимизировать т.к. итераций может быть много - применим WebDriverWait
    #time.sleep(5)
    #message = driver.find_element_by_class_name('letter-body').text)
    email_data['message'] = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,'letter-body'))).text
    email_data['contact'] = driver.find_element_by_class_name('letter-contact').text
    email_data['date'] = driver.find_element_by_class_name('letter__date').text
    email_data['subj'] = driver.find_element_by_class_name('thread__subject-line').text

    emails.append(email_data)
    #exit()
    pprint(email_data)

#pprint(emails)
#print('\n\n Писем всего: ', len(mail_links))
#------------------------------------------------------------------------------------------
# Подключаемся к БД и пишем данные все за раз:
client = MongoClient( 'localhost' , 27017 )
db = client['mail_db']
# db.letters.drop()
db.letters.insert_many(emails)
#------------------------------------------------------------------------------------------
print('\nКонец\n')