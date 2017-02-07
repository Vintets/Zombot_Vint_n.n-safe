# coding=utf-8
import logging
import xlwt
import datetime
import time
import vkontakte.api
from hashlib import md5
# from game_state.connection import Connection
import random as random_number
from game_state.base import BaseActor

logger = logging.getLogger(__name__)

class ActiveUser(BaseActor):
    def perform_action(self):
        self.friends = self.get_friendsid()
        self.data = [datetime.date.today().strftime('%Y.%m.%d'), datetime.date.today().strftime('%j')]
        self.new = False
        self.curuser = str(self._get_game_state().get_curuser())
        
        # грузим friends_active_game.txt
        if not hasattr(self._get_game_state(),'friends_active_game'):
            self.load_friends_active_game()
        
        # обновляем инфу по бродящим друзьям
        self.check_active_gost()
        
        # обновляем инфу по стукам в чудовище
        self.check_active_monster()
        
        # обновляем инфу по стукам в ёлки
        self.check_active_newYearTree()
        
        # обновляем по присланным подаркам
        self.check_active_gift()
        
        # обновляем инфу по возможности копать
        self.check_active_haveTreasure()
        
        # были изменения, запись в файл
        if self.new:
            logger.info(u'Обновляем инфу о активности друзей...')
            with open('statistics\\'+self.curuser+'\\friends_active_game.txt', 'w') as f:
                f.write(str(self._get_game_state().friends_active_game))

        
    def load_friends_active_game(self):
        try:
            with open('statistics\\'+self.curuser+'\\friends_active_game.txt', 'r') as f:
                self._get_game_state().friends_active_game = eval(f.read())
        except:
            self._get_game_state().friends_active_game = {}
        for friends_id in self.friends:
            self._get_game_state().friends_active_game.setdefault(friends_id, ['0', '0'])
        with open('statistics\\'+self.curuser+'\\friends_active_game.txt', 'w') as f:
            f.write(str(self._get_game_state().friends_active_game))

    def check_active_gost(self):
        count = 0
        for player in self._get_game_state().get_state().location.guestInfos:
            #print 'guestInfos user', player.userId
            if self._get_game_state().friends_active_game.get(str(player.userId)) != self.data:
                self._get_game_state().friends_active_game[str(player.userId)] = self.data
                self.new = True
                count += 1
        if count > 0:
            logger.info(u'Обновление активных посетителей %d' % (count))

    def check_active_monster(self):
        monster = self._get_game_location().get_all_objects_by_type('monsterPit')
        if (len(monster) == 0): return
        count = 0
        if monster[0].state == 'DIGGING':
            for player in monster[0].users:
                #print 'Monster user', player.user
                if self._get_game_state().friends_active_game.get(str(player.user)) != self.data:
                    self._get_game_state().friends_active_game[str(player.user)] = self.data
                    self.new = True
                    count += 1
        if count > 0:
            logger.info(u'Обновление активных закапывателей медведя %d' % (count))

    def check_active_newYearTree(self):
        trees = self._get_game_location().get_all_objects_by_type('newYearTree')
        count = 0
        for tree in trees:
            if not ('B_SPRUCE_' in tree.item): continue
            for player in tree.users:
                #print 'NewYearTree user', player.id
                if self._get_game_state().friends_active_game.get(str(player.id)) != self.data:
                    self._get_game_state().friends_active_game[str(player.id)] = self.data
                    self.new = True
                    count += 1
        if count > 0:
            logger.info(u'Обновление активных дарителей стучащих в ёлки %d' % (count))

    def check_active_gift(self):
        count = 0
        for gift in set(self._get_game_state().get_state().gifts):
            if gift.user == u'zfadmin': continue
            if self._get_game_state().friends_active_game.get(str(gift.user)) != self.data:
                self._get_game_state().friends_active_game[str(gift.user)] = self.data
                self.new = True
                count += 1
        if count > 0:
            logger.info(u'Обновление активных дарителей подарков %d' % (count))

    def check_active_haveTreasure(self):
        if not hasattr(self._get_game_state(), 'playersInfo'): return
        count = 0
        for player in self._get_game_state().playersInfo:
            txt = self._get_game_state().friends_active_game.get(str(player.id))
            if player.liteGameState.haveTreasure and txt != self.data:
                self._get_game_state().friends_active_game[str(player.id)] = self.data
                self.new = True
                count += 1
        if count > 0:
            logger.info(u'Обновление активных зелёных друзей %d' % (count))


        
