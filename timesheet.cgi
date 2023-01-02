#!/usr/bin/env python3

import cgi
import os
import calendar
import sqlite3
from datetime import datetime

salary_table = []
timesheet_table = []
timesheet_table_dict = {}
names_months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
names_days = ['пн','вт','ср','чт','пт','сб','вс']
y = datetime.now().strftime("%Y")
today = datetime.now().strftime("%d/%m/%Y %H:%M")
year = []
for i in range(1,13):
    year.append(calendar.monthcalendar(int(y), i)) # запись в 'year' всех дат года
tariff = 250.0 # тариф в час

print('Content-type: text/html')
print('')

print('''<!DOCTYPE html>
<head>
<meta content="noindex">
<meta charset="utf-8">
<title>Work Timesheet</title>
</head>
<body>''')

print(f'<p><i><b>{today}</b></i></p>')

# форма для записи данных о работе
print('''<form method="post">
<fieldset>
<legend><i><b>Ввод данных о работе</b></i></legend>
<input type="text" name="worked_date" placeholder="Дата   ">
<input type="text" name="boss" placeholder="Босс   "><br>
<input type="text" name="address" placeholder="Основной адрес   ">
<input type="text" name="added_address" placeholder="Дополнительный адрес   "> <input type="checkbox" name="change_location"><br>
<input type="text" name="hours" placeholder="Основные часы   ">
<input type="text" name="added_hours" placeholder="Дополнительные часы   "><br>
<input type="text" name="bonus" placeholder="Бонус   ">
<input type="text" name="fine" placeholder="Штраф   "><br><br>
<input type="submit" value="Записать"><br><br>
<details><summary><i><b>Помощь по вводу</b></i></summary>
        <p>
        1. Дату писать в формате 'день/месяц/год'. Более 1 раза для одной даты делать записи не получится. =)
        2. При незаполненном поле 'Дата' запись в базу данных произведена не будет.<br>
        3. Выходной день станет выходным только при записи русскими заглавными буквами. 
        В ином случае это станет основным адресом рабочего дня.<br>
        4. Все часы записывать только целыми или вещественными числами.
        Попытка записи иных знаков приведёт к ошибке выполнения.<br>
        5. Редактирование записей не производится. Пишите внимательно. =)
        </p>
</details>
</fieldset>
</form>''')

print('<p><a href="salary.cgi">Запись данных о З/П</a></p><br>')

if f'timesheet_{y}.db' not in os.listdir():
    db_connect = sqlite3.connect(f'timesheet_{y}.db')
    db = db_connect.cursor()
    db.execute('CREATE TABLE timesheet (c_d, c_t, worked_date, boss, address, added_address, hours, added_hours, bonus, fine, hlc);')
    db_connect.commit()
    db.execute('CREATE TABLE salary (c_d, c_t, payday, boss, amount_money, note);')
    db_connect.commit()
    db.close(); del db
    db_connect.close(); del db_connect

db_connect = sqlite3.connect(f'timesheet_{y}.db')

# запись и вывод данных о работе
work = cgi.FieldStorage()
w_date = work.getfirst('worked_date')
if w_date:
    w_date = w_date.split('/')
    worked_date = f'{w_date[2]}-{w_date[1]}-{w_date[0]}'
else:
    worked_date = None
boss = work.getfirst('boss')
if not boss:
    boss = "Неизвестен"
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
fine = work.getfirst('fine')
if not fine:
    fine = 0

hlc = 0 #hour_per_location_change, час за смену локации
if bool(work.getfirst('change_location')) == True:
    hlc += 1

def read_timesheet_table():
    global timesheet_table #wdb
    global timesheet_table_dict #wdb_dict
    db_read = db_connect.cursor()
    timesheet_table = db_read.execute('SELECT worked_date, boss, address, added_address, hours, added_hours, bonus, fine, hlc FROM timesheet;').fetchall()
    for i in timesheet_table:
        timesheet_table_dict[i[0]] = (i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]) # {date: tuple(boss, address, added_address, hours, added_hours, bonus, fine, hlc)}
    db_read.close(); del db_read
    return timesheet_table, timesheet_table_dict

read_timesheet_table()

