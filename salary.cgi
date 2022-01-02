#!/usr/bin/env python3

#import os
import sqlite3
import cgi
from datetime import datetime

y = datetime.now().strftime("%Y")
today = datetime.now().strftime("%d/%m/%Y %H:%M")

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
      <fieldset><legend><i><b>Ввод данных о зарплате</b></i></legend>
      <input type="text" name="payday" placeholder="Дата"><br>
      <input type="text" name="boss" placeholder="Босс"><br>
      <input type="text" name="amount_money" placeholder="Зарплата"><br>
      <input type="text" name="note" placeholder="Примечание"><br><br>
      <input type="submit" value="Записать"><br><br>
      <details><summary><i><b>Помощь по вводу</b></i></summary>
      <p>1. Дату писать в формате 'день/месяц/год'.<br>
      2. При незаполненных полях 'Дата' или 'Босс' записи в базу данных производиться не будут.<br>
      3. 'Зарплату' записывать только числами. Попытка записи иных знаков приведет к ошибке выполнения.<br>
      4. Если 'Примечание' не заполнено, его значением станет 'З/П'.<br> 
      5. Одни и те же данные, введённые дважды, будут записаны дважды. Редактирование записей не производится. Пишите внимательно. =)</p>
      </details></fieldset>
      </form>''')

print('<p><a href="timesheet.cgi">Календарь</a></p>')

sal = cgi.FieldStorage()
payday = sal.getfirst("payday") # Дата
boss = sal.getfirst("boss") # Босс
amount_money = sal.getfirst("amount_money") # Зарплата
note = sal.getfirst("note") # Примечание
if note == None:
    note = "З/П"

db_connect = sqlite3.connect(f'timesheet_{y}.db')

if (payday and boss):
    db = db_connect.cursor()
    db.execute('INSERT INTO salary (c_d, c_t, payday, boss, amount_money, note) VALUES (CURRENT_DATE, CURRENT_TIME, ?, ?, ?, ?);', 
               (str(payday), str(boss), str(amount_money), str(note)))
    db_connect.commit()
    db.close(); del db
    if amount_money:
        print(f'<p>Записано:   <i><b>{payday}</b></i> получено от <i>{boss}</i> <i><b>{amount_money}</b> ({note})</i></p>')

db_connect.close(); del db_connect

print('</body></html>')
