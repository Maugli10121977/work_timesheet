#!/usr/bin/env python3

import os
import sqlite3
import cgi
from datetime import datetime

y = datetime.now().strftime("%Y")
today = datetime.now().strftime("%d/%m/%Y %H:%M")

if f'salary_{y}.db' not in os.listdir():
    db_connect = sqlite3.connect(f'salary_{y}.db')
    db = db_connect.cursor()
    db.execute('CREATE TABLE salary (c_d, c_t, payday, boss, amount_money);')
    db_connect.commit()
    db.close(); del db
    db_connect.close(); del db_connect

print('Content-type: text/html')
print('')

print('''<!DOCTYPE html>
<head>
<meta content="noindex">
<meta charset="utf-8">
<title>WRITE SALARY</title>
</head>
<body>''')

print(f'<p><i><b>{today}</b></i></p>')

print('''<form method="post">
      <fieldset><legend>Ввод данных о зарплате</legend>
      <input type="text" name="payday" placeholder="Дата"><br>
      <input type="text" name="boss" placeholder="Босс"><br>
      <input type="text" name="amount_money" placeholder="Зарплата"><br><br>
      <input type="submit" value="Записать"><br><br>
      <details><summary>Помощь по вводу</summary>
      <p>1. Дату писать в формате 'день/месяц/год'.<br>
      2. При незаполненных полях 'Дата' или 'Босс' записи в базу данных производиться не будут.<br>
      3. 'Зарплату' записывать только числами. Попытка записи иных знаков приведет к ошибке выполнения.<br>
      4. Редактирование записей не производится. Пишите внимательно. =)</p>
      </details></fieldset>
      </form>''')

print('<p><a href="timesheet.cgi">Календарь</a></p>')

sal = cgi.FieldStorage()
payday = sal.getfirst("payday") # Дата
boss = sal.getfirst("boss") # Босс
amount_money = sal.getfirst("amount_money") # Зарплата

db_connect = sqlite3.connect(f'salary_{y}.db')

wdb = []
def read_db(wdb):
    db = db_connect.cursor()
    wdb = db.execute('SELECT payday, boss, amount_money FROM salary;').fetchall()
    db.close(); del db
    return wdb

read_db(wdb)

all_paydays = []
all_bosses = []
all_amount_money = []
for i in wdb:
    all_paydays.append(i[0])
    all_bosses.append(i[1])
    all_amount_money.append(i[2])

if (payday and boss):
    db = db_connect.cursor()
    db.execute('INSERT INTO salary (c_d, c_t, payday, boss, amount_money) VALUES (CURRENT_DATE, CURRENT_TIME, ?, ?, ?);', 
               (str(payday), str(boss), str(amount_money)))
    db_connect.commit()
    db.close(); del db
    read_db(wdb)
    if amount_money:
        print(f'<p>Записано:   <i><b>{payday}</b></i> получено от <i>{boss}</i> <i><b>{amount_money}</b></i></p>')

print('</body></html>')
