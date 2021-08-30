#!/usr/bin/env python3

import cgi
import os
import calendar
import sqlite3
from datetime import datetime

wdb = []
wdb_dict = {}
names_months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
names_days = ['пн','вт','ср','чт','пт','сб','вс']
y = datetime.now().strftime("%Y")
today = datetime.now().strftime("%d/%m/%Y %H:%M")
year = []
for i in range(1,13):
    year.append(calendar.monthcalendar(int(y), i)) # запись в 'year' всех дат года
tariff = 312.5 # тариф в час

print('Content-type: text/html')
print('')

print('''<!DOCTYPE html>
<head>
<meta content="noindex">
<meta charset="utf-8">
<title>Work Timesheet</title>
</head>
<body>''')

print(f'<h4>{today}</h4>')

print('<hr size="2">')

# форма для записи данных о работе
print('''<form method="post">
<fieldset>
<legend>Ввод данных о работе</legend>
<input type="text" name="worked_date" placeholder="Дата   "><br>
<input type="text" name="address" placeholder="Основной адрес   ">
<input type="text" name="added_address" placeholder="Дополнительный адрес   "><br>
<input type="text" name="hours" placeholder="Основные часы   ">
<input type="text" name="added_hours" placeholder="Дополнительные часы   "><br>
<input type="text" name="bonus" placeholder="Бонус   ">
<input type="text" name="boss" placeholder="Босс   "><br><br>
<input type="submit" value="Записать"><br><br>
<details><summary>Помощь по вводу</summary>
        <p>
        1. Дату писать в формате 'день/месяц/год'. Более 1 раза для одной даты делать записи не получится. =)
        При незаполненном поле 'Дата' запись в базу данных произведена не будет.<br>
        2. Выходной день станет выходным только при записи русскими заглавными буквами. 
        В ином случае это станет основным адресом рабочего дня.<br>
        3. Все часы записывать только целыми или вещественными числами.
        Попытка записи иных знаков приведёт к ошибке выполнения.<br>
        4. Редактирование записей не производится. Пишите внимательно. =)
        </p>
</details>
</fieldset>
</form><br>''')

if 'timesheet.db' not in os.listdir():
    db_connect = sqlite3.connect('timesheet.db')
    db = db_connect.cursor()
    db.execute('CREATE TABLE timesheet (worked_date, address, added_address, hours, added_hours, bonus, boss);')
    db_connect.commit()
    db.close(); del db
    db_connect.close(); del db_connect
db_connect = sqlite3.connect('timesheet.db')

# запись и вывод данных о работе
work = cgi.FieldStorage()
w_date = work.getfirst('worked_date')
if w_date:
    w_date = w_date.split('/')
    worked_date = f'{w_date[2]}-{w_date[1]}-{w_date[0]}'
else:
    worked_date = None
address = work.getfirst('address')
if not address:
    address = "Нет"
added_address = work.getfirst('added_address')
if not added_address:
    added_address = "Нет"
hours = work.getfirst('hours')
if not hours:
    hours = 0
added_hours = work.getfirst('added_hours')
if not added_hours:
    added_hours = 0
bonus = work.getfirst('bonus')
if not bonus:
    bonus = 0
boss = work.getfirst('boss')
if not boss:
    boss = "Неизвестен"

def read_db():
    global wdb
    global wdb_dict
    db_read = db_connect.cursor()
    wdb = db_read.execute('SELECT * FROM timesheet;').fetchall()
    for i in wdb:
        wdb_dict[i[0]] = (i[1], i[2], i[3], i[4], i[5], i[6])
    db_read.close(); del db_read
    return wdb, wdb_dict

read_db()

if (worked_date != None and address != 'Нет') and (worked_date not in wdb_dict.keys()):
    db_write = db_connect.cursor()
    db_write.execute('''INSERT INTO timesheet (worked_date, address, added_address, hours, added_hours, bonus, boss) 
                        VALUES (?, ?, ?, ?, ?, ?, ?);''', 
                    (str(worked_date), str(address), str(added_address), str(hours), str(added_hours), str(bonus), str(boss)))
    db_connect.commit()
    db_write.close(); del db_write

read_db()

# таблица для вывода календаря
sum_year_hours = 0 # сумма часов за год
sum_year_rub = 0 # сумма рублей за год
sum_year_added_hours = 0 # сумма доп. часов за год
sum_year_added_rub = 0 # сумма доп. рублей за год
sum_year_bonus = 0 # сумма бонусов за год
sum_year_worked_days = 0 # сумма рабочих дней за год
sum_year_holidays = 0 # сумма выходных дней за год

print('<hr size="2">')