class FinalReportUserMR(BaseActor):  # FinalReportUserMR
    def perform_action(self):
        self.curuser = str(self._get_game_state().get_curuser())
        self.report()
        raw_input('-------------   END   ---------------')
        
    def report(self):
        if not hasattr(self._get_game_state(), 'playersInfo'): return
        players_info = self._get_game_state().playersInfo

        try:
            with open('statistics\\'+self.curuser+'\\perron.txt', 'r') as f:
                perron_list = eval(f.read())
        except:
            perron_list = []
            print u"Нет файла 'perron.txt' с перронами. Информация о перронах не попадёт в отчёт."

        try:
            with open('statistics\\'+self.curuser+'\\baduser.txt', 'r') as f:
                baduser_list = eval(f.read())
        except:
            baduser_list = []
            print u"Нет файла 'baduser.txt' с друзьями к которым не получается зайти."

        try:
            with open('statistics\\'+self.curuser+'\\friends_active_game.txt', 'r') as f:
                friends_active_game = eval((f.read()))
        except:
            friends_active_game = {}
            print u"Нет файла 'friends_active_game' с информацией о активности друзей."
            return
            
        try:
            with open('statistics\\'+self.curuser+'\\friends_all_info.txt', 'r') as f:
                friends_all_info = (f.read()).decode('UTF-8')
                friends_all_info = eval(friends_all_info)
        except:
            friends_all_info = {}
        if friends_all_info == {} or friends_all_info == None:
            print u"Нет файла 'friends_all_info.txt' с информацией о друзьях."
            return

        current_time = int(time.time())
        #print u'Текущее время', current_time

        # заполняем шапку TXT
        target = open('statistics\\'+self.curuser+'\\Users_Info.txt', 'w')
        zagolovok = u''
        zagolovok += u'id\t'                    # id
        zagolovok += u'Имя\t'                   # Name
        zagolovok += u'Имя в игре\t'            # Game_Name
        zagolovok += u'Открыть в браузере\t'    # URL

        zagolovok += u'Не был в М.Мире, дней\t'                     # Last_visit
        zagolovok += u'Был дней назад\t'                            # AccessDate
        zagolovok += u'Последняя замеченная активность в ZF\t'      # Active_date
        zagolovok += u'Последняя активность (день года)\t'          # Active_day

        zagolovok += u'ZF\t'                    # app_installed
        zagolovok += u'Уровень\t'               # Level
        #zagolovok += u'Опыта\t'                # Exp
        zagolovok += u'Статус\t'                # Status
        zagolovok += u'Баня\t'                  # Banned
        zagolovok += u'Перрон\t'                # Perron
        zagolovok += u'Нельзя зайти\t'          # Error_load
        zagolovok += u'Ссылка'                  # Link
        zagolovok += u'\n'
        
        target.write(zagolovok.encode('UTF-8'))
        target.close()
        target = open('statistics\\'+self.curuser+'\\Users_Info.txt', 'a')
        
        # заполняем шапку XLS
        # Создаем книгу
        book = xlwt.Workbook('utf8')
        # Добавляем лист
        sheet = book.add_sheet('Frends_Report')
        # Высота строки
        sheet.row(0).height = 2500
        # Лист в положении "альбом"
        sheet.portrait = False
        style0 = xlwt.easyxf('font: name Arial,colour_index black, bold on,italic off; align: wrap on, vert top, horiz center;pattern: pattern solid, fore_colour gray25; borders: top thin, bottom thin, left thin, right thin;')
        style_left = xlwt.easyxf('font: name Arial,colour_index black, bold off,italic off; align: wrap on, vert top, horiz left;pattern: pattern solid, fore_colour white; borders: top thin, bottom thin, left thin, right thin;')
        style_right = xlwt.easyxf('font: name Arial,colour_index black, bold off,italic off; align: wrap on, vert top, horiz right;pattern: pattern solid, fore_colour white; borders: top thin, bottom thin, left thin, right thin;')
        style_center = xlwt.easyxf('font: name Arial,colour_index black, bold off,italic off; align: wrap on, vert top, horiz center;pattern: pattern solid, fore_colour white; borders: top thin, bottom thin, left thin, right thin;')
        row = 0

        # Ширина колонки
        sheet.col(0).width = 5500  #2300
        sheet.col(1).width = 6500
        sheet.col(2).width = 4500
        sheet.col(3).width = 2500
        sheet.col(4).width = 2500
        sheet.col(5).width = 3000
        sheet.col(6).width = 4300
        sheet.col(7).width = 3000
        sheet.col(8).width = 1000
        #sheet.col(9).width = 650
        #sheet.col(10).width = 650
        #sheet.col(11).width = 650
        sheet.col(12).width = 2000
        #sheet.col(13).width = 650
        sheet.col(14).width = 11300

        sheet.write(0, 0, u'id', style0)
        sheet.write(0, 1, u'Имя', style0)
        sheet.write(0, 2, u'Имя в игре', style0)
        sheet.write(0, 3, u'Открыть в браузере', style0)
        sheet.write(0, 4, u'Не был в М.Мире, дней', style0)
        sheet.write(0, 5, u'Был дней назад', style0)
        sheet.write(0, 6, u'Последняя замеченная активность в ZF', style0)
        sheet.write(0, 7, u'Последняя активность (день года)', style0)
        sheet.write(0, 8, u'ZF', style0)
        sheet.write(0, 9, u'Уровень', style0)
        sheet.write(0, 10, u'Статус', style0)
        sheet.write(0, 11, u'Баня', style0)
        sheet.write(0, 12, u'Перрон', style0)
        sheet.write(0, 13, u'Нельзя зайти', style0)
        sheet.write(0, 14, u'Ссылка', style0)        

        for frend_id in friends_all_info.keys():
            #{"first_name": "Клондайк", "last_name": "Сити", "last_visit": "1412281333", "app_installed": 1, "nick": "Клондайк", "link": "http://my.mail.ru/mail/scorpion101188/"}
            row += 1
            first_name = (self._correct(friends_all_info[frend_id]['first_name'])).decode('UTF-8', "ignore")
            last_name = (self._correct(friends_all_info[frend_id]['last_name'])).decode('UTF-8', "ignore")
            last_visit = str(int((current_time - int(friends_all_info[frend_id]['last_visit']))/86400))     # 5 дней
            app_installed = bool(friends_all_info[frend_id]['app_installed'])
            if app_installed:
                app_installed = u'ZF'
            else:
                app_installed = u''
            nick = (self._correct(friends_all_info[frend_id]['nick'])).decode('UTF-8', "ignore")
            link = friends_all_info[frend_id]['link']
            elink = u'HYPERLINK("' + link + u'";"' + link + '")'
            #hyperlink = u'ГИПЕРССЫЛКА("' + link + u'";"перейти")'
            hyperlink = u'HYPERLINK("' + link + u'";"перейти")'
            game_name = u''
            accessDate = u''
            level = u''
            exp = u''
            status = u''
            banned = u''
            perron = u''
            baduser = u''

            for n in players_info:
                if n.id == frend_id:
                    if hasattr(n, 'name'):
                        nam = (n.name).encode("UTF-8", "ignore")
                        game_name = (self._correct(nam)).decode('UTF-8', "ignore")
                    if hasattr(n, 'accessDate'): accessDate = str(long(n.accessDate)/86400000)
                    level = str(n.level)
                    exp = str(n.exp)
                    status = n.playerStatus[4:] # ZOMBIE/HUMAN
                    if str(n.banned) == 'True': banned = 'banned'
                    break

            if frend_id in perron_list: perron = 'perron'
            if frend_id in baduser_list: baduser = 'NoLoad'
            try:
                active_date = friends_active_game[frend_id][0]
                active_day = friends_active_game[frend_id][1]
            except:
                active_date = ''
                active_day = ''

            text = u''
            text += frend_id + u'\t'
            text += first_name + u' ' + last_name + u'\t'
            text += game_name + u'\t'
            text += u'=' + hyperlink + u'\t'       

            text += last_visit + u'\t'
            text += accessDate + u'\t'
            text += active_date + u'\t'
            text += active_day + u'\t'

            text += app_installed + u'\t'
            text += level + u'\t'
            #text += exp + u'\t'
            text += status + u'\t'
            text += banned + u'\t'
            text += perron + u'\t'
            text += baduser + u'\t'
            
            text += u'=' + elink + u'\t'
            text += u'\n'

            target.write(text.encode("UTF-8", "ignore"))

            # заносим в xls
            sheet.write(row, 0, frend_id, style_left)
            sheet.write(row, 1, first_name + u' ' + last_name, style_left)
            sheet.write(row, 2, game_name, style_left)
            sheet.write(row, 3, xlwt.Formula(hyperlink), style_center)
            sheet.write(row, 4, last_visit, style_right)
            sheet.write(row, 5, accessDate, style_center)
            sheet.write(row, 6, active_date, style_center)
            sheet.write(row, 7, active_day, style_right)
            sheet.write(row, 8, app_installed, style_center)
            sheet.write(row, 9, level, style_center)
            sheet.write(row, 10, status, style_center)
            sheet.write(row, 11, banned, style_center)
            sheet.write(row, 12, perron, style_center)
            sheet.write(row, 13, baduser, style_center)
            sheet.write(row, 14, xlwt.Formula(elink), style_left)
            sheet.row(row).height = 625

        target.close()
        book.save('statistics\\'+self.curuser+'\\Users_Info.xls')     # Сохраняем в файл xls
        print u'Отчёт составлен.'
        time.sleep(3)

    def _correct(self, name_):
        # print 'type name_', type(name_)
        # print 'name_',  name_
        while '{' in name_ or '}' in name_ or '[' in name_ or ']' in name_ or '^' in name_ or '&' in name_ or '†' in name_ or '✔' in name_:
            for l in '{}[]^&†✔':
                name_ = name_.replace(l, '')
        if '\u0456' in name_:
            name_ = name_.replace('\u0456', u'i')
        return name_

