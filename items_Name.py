#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

itemn = []
true = 'true'
false = 'false'
with open('items.txt', 'r') as f:
    reader = eval(f.read())
    
im = []
for itm in reader:
    if ('id' and 'name') in itm:
        if itm['id'] in im: continue
        im.append(itm['id'])
        if 'shopImage' in itm:
            image = 'http://s.shadowlands.ru/zombievk-res/icons/' + itm['shopImage']
        elif 'postImage' in itm:
            image = 'http://s.shadowlands.ru/zombievk-res/icons/' + itm['postImage']
        elif 'storageImage' in itm:
            image = 'http://s.shadowlands.ru/zombievk-res/icons/' + itm['storageImage']
        elif 'image' in itm:
            image = 'http://s.shadowlands.ru/zombievk-res/icons/' + itm['image']
        else:
            image = ''
        itemn.append([itm['id'], itm['name'].decode('UTF-8', 'ignore'), image])

itemn.sort()
with open('items_name.txt', 'w') as f:
    #f.write(str(itemn))
    for itm in itemn:
        text = itm[0] + ' : ' + itm[1] + '\n'
        # text = itm[0] + ' : ' + itm[1] + ' : ' + itm[2] + '\n'
        f.write(text.encode("UTF-8", "ignore"))


# HTML
file_name = 'items_name.html'
first = '''<HTML>
<HEAD>
<TITLE>
Имена из items
</TITLE>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</HEAD>
<BODY bgcolor="#A0BEC4">
<table border="1" align="center" width="600">
<tbody>
<tr>
<td align="center"><b>Item</b></td>
<td align="center"><b>Name</b></td>
<td align="center"><b>Icon</b></td>
</tr>
'''
end = '''</table>

</BODY>
</HTML>
'''        
        
file_inst = open(file_name,'w')
file_inst.write(first)

print u'Всего элементов', len(itemn)
text = u'<p align="center"><b>Всего элементов: ' + str(len(itemn)) + '</b></p>'
file_inst.write(text.encode('UTF-8', 'ignore'))

for row in range(len(itemn)):
    # if row == 100: break
    url = itemn[row][2]
    print row, url
    file_inst.write('<tr>')
    file_inst.write('<td align="center"><nobr>' + itemn[row][0] + '</nobr></td>')
    name = '<td align="center"><nobr>' + itemn[row][1] + '</nobr></td>'
    file_inst.write(name.encode('UTF-8', 'ignore'))

    if url:
        if url[-4:] != '.png':
            url += '.png'
            print 'New URL', url

        file_inst.write('<td align="center">')
        file_inst.write('<img alt=' + itemn[row][0] +' src="' + url + '" border="0">')
        file_inst.write('</td>')
    else:
        file_inst.write('<td align="center"></td>')

    file_inst.write('</tr>\n')

file_inst.write(end) 
file_inst.close()
print u'Отчёт составлен.'
time.sleep(0.5)

os.startfile(file_name)


# raw_input('-------------   END   ---------------')
# cd C:\Python27\A_Python
# python items_Name.py

# 'shopImage':'decorations/m_coral_sphere_1.png'
# 'postImage':'missions/achievs/post/ACHIEV_02.png'
# 'storageImage':'crops/m_autumn_box1.png'
# 'image':'collections/war_chest.png'
