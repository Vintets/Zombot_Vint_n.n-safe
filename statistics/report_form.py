#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import re
import sys
sys.path.append('../API')
import xlwt
import time
# import subprocess

limits = {
        '@COINS':200000,
        '@DUBLON':500,
        '@CR_47':50,
        '@CR_53':25,
        '@CR_68':25,
        '@CR_33':25,
        '@CR_11':150,
        '@CR_41':200,
        '@METAL_SCRAP':3000,
        '@S_34':300,
        '@CR_31':75,
        '@CR_29':25,
        '@CR_23':30,
        '@CR_17':25,
        '@R_33':3,
        '@CR_08':10,
        '@C_48':50,
        '@C_19':100,
        '@C_16':100,
        '@C_17':100,
        '@C_8':50,
        '@C_22':100
        }

"""        
Монеты                      @COINS      200000
Дублон                      @DUBLON     500

Сталь                       @CR_47     50
Болт                        @CR_53     25
Резина                      @CR_68     25
Синее сердце                @CR_33     25
Доска                       @CR_11     150
Брёвна пальмы               @CR_41     200
Металлолом                  @METAL_SCRAP  3000
Чёрная рука                 @S_34      300
Любовь                      @CR_31     75
Огонь                       @CR_29     25
Трансформатор               @CR_23     30
Супер-клей                  @CR_17     25
Альбом                      @R_33      3
Зелёная краска              @CR_08     10

Коллекция палача            C_48       50
Коллекция Анти-зомби        C_19       100
Коллекция Белого кролика    C_16       100
Коллекция Цветов            C_17       100
Строительная коллекция      C_8        50
Тинейджерская коллекция     C_22       100
"""

file_name = 'storage_united.xls'
pattern = r' ( )+'

def lit_col(col):
    if col > 25:
        lit = chr(64 + col // 26) + chr(65 + col % 26)
    else:
        lit = chr(65 + col)
    return lit

files = {}
for file in glob.glob(u'storage_*.txt'):
    # name = os.path.splitext(file)[0].lstrip('storage_')
    name = os.path.splitext(file)[0][8:]
    # print file
    # print name
    files[file] = name

alldata = {}
for file in files.keys():
    text = open(file, 'r').read().decode('utf-8')
    lines = text.split('\n')
    data = []
    for line in lines:
        if not line: continue
        rem = re.split(pattern, line)
        while rem.count(' '):
            rem.remove(' ')
        data.append(rem)
        # for word in rem:
            # print word,
        # print
    alldata[files[file]] = data
    # print

# print alldata
if not alldata: exit(0)
items = {}

if os.path.isfile(file_name):
    try:
        os.remove(file_name)
    except:
        print u'Файл заблокирован! Невозможно удалить старый.'
        raw_input('-------------   END   ---------------')

# Создаем книгу
book = xlwt.Workbook('utf8')
# Добавляем лист
sheet = book.add_sheet('Storage_Report')
# Высота строки
sheet.row(0).height = 2500
# Лист в положении "альбом"
sheet.portrait = False

style0 = xlwt.easyxf('font: name Arial, colour_index black, bold on, italic off; \
            align: wrap on, vert top, horiz center; \
            pattern: pattern solid, fore_colour gray25; \
            borders: top thin, bottom thin, left thin, right thin;')
style1 = xlwt.easyxf('font: name Arial, colour_index dark_blue, bold on, italic off; \
            align: wrap on, vert top, horiz center; \
            pattern: pattern solid, fore_colour gray25; \
            borders: top thin, bottom thin, left thin, right thin;')
style_left = xlwt.easyxf('font: name Arial, colour_index black, bold off, italic off; \
            align: wrap on, vert top, horiz left; \
            pattern: pattern solid, fore_colour white; \
            borders: top thin, bottom thin, left thin, right thin;')
style_right = xlwt.easyxf('font: name Arial, colour_index black, bold off, italic off; \
            align: wrap on, vert top, horiz right; \
            pattern: pattern solid, fore_colour white; \
            borders: top thin, bottom thin, left thin, right thin;')
style_center = xlwt.easyxf('font: name Arial, colour_index black, bold off, italic off; \
            align: wrap on, vert top, horiz center; \
            pattern: pattern solid, fore_colour white; \
            borders: top thin, bottom thin, left thin, right thin;')
style_right_red = xlwt.easyxf('font: name Arial, colour_index black, bold off, italic off; \
            align: wrap on, vert top, horiz right; \
            pattern: pattern solid, fore_colour rose; \
            borders: top thin, bottom thin, left thin, right thin;')
style_sum = xlwt.easyxf('font: name Arial, colour_index dark_blue, bold on, italic off; \
            align: wrap on, vert top, horiz right; \
            pattern: pattern solid, fore_colour light_turquoise; \
            borders: top thin, bottom thin, left thin, right thin;')
style_link = xlwt.easyxf('font: name Arial, colour_index blue, bold on, italic off, underline single; \
            align: wrap on, vert top, horiz center; \
            pattern: pattern solid, fore_colour white; \
            borders: top thin, bottom thin, left thin, right thin;')

# Ширина колонки
sheet.col(0).width = 5500
sheet.col(1).width = 3400

sheet.write(0, 0, u'Название', style0)
sheet.write(0, 1, u'Итого', style1)

row = 1
col = 1
for akk in alldata.keys():
    col += 1
    sheet.col(col).width = 3400
    sheet.write(0, col, akk, style0)
    for mat in alldata[akk]:
        if mat[1] in items.keys():
            str_ = items[mat[1]]
        else:
            items[mat[1]] = row
            sheet.write(row, 0, mat[0], style_left)
            # sheet.write(row, 1, mat[1], style_left)
            for i in range(2,col):
                sheet.write(row, i, ' ', style_right)
            str_ = row
            row += 1
        if int(mat[2]) == 0 or (mat[1] in limits.keys() and int(mat[2]) < limits[mat[1]]):
            sheet.write(str_, col, int(mat[2]), style_right_red)
        else:
            sheet.write(str_, col, int(mat[2]), style_right)

lit_end = lit_col(col)
for _str in range(1,row):
    sheet.write(_str, 1, xlwt.Formula('SUM(C'+str(_str+1) + ':' + lit_end+str(_str+1)+')'), style_sum)

book.save(file_name)     # Сохраняем в файл xls
print u'Отчёт составлен.'
time.sleep(0.5)

os.startfile(file_name)
# subprocess.call(file_name, shell=True)
# subprocess.Popen(file_name, shell=True)



# raw_input('-------------   END   ---------------')
# cd C:\Python27\Zombot_Vint_9.7++\statistics
# python report_form.py