class FinalReportUserVK(BaseActor):  # FinalReportUserVK
    def perform_action(self):
        self.curuser = str(self._get_game_state().get_curuser())
        self.report()

    def report(self):
        if not hasattr(self._get_game_state(), 'playersInfo'): return
        players_info = self._get_game_state().playersInfo

        try:
            with open('statistics\\'+self.curuser+'\\perron.txt', 'r') as f:
                perron_list = eval(f.read())
        except:
            perron_list = []
            print u"Нет файла 'perron.txt' с перронами. Информация о перронах не попадёт в отчёт."

        try:
            with open('statistics\\'+self.curuser+'\\baduser.txt', 'r') as f:
                baduser_list = eval(f.read())
        except:
            baduser_list = []
            print u"Нет файла 'baduser.txt' с друзьями к которым не получается зайти."

        try:
            with open('statistics\\'+self.curuser+'\\friends_active_game.txt', 'r') as f:
                friends_active_game = eval((f.read()))
        except:
            friends_active_game = {}
            print u"Нет файла 'friends_active_game' с информацией о активности друзей."
            return

        try:
            with open('statistics\\'+self.curuser+'\\friends_all_infoVK.txt', 'r') as f:
                friends_all_info = (f.read()).decode('UTF-8')
                friends_all_info = eval(friends_all_info)
        except:
            friends_all_info = {}
        if friends_all_info == {} or friends_all_info == None:
            print u"Нет файла 'friends_all_info.txt' с информацией о друзьях."
            return

        current_time = int(time.time())
        #print u'Текущее время', current_time

        # заполняем шапку TXT
        target = open('statistics\\'+self.curuser+'\\Users_Info.txt', 'w')
        zagolovok = u''
        zagolovok += u'id\t'                    # id
        zagolovok += u'Имя\t'                   # Name
        zagolovok += u'Имя в игре\t'            # Game_Name
        zagolovok += u'Открыть в браузере\t'    # URL

        zagolovok += u'Не был в М.Мире, дней\t'                     # Last_visit
        zagolovok += u'Был дней назад\t'                            # AccessDate
        zagolovok += u'Последняя замеченная активность в ZF\t'      # Active_date
        zagolovok += u'Последняя активность (день года)\t'          # Active_day

        zagolovok += u'ZF\t'                    # app_installed
        zagolovok += u'Уровень\t'               # Level
        #zagolovok += u'Опыта\t'                # Exp
        zagolovok += u'Статус\t'                # Status
        zagolovok += u'Баня\t'                  # Banned
        zagolovok += u'Перрон\t'                # Perron
        zagolovok += u'Нельзя зайти\t'          # Error_load
        zagolovok += u'Ссылка'                  # Link
        zagolovok += u'\n'
        
        target.write(zagolovok.encode('UTF-8'))
        target.close()
        target = open('statistics\\'+self.curuser+'\\Users_Info.txt', 'a')
        
        # заполняем шапку XLS
        # Создаем книгу
        book = xlwt.Workbook('utf8')
        # Добавляем лист
        sheet = book.add_sheet('Frends_Report')
        # Высота строки
        sheet.row(0).height = 2500
        # Лист в положении "альбом"
        sheet.portrait = False
        style0 = xlwt.easyxf('font: name Arial,colour_index black, bold on,italic off; align: wrap on, vert top, horiz center;pattern: pattern solid, fore_colour gray25; borders: top thin, bottom thin, left thin, right thin;')
        style_left = xlwt.easyxf('font: name Arial,colour_index black, bold off,italic off; align: wrap on, vert top, horiz left;pattern: pattern solid, fore_colour white; borders: top thin, bottom thin, left thin, right thin;')
        style_right = xlwt.easyxf('font: name Arial,colour_index black, bold off,italic off; align: wrap on, vert top, horiz right;pattern: pattern solid, fore_colour white; borders: top thin, bottom thin, left thin, right thin;')
        style_center = xlwt.easyxf('font: name Arial,colour_index black, bold off,italic off; align: wrap on, vert top, horiz center;pattern: pattern solid, fore_colour white; borders: top thin, bottom thin, left thin, right thin;')
        row = 0

        # Ширина колонки
        sheet.col(0).width = 5500  #2300
        sheet.col(1).width = 6500
        sheet.col(2).width = 4500
        sheet.col(3).width = 2500
        sheet.col(4).width = 2500
        sheet.col(5).width = 3000
        sheet.col(6).width = 4300
        sheet.col(7).width = 3000
        sheet.col(8).width = 1000
        #sheet.col(9).width = 650
        #sheet.col(10).width = 650
        #sheet.col(11).width = 650
        sheet.col(12).width = 2000
        #sheet.col(13).width = 650
        sheet.col(14).width = 11300

        sheet.write(0, 0, u'id', style0)
        sheet.write(0, 1, u'Имя', style0)
        sheet.write(0, 2, u'Имя в игре', style0)
        sheet.write(0, 3, u'Открыть в браузере', style0)
        sheet.write(0, 4, u'Не был в М.Мире, дней', style0)
        sheet.write(0, 5, u'Был дней назад', style0)
        sheet.write(0, 6, u'Последняя замеченная активность в ZF', style0)
        sheet.write(0, 7, u'Последняя активность (день года)', style0)
        sheet.write(0, 8, u'ZF', style0)
        sheet.write(0, 9, u'Уровень', style0)
        sheet.write(0, 10, u'Статус', style0)
        sheet.write(0, 11, u'Баня', style0)
        sheet.write(0, 12, u'Перрон', style0)
        sheet.write(0, 13, u'Нельзя зайти', style0)
        sheet.write(0, 14, u'Ссылка', style0)        

        for frend_id in friends_all_info.keys():
            #{"first_name": "Клондайк", "last_name": "Сити", "last_visit": "1412281333", "app_installed": 1, "nick": "Клондайк", "link": "http://my.mail.ru/mail/scorpion101188/"}
            row += 1
            first_name = (self._correct(friends_all_info[frend_id]['first_name'])).decode('UTF-8', "ignore")
            last_name = (self._correct(friends_all_info[frend_id]['last_name'])).decode('UTF-8', "ignore")
            last_visit = ''
            app_installed = friends_all_info[frend_id]['app_installed']
            nick = (self._correct(friends_all_info[frend_id]['nick'])).decode('UTF-8', "ignore")
            link = friends_all_info[frend_id]['link']
            elink = u'HYPERLINK("' + link + u'";"' + link + '")'
            #hyperlink = u'ГИПЕРССЫЛКА("' + link + u'";"перейти")'
            hyperlink = u'HYPERLINK("' + link + u'";"перейти")'
            game_name = u''
            accessDate = u''
            level = u''
            exp = u''
            status = u''
            banned = u''
            perron = u''
            baduser = u''

            for n in players_info:
                if n.id == frend_id:
                    if hasattr(n, 'name'):
                        nam = (n.name).encode("UTF-8", "ignore")
                        game_name = (self._correct(nam)).decode('UTF-8', "ignore")
                    if hasattr(n, 'accessDate'): accessDate = str(long(n.accessDate)/86400000)
                    level = str(n.level)
                    exp = str(n.exp)
                    if hasattr(n, 'playerStatus'):
                        status = n.playerStatus[4:] # ZOMBIE/HUMAN
                    else: status = 'N/A'
                    if str(n.banned) == 'True': banned = 'banned'
                    break

            if frend_id in perron_list: perron = 'perron'
            if frend_id in baduser_list: baduser = 'NoLoad'
            try:
                active_date = friends_active_game[frend_id][0]
                active_day = friends_active_game[frend_id][1]
            except:
                active_date = ''
                active_day = ''

            text = u''
            text += frend_id + u'\t'
            text += first_name + u' ' + last_name + u'\t'
            text += game_name + u'\t'
            text += u'=' + hyperlink + u'\t'       

            text += last_visit + u'\t'
            text += accessDate + u'\t'
            text += active_date + u'\t'
            text += active_day + u'\t'

            text += app_installed + u'\t'
            text += level + u'\t'
            #text += exp + u'\t'
            text += status + u'\t'
            text += banned + u'\t'
            text += perron + u'\t'
            text += baduser + u'\t'
            
            text += u'=' + elink + u'\t'
            text += u'\n'

            target.write(text.encode("UTF-8", "ignore"))

            # заносим в xls
            sheet.write(row, 0, frend_id, style_left)
            sheet.write(row, 1, first_name + u' ' + last_name, style_left)
            sheet.write(row, 2, game_name, style_left)
            sheet.write(row, 3, xlwt.Formula(hyperlink), style_center)
            sheet.write(row, 4, last_visit, style_right)
            sheet.write(row, 5, accessDate, style_center)
            sheet.write(row, 6, active_date, style_center)
            sheet.write(row, 7, active_day, style_right)
            sheet.write(row, 8, app_installed, style_center)
            sheet.write(row, 9, level, style_center)
            sheet.write(row, 10, status, style_center)
            sheet.write(row, 11, banned, style_center)
            sheet.write(row, 12, perron, style_center)
            sheet.write(row, 13, baduser, style_center)
            sheet.write(row, 14, xlwt.Formula(elink), style_left)
            sheet.row(row).height = 625
        
        target.close()
        book.save('statistics\\'+self.curuser+'\\Users_Info.xls')     # Сохраняем в файл xls
        print u'Отчёт составлен.'
        time.sleep(3)
        raw_input('-------------   END   ---------------')

    def _correct(self, name_):
        # print 'type name_', type(name_)
        # print 'name_',  name_
        while '{' in name_ or '}' in name_ or '[' in name_ or ']' in name_ or '^' in name_ or '&' in name_ or '†' in name_ or '✔' in name_:
            for l in '{}[]^&†✔':
                name_ = name_.replace(l, '')
        if '\u0456' in name_:
            name_ = name_.replace('\u0456', u'i')
        return name_

    # def perform_action(self):
        # self.__api_access_token = self._get_options()[0]
        # self.my_id = self._get_options()[1]
        # self._getFriendsAllMR0()

    # def _getFriendsAllMR0(self):
        # friends_all_id = []
        # #return friends_all_id
        # offset = 0
        # ex_fr = 0
        # while ex_fr == 0:
            # post = {
                # 'method': 'friends.get',
                # 'app_id': '609744',
                # 'offset' : str(offset),
                # 'session_key': self.__api_access_token
                # }
            # post_keys = sorted(post.keys())
            # param_str = "".join(["%s=%s" % (str(key), vkontakte.api._encode(post[key])) for key in post_keys])
            # param_str = self.my_id + param_str + u'5cbd867117243d62af914948498eb3de'
            # sign = md5(param_str).hexdigest().lower()
            # post.update({'sig': sign})
            # BASE_URL = Connection('http://www.appsmail.ru/platform/api')
                
            # resp_fr = BASE_URL.sendRequest(post, cookies=self.__session_cookies)
            # while resp_fr == None:
                # print u'Друзья заедают... попробуем ещё раз'
                # time.sleep(0.5)
                # resp_fr = BASE_URL.sendRequest(post, cookies=self.__session_cookies)
            # add = eval(resp_fr) 
            # print 'load MR', len(add)
            # if len(add) == 0:
                # ex_fr = 1
            # else:
                # offset +=1000
                # friends_all_id.extend(add)
        # print (u'Друзей в Моём Мире: %s'%str(len(friends_all_id))).encode('cp866')
        # with open('statistics\\'+self.curuser+'\friends_all_info.txt', 'w') as f:
            # f.write(friends_all_id.encode("UTF-8", "ignore"))
        # return friends_all_id




        # return
        # raw_input('-------------   END   ---------------')

        #location.guestInfos.userId  # кто у нас ходит в гостях


    """
    # Сортируем список друзей по уровню
    fr_dict = {info.id : info.level for info in players_info}
    friends_order = fr_dict.items()
    friends_order.sort(key=lambda x: x[:-1], reverse=True)
    friends = [fr[0] for fr in friends_order]

    # Пример
    fr_dict = {'567':5, '123':1, '345':3, '456':4}
    friends_order = fr_dict.items()
    friends_order.sort(key=lambda x: x[:-1], reverse=True)
    friends = [fr[0] for fr in friends_order]
    """