if (worked_date != None and address != 'Нет') and (worked_date not in timesheet_table_dict.keys()):
    db_write = db_connect.cursor()
    db_write.execute('''INSERT INTO timesheet (c_d, c_t, worked_date, boss, address, added_address, hours, added_hours, bonus, fine, hlc) 
                        VALUES (CURRENT_DATE, CURRENT_TIME, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', 
                    (str(worked_date), str(boss), str(address), str(added_address), str(hours), str(added_hours), str(bonus), str(fine), str(hlc)))
    db_connect.commit()
    db_write.close(); del db_write

read_timesheet_table()

# таблица для вывода календаря
sum_year_hours = 0 # сумма часов за год
sum_year_rub = 0 # сумма рублей за год
sum_year_added_hours = 0 # сумма доп. часов за год
sum_year_added_rub = 0 # сумма доп. рублей за год
sum_year_bonus = 0 # сумма бонусов за год
sum_year_fine = 0 # сумма штрафов за год
sum_year_count_LC = 0 # количество смен локации за год
sum_year_worked_days = 0 # сумма рабочих дней за год
sum_year_holidays = 0 # сумма выходных дней за год
result_year_rub = 0 # результат (в рублях) за год

print('<hr size="2">')

print('<details><summary><i><b>Показать календарь</b></i></summary>') # Показать календарь
print('<table border="1" width="100%">')
month = (m for m in year)
for a in range(1, len(year)+1):
    sum_month_hours = 0 # сумма часов за месяц
    sum_month_rub = 0 # сумма основных рублей за месяц
    sum_month_added_hours = 0 # сумма дополнительных часов за месяц
    sum_month_added_rub = 0 # сумма дополнительных рублей за месяц
    sum_month_bonus = 0 # сумма бонусов за месяц
    sum_month_fine = 0 # сумма штрафов за месяц
    sum_month_count_LC = 0 # количество смен локации за месяц
    sum_month_worked_days = 0  # сумма выходных дней за месяц
    sum_month_holidays = 0 # сумма рабочих дней за месяц
    result_month = 0 # результат (в рублях) за месяц
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
                print(f'<p><i><b>{date_d}/{date_m}/{y}</b></i></p>')
                # сюда данные из БД
                for z in timesheet_table_dict.keys():
                    if f'{y}-{date_m}-{date_d}' == z:
                        timesheet_table_dict__boss = str(timesheet_table_dict[z][0])
                        timesheet_table_dict__address = str(timesheet_table_dict[z][1])
                        timesheet_table_dict__added_address = str(timesheet_table_dict[z][2])
                        timesheet_table_dict__hours = float(timesheet_table_dict[z][3])
                        timesheet_table_dict__hours_mul_tariff = timesheet_table_dict__hours * tariff
                        timesheet_table_dict__added_hours = float(timesheet_table_dict[z][4])
                        #timesheet_table_dict__count_hlc = 0
                        timesheet_table_dict__money_hlc = int(timesheet_table_dict[z][7]) * tariff # money_per_hlc (hour_location_change)
                        if timesheet_table_dict__money_hlc:
                            sum_month_count_LC += 1
                        timesheet_table_dict__added_hours_mul_tariff = timesheet_table_dict__added_hours * tariff
                        timesheet_table_dict__bonus = int(timesheet_table_dict[z][5])
                        timesheet_table_dict__fine = int(timesheet_table_dict[z][6])
                        result_day = timesheet_table_dict__hours_mul_tariff + timesheet_table_dict__added_hours_mul_tariff + timesheet_table_dict__bonus + timesheet_table_dict__money_hlc - timesheet_table_dict__fine
                        print(f'''<p><i>Босс:    <b>{timesheet_table_dict__boss}</b></i><br>
                                     <i>Адрес:   <br>
                                     <b>{timesheet_table_dict__address}</b></i><br>
                                     <i>Осн. часы:<br><b>{timesheet_table_dict__hours}</b> ({timesheet_table_dict__hours_mul_tariff})</i><br>
                                     <i>Доп. адрес:   <br>
                                     <b>{timesheet_table_dict__added_address}</b></i><br>
                                     <i>Доп. часы:<br><b>{timesheet_table_dict__added_hours}</b> ({timesheet_table_dict__added_hours_mul_tariff} + {timesheet_table_dict__money_hlc} (см. лок.))</i><br>
                                     <i>Бонус:   {timesheet_table_dict__bonus}</i><br>
                                     <i>Штраф:   {timesheet_table_dict__fine}</i><br>
                                     <i>Итог дня:   {result_day}</i></p>''')
                        sum_month_hours = sum_month_hours + timesheet_table_dict__hours
                        sum_month_rub = sum_month_rub + timesheet_table_dict__hours_mul_tariff
                        #result_month_rub = sum_month_rub + timesheet_table_dict__money_hlc
                        sum_month_added_hours = sum_month_added_hours + timesheet_table_dict__added_hours
                        sum_month_added_rub = sum_month_added_rub + timesheet_table_dict__added_hours_mul_tariff
                        sum_month_bonus = sum_month_bonus + timesheet_table_dict__bonus
                        sum_month_fine = sum_month_fine + timesheet_table_dict__fine
                        result_month = sum_month_rub + sum_month_added_rub + (sum_month_count_LC * tariff) + sum_month_bonus - sum_month_fine
                        if timesheet_table_dict__address == 'ВЫХОДНОЙ':
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
              <th>{sum_month_hours + sum_month_added_hours} всех час.<br>{sum_month_count_LC} см. лок.</th>
              <th>{sum_month_worked_days} раб. дней<br>{sum_month_holidays} вых. дней</th>
              </tr>''')
    print(f'''<tr>
              <th>{names_months[a-1]}<br>(бобы)</th>
              <th>{sum_month_rub} осн. руб.<br>{sum_month_fine} штрафов</th>
              <th>+</th>
              <th>{sum_month_added_rub} доп. руб.<br>и {sum_month_bonus} бонусов</th>
              <th>=</th>
              <th>{result_month}<br>всех руб.</th>
              <th>Тариф<br>{tariff} руб/час</th>
              </tr>''')
    sum_year_hours = sum_year_hours + sum_month_hours
    sum_year_rub = sum_year_rub + sum_month_rub
    sum_year_added_hours = sum_year_added_hours + sum_month_added_hours
    sum_year_added_rub = sum_year_added_rub + sum_month_added_rub
    sum_year_bonus = sum_year_bonus + sum_month_bonus
    sum_year_fine = sum_year_fine + sum_month_fine
    sum_year_count_LC = sum_year_count_LC + sum_month_count_LC
    sum_year_worked_days = sum_year_worked_days + sum_month_worked_days
    sum_year_holidays = sum_year_holidays + sum_month_holidays

