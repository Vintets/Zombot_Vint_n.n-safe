#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import time
logger = logging.getLogger(__name__)


name = 'conifer_user.txt'
# name = 'circus_user.txt'
# name = 'airplane_user.txt'

try:
    with open(name, 'r') as f:   
        spisok = eval(f.read())
except:
    print u'Файла нет'
    raw_input('-------------   END   ---------------')

#spisok = [1,2,3,4,5,3,4]
start = len(spisok)
print u'Начальная длина', start
result = list(set(spisok))
    
open(name, 'w').write(str(result))
print u'Конец. Дублей убрано: ', start-len(result)

raw_input('-------------   END   ---------------')
# cd C:\Python27\A_Python
# python No_duble.py