print('<details><summary>Показать календарь</summary>')
print('<table border="1" width="100%">')
month = (m for m in year)
for a in range(1, len(year)+1):
    sum_month_hours = 0 # сумма часов за месяц
    sum_month_rub = 0 # сумма рублей за месяц
    sum_month_added_hours = 0 # сумма дополнительных часов за месяц
    sum_month_added_rub = 0 # сумма дополнительных рублей за месяц
    sum_month_bonus = 0 # сумма бонусов за месяц
    sum_month_worked_days = 0  # сумма выходных дней за месяц
    sum_month_holidays = 0 # сумма рабочих дней за месяц
    print('<tr>')
    for day in range(len(names_days)):
        if names_days[day] != 'сб' and names_days[day] != 'вс':
            print(f'<th bgcolor="green">{names_days[day]}</th>')
        else:
            print(f'<th bgcolor="brown">{names_days[day]}</th>')
    print('</tr>')
    month_next = month.__next__()
    week = (w for w in month_next)
    for b in range(len(month_next)):
        print('<tr>')
        week_next = week.__next__()
        for c in range(len(week_next)):
            if week_next[c] != 0:
                print('<td>')
                if week_next[c] < 10: date_d = '0' + str(week_next[c])
                else: date_d = str(week_next[c])
                if a < 10: date_m = '0' + str(a)
                else: date_m = str(a)
                print(f'<p><b>{date_d}/{date_m}/{y}</b></p>')
                # сюда данные из БД
                for z in wdb_dict.keys():
                    if f'{y}-{date_m}-{date_d}' == z:
                        wdb_dict__address = str(wdb_dict[z][0])
                        wdb_dict__added_address = str(wdb_dict[z][1])
                        wdb_dict__hours = float(wdb_dict[z][2])
                        wdb_dict__hours_mul_tariff = wdb_dict__hours * tariff
                        wdb_dict__added_hours = float(wdb_dict[z][3])
                        wdb_dict__added_hours_mul_tariff = wdb_dict__added_hours * tariff
                        wdb_dict__bonus = int(wdb_dict[z][4])
                        wdb_dict__boss = str(wdb_dict[z][5])
                        wdb_dict__result_day = wdb_dict__hours_mul_tariff + wdb_dict__added_hours_mul_tariff + wdb_dict__bonus
                        print(f'''<p><i>Адрес:   <br>
                                     <b>{wdb_dict__address}</b></i><br>
                                     <i>Осн. часы:   <b>{wdb_dict__hours}</b> ({wdb_dict__hours_mul_tariff})</i><br>
                                     <i>Доп. адрес:   <br>
                                     <b>{wdb_dict__added_address}</b></i><br>
                                     <i>Доп. часы:   <b>{wdb_dict__added_hours}</b> ({wdb_dict__added_hours_mul_tariff})</i><br>
                                     <i>Бонус:   {wdb_dict__bonus}</i><br>
                                     <i>Босс:    <b>{wdb_dict__boss}</b></i></p>
                                     <p><i>Итог дня:   {wdb_dict__result_day}</i></p>''')
                        sum_month_hours = sum_month_hours + wdb_dict__hours
                        sum_month_rub = sum_month_rub + wdb_dict__hours_mul_tariff
                        sum_month_added_hours = sum_month_added_hours + wdb_dict__added_hours
                        sum_month_added_rub = sum_month_added_rub + wdb_dict__added_hours_mul_tariff
                        sum_month_bonus = sum_month_bonus + wdb_dict__bonus
                        if wdb_dict__address == 'ВЫХОДНОЙ':
                            sum_month_holidays = sum_month_holidays + 1
                        else:
                            sum_month_worked_days = sum_month_worked_days + 1
                print('</td>')
            else:
                print('<td></td>')
        print('</tr>')
    print(f'''<tr>
              <th>{names_months[a-1]}<br>(часы и дни)</th>
              <th>{sum_month_hours}<br>осн. час.</th>
              <th>+</th>
              <th>{sum_month_added_hours}<br>доп.час.</th>
              <th>=</th>
              <th>{sum_month_hours + sum_month_added_hours}<br>всех час.</th>
              <th>{sum_month_worked_days} раб. дней<br>{sum_month_holidays} вых. дней</th>
              </tr>''')
    print(f'''<tr>
              <th>{names_months[a-1]}<br>(бобы)</th>
              <th>{sum_month_rub}<br>осн. руб.</th>
              <th>+</th>
              <th>{sum_month_added_rub} доп. руб.<br>и {sum_month_bonus} бонусов</th>
              <th>=</th>
              <th>{sum_month_rub + sum_month_added_rub + sum_month_bonus}<br>всех руб.</th>
              <th>Тариф<br>{tariff} руб/час</th>
              </tr>''')
    sum_year_hours = sum_year_hours + sum_month_hours
    sum_year_rub = sum_year_rub + sum_month_rub
    sum_year_added_hours = sum_year_added_hours + sum_month_added_hours
    sum_year_added_rub = sum_year_added_rub + sum_month_added_rub
    sum_year_bonus = sum_year_bonus + sum_month_bonus
    sum_year_worked_days = sum_year_worked_days + sum_month_worked_days
    sum_year_holidays = sum_year_holidays + sum_month_holidays
#print(f'{year}')

print('</table>')
print('</details><br>')

print('<hr size="2"')
print(f'<p>ИТОГО (за весь {y} год):</p>')
print(f'''<p>Заработанных денег:    ((ocн. руб.: {sum_year_rub}, доп. руб.: {sum_year_added_rub}, бонусов: {sum_year_bonus}), 
             всего {sum_year_rub + sum_year_added_rub + sum_year_bonus} руб.)</p>''')
print(f'''<p>Рабочих дней:   {sum_year_worked_days} ((осн. час. {sum_year_hours}, доп. час. {sum_year_added_hours}), 
           всего {sum_year_hours + sum_year_added_hours} часов)</p>''')
print(f'<p>Выходных дней:   {sum_year_holidays}</p>')

db_connect.close(); del db_connect
print('</body></html>')