print('</table>')
print('</details><br>') # Показать календарь

def read_salary_table():
    sdb = db_connect.cursor()
    global salary_table
    salary_table = sdb.execute('SELECT payday, boss, amount_money, note FROM salary;').fetchall()
    sdb.close(); del sdb
    return salary_table

read_salary_table()

sum_amount_money = 0
for i in salary_table:
    if i[2] != 'None':
        sum_amount_money = sum_amount_money + int(i[2])

print('<hr size="2">')
print(f'<details><summary><i><b>ИТОГО (за весь {y} год):</b></i></summary>') # ИТОГИ ГОДА
print('<p>-----------------------------')
print(f'''<p>ЗАРАБОТАНО:\n((ocн. руб.: {sum_year_rub}, доп. руб.: {sum_year_added_rub}, бонусы: {sum_year_bonus}, штрафы: {sum_year_fine}), смены локации ({sum_year_count_LC}): {sum_year_count_LC * tariff}),
             всего {(sum_year_rub + sum_year_added_rub + sum_year_bonus + (sum_year_count_LC * tariff)) - sum_year_fine} руб.)</p>''')
print('<p>-----------------------------</p>')
print('<p>ПОЛУЧЕНО:</p>')
remainder = sum_year_rub + sum_year_added_rub + sum_year_bonus + (sum_year_count_LC * tariff) - sum_year_fine
for i in salary_table:
    if i[1] != 'None':
        print(f'<p>{i[0]} <b>{i[2]}</b> ({i[3]}) от <i>{i[1]}</i>')
        remainder = remainder - int(i[2])
print('<p>-----------------------------</p>')
print(f'<p>ОСТАТОК:   <i><b>{remainder}</b></i></p>')
print('<p>-----------------------------</p>')
print(f'''<p>Рабочих дней:   {sum_year_worked_days} ((осн. час. {sum_year_hours}, доп. час. {sum_year_added_hours}), 
           всего {sum_year_hours + sum_year_added_hours} часов)</p>''')
print(f'<p>Выходных дней:   {sum_year_holidays}</p>')
print('</details><br>') # ИТОГИ ГОДА
print('<hr size="2">')
db_connect.close(); del db_connect
print('</body></html>')
