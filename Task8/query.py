'''     Урок 8. Работа с данными
3) Собранные данные необходимо сложить в базу данных. Структуру данных нужно заранее продумать, чтобы:
4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
'''

import pymongo
from pymongo import MongoClient
# --------------------------------------------------------------------------------------------------------------

def connect_db_col(db_name, col_name):
    conn = pymongo.MongoClient("localhost" , 27017)
    return conn[db_name][col_name]

# --------------------------------------------------------------------------------------------------------------

def followed(dbcol):
    return(dbcol.find({'type':'followed'},{'user_name':1}))

# --------------------------------------------------------------------------------------------------------------

def following(dbcol):
    return(dbcol.find({'type':'following'},{'user_name':1}))

#--------------------------------------------------------------------------------------------------------------

account = 'pupkin1021'
account = 'pupkin5267'

account = input('\nВведите имя учётки для которой вы хотите посмотреть подписчиков и подписки:\n')


dbcol = connect_db_col('InstaAccounts', account)

print(f'\nНа пользователя {account} подписаны:')
followed_users = followed(dbcol)
for itm in followed_users:
    print(f" - {itm['user_name']}")

print(f'\nПользователь {account} подписан на:')
following_users = following(dbcol)
for itm in following_users:
    print(f" - {itm['user_name']}")
