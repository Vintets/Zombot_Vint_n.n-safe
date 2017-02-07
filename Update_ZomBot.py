#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ftplib import FTP
import sys
sys.path.append('./API')
import os
import re
import shutil
import subprocess
# import simplejson
import ConfigParser
import time
import platform
from ctypes import windll

stdout_handle = windll.kernel32.GetStdHandle(-11)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute


class UP():
    def __init__(self, host, user, password):
        self.host = host
        self.ftp_user = user
        self.ftp_password = password
        self.up_path = 'update'
        self.read_me = []
        if not os.path.isdir(self.up_path): os.makedirs(self.up_path)
        self.up_path += '\\'
        name_ini = self.up_path + 'update.ini'
        self.init_ini(name_ini)
        self.set_name_section('update')
        self.err = False
        self.pref = 'update_'
        # self.pref = '__test_'

    def run(self):
        try:
            con = FTP(self.host, self.ftp_user, self.ftp_password)
        except:
            self.cprint(u'12Ошибка связи с сервером обновлений!')
            return

        folders_r = con.nlst()
        folders = []
        for f in folders_r:
            if f[:7] == self.pref:
                folders.append(f)
        # folders.remove(u'update_list.txt')
        self.cprint(u'1Всего выпущено обновлений^15_%d' % len(folders))

        last_download = self.get_param('last_download')
        if last_download and (last_download in folders):
            news_download = folders[folders.index(last_download) + 1:]
        else:
            news_download = folders
        self.cprint(u'13Новых обновлений для загрузки^15_%d' % len(news_download))

        last_update = self.get_param('last_update')
        if last_update and (last_update in folders):
            news_update = folders[folders.index(last_update) + 1:]
        else:
            news_update = folders
        self.cprint(u'13Новых обновлений для установки^15_%d' % len(news_update))
        print
        self.worker(con, news_download, news_update)
        time.sleep(0.5)
        if self.err:
            self.cprint(u'12-------  ошибка установки некоторых обновлений  -------')
        else:
            self.cprint(u'2---------------  обновление завершено  ---------------')

    def worker(self, con, news_download, news_update):
        # last_up_name = self.load(con, news_download)
        try:
            last_up_name = self.load(con, news_download)
            if last_up_name:
                self.set_param('last_download', last_up_name)
                self.save()
        except:
            self.cprint(u'12Ошибка скачивания!')
            self.err = True
            return
        last_up_name = self.updates(con, news_update)
        if last_up_name:
            self.open_read_me()
                
    def open_read_me(self):
        if '64' in platform.machine(): 
            notep = 'C:\Program Files (x86)\Notepad++\Notepad++.exe'
        else:
            notep = 'C:\Program Files\Notepad++\Notepad++.exe'
        for txt in self.read_me:
            try:
                subprocess.Popen([notep, os.getcwd() + '\\' + txt])
                time.sleep(0.5)
            except: pass

    def load(self, con, news_download):
        last_up_name = None
        if news_download:
            self.cprint(u'14Cкачиваем...')
        for name_update in news_download:
            if name_update[:7] == self.pref:
                last_up_name = name_update
            self.cprint(u'9\t%s' % name_update)
            
            if not os.path.isdir(self.up_path + name_update):
                os.makedirs(self.up_path + name_update)
            dates = name_update[7:]
            read_me = '__read_me_' + dates + '.py'
            change_mega = 'change_mega.py'
            uzb = 'Update_ZomBot.py'
            dirs = ['game_actors_and_handlers', 'game_state', 'statistics', 'API']
            
            subfolders = con.nlst(name_update)
            # print 'subfolders', subfolders
            for subfolder in subfolders:
                if (subfolder[:7] != self.pref) and (subfolder not in dirs):
                    print '\t\t' + subfolder
                    filename = name_update + '\\' + subfolder
                    # print u'скачиваем read_me, change_mega или up2up'
                    self.download(con, filename)
                    continue
                if not os.path.isdir(self.up_path + name_update + '\\' + subfolder):
                    os.makedirs(self.up_path + name_update + '\\' + subfolder)
                subfiles = con.nlst(name_update + '\\' + subfolder)
                # print 'subfiles', subfiles
                for _file in subfiles:
                    print '\t\t' + subfolder + '\\' + _file
                    filename = name_update + '\\' + subfolder + '\\' + _file
                    self.download(con, filename)
            print
        # Закрываем FTP соединение
        con.close
        return last_up_name

    def updates(self, con, news_update):
        last_up_name = None
        last_update = self.get_param('last_update')
        # if last_update and (last_update in folders):
            # news = folders[folders.index(last_update) + 1:]
        # else:
            # news = folders
        print
        if news_update:
            self.cprint(u'14Установка обновлений...')
            for name_update in news_update:
                change_mega = ''
                up2up = ''
                self.cprint2(u'9%s\t^1_status ' % name_update)
                current = self.up_path + name_update
                if not os.path.isdir(current):
                    self.status('Error')
                    self.err = True
                    return last_up_name
                for d, dirs, files in os.walk(current):
                    # print d, dirs, files
                    for f in files:
                        # print u'Файл', f
                        if f[:10] == '__read_me_':
                            read_me = os.path.join(d,f)
                        elif f == 'change_mega.py':
                            change_mega = f
                        elif f == 'Update_ZomBot.py':
                            up2up = f
                            read_me = os.path.join(d,f)
                        else:
                            file_in = os.path.join(d,f)
                            file_out = file_in.split(current + '\\')[-1]
                            # print u'откуда', file_in
                            # print u'куда', file_out
                            try:
                                shutil.copyfile(file_in, file_out)
                            except IOError:
                                self.status('Error COPY^5_' + file_in)
                                self.err = True
                                return last_up_name
                # обрабатываем change_mega
                if change_mega:
                    response = self.change_mega_f(current, change_mega, name_update)
                    # try:
                        # response = self.change_mega_f(current, change_mega, name_update)
                        # if response != 0:
                            # self.status('Error edit ' + change_mega)
                            # self.err = True
                            # return last_up_name
                    # except:
                        # self.status('Error edit ' + change_mega)
                        # self.err = True
                        # return last_up_name
                if up2up:
                    self.read_me.append(read_me)
                    self.up2up(current, name_update)
                    
                self.status('OK')
                last_up_name = name_update
                self.read_me.append(read_me)
                self.set_param('last_update', last_up_name)
                self.save()
        return last_up_name

    def change_mega_f(self, current, change_mega, name_update):
        self.backup('_mega_options', name_update[7:])
        rstr = ['python', current + '\\' + change_mega, current]
        response = subprocess.call(rstr)
        return response

    def up2up(self, current, name_update):
        print
        self.backup('Update_ZomBot', name_update[7:])
        self.unpack_bat()
        rstr = [os.getcwd() + '\\update\\up2up.bat', name_update]
        # print u'запуск up2up', rstr
        self.cprint(u'9Запуск обновления обновлялки :) ...')
        subprocess.Popen(rstr, creationflags=subprocess.CREATE_NEW_CONSOLE)
        last_up_name = name_update
        self.set_param('last_update', last_up_name)
        self.save()
        time.sleep(1)
        self.open_read_me()
        exit()

    def backup(self, file, name_update):
        loc_path = self.up_path + 'backup'
        if not os.path.isdir(loc_path): os.makedirs(loc_path)
        loc_path = loc_path + '\\'
        num = 1
        name = file + '_before_' + name_update + '_' + str(num) + '.py'
        while os.path.isfile(loc_path + name):
            num += 1
            name = file + '_before_' + name_update + '_' + str(num) + '.py'
        shutil.copyfile(file + '.py', loc_path + name)

    def unpack_bat(self):  # прописывание батника
        if not os.path.isfile(self.up_path + 'up2up.bat'):
            text = self.get_text_bat()
            with open(self.up_path + 'up2up.bat', 'w') as fp:
                fp.write(text.encode('cp866'))

    def status(self, status):
        if status == 'OK':
            self.cprint(u'2%s' % status)
        else:
            self.cprint(u'12%s' % status)

    def download(self, con, filename):  # скачиваем файл
        with open(self.up_path + filename, 'wb') as lf:
            con.retrbinary('RETR ' + filename, lf.write, 8*1024)

    def init_ini(self, filename):  # работа с pirate ini
        self.filename = filename
        if not os.path.isfile(filename):
            self.new_ini()
        self.parser = ConfigParser.RawConfigParser()
        self.read_ini()

    def new_ini(self):
        with open(self.filename, 'w') as f:
            text = u'[update]\n\n'
            f.write(text.encode('UTF-8'))

    def read_ini(self):
        self.parser.read(self.filename)

    def set_name_section(self,section):
        self.sect = section
        if not self.parser.has_section(section):
            self.add_section(section)

    def get_sections(self):
        return self.parser.sections()

    def get_param(self, param):
        if param in self.parser.options(self.sect):
            return self.parser.get(self.sect, param)
        return None

    def get_allparam(self):
        return self.parser.items(self.sect)
        
    def set_param(self, param, value):
        self.parser.set(self.sect, param, value)

    def add_section(self, param):
        try:
            self.parser.add_section(param)
            self.save()
        except ConfigParser.DuplicateSectionError:
            # print u"Секция '%s' уже есть" % param
            pass
        except:
            print u"Не смог записать секцию '%s' в файл" % param

    def remove_option(self, param):
        self.parser.remove_option(self.sect, param)

    def remove_section(self, param):
        if self.parser.has_section(param):
            self.parser.remove_section(self.sect, param)
            self.save()

    def save(self):
        with open(self.filename, 'w') as fp:
            self.parser.write(fp)
            
    def cprint(self, cstr):
        clst = cstr.split('^')
        color = 0x0001

        for cstr in clst:
            dglen = re.search("\D", cstr).start()
            color = int(cstr[:dglen])
            text = cstr[dglen:]
            if text[:1] == "_": text = text[1:]
            SetConsoleTextAttribute(stdout_handle, color | 0x0070) #78
            print text.replace(u'\u0456', u'i').encode("cp866", "ignore"),
        #sys.stdout.flush()
        print ""
        SetConsoleTextAttribute(stdout_handle, 0x0001 | 0x0070)

    def cprint2(self, cstr):
        clst = cstr.split('^')
        color = 0x0001

        for cstr in clst:
            dglen = re.search("\D", cstr).start()
            color = int(cstr[:dglen])
            text = cstr[dglen:]
            if text[:1] == "_": text = text[1:]
            SetConsoleTextAttribute(stdout_handle, color | 0x0070) #78
            print text.replace(u'\u0456', u'i').encode("cp866", "ignore"),
        sys.stdout.flush()
        SetConsoleTextAttribute(stdout_handle, 0x0001 | 0x0070)

    def get_text_bat(self):
        txt = u"""
@echo off

::echo %~dp0
cd %~dp0

@echo %DATE%
@echo Ждём закрытия основного обновления...
@echo.
@ping -n 5  127.0.0.1>nul
@echo %time:~0,-3% Переносим файл Update_ZomBot.py
@xcopy "%1\\Update_ZomBot.py" ".." /Y
@echo.
@echo %time:~0,-3% Копирование завершено
@echo -------------------------------
@ping -n 5  127.0.0.1>nul
"""
        return txt


if __name__ == '__main__':
    host = '185.117.153.104'
    user = 'ZomBotUpdate'
    password = 'ZomBotUpdate'
    up = UP(host, user, password)
    up.run()
    raw_input(u' ')

# chdir /D D:\Яндекс Диск\_Update_ZomBot
# python Update_ZomBot.py
