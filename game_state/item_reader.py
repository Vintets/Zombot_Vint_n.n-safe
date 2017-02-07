# -*- coding: utf-8 -*-
from game_state.game_event import dict2obj
from game_state.base import BaseActor
import json
import logging
import os
import time
from game_state.connection import Connection
from game_state.settings import Settings
import pprint
import requests.api
import zlib
import struct


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, obj, context, maxlevels, level):
        if isinstance(obj, unicode):
            return (obj.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, obj,
                                           context, maxlevels, level)


class GameCompositionReader():
    def __init__(self,settings,curuser):
        self.__settings = settings
        self.__curuser = curuser
        
    def readCompositnew(self):
        anims = []
        d = open ('statistics\\'+self.__curuser+'\\compositions', 'rb').read()
        size = len(d)
        count = 0
        obj_Anim = u''
        for i in range(size):
            check = str((struct.unpack_from('c', d,count)))[2:-3]
            count += 1
            if len(check) == 1:obj_Anim += check
            elif obj_Anim != '':
                if len(obj_Anim) > 1:
                    anims.append(obj_Anim)
                    #raw_input()
                    obj_Anim = u''
                else:obj_Anim = u''
        return anims
    def readComposit(self,objAnim,filename):
        d = open ('statistics\\'+self.__curuser+'\\compositions', 'rb').read()
        count = d.count(str(objAnim))
        index2 = d.find(str(objAnim))
        size = len(objAnim.encode())
        counts = 0
        need = 0
        for i in range(count):
            index2 = d.find(str(objAnim),need,-1)
            counts = index2
            check = str((struct.unpack_from('c', d,index2-1)))[2:-3]
            check2 = str((struct.unpack_from('c', d,index2+size+1)))[2:-3]
            if len(check) == 1 or len(check2) == 1: # check in vip_symbol  or check2 in symbol:
                need = size + index2
                continue
            else:break
        x = counts + size + 4 # index+len(search_)+4
        y = x + 4
        w = y + 4
        h = w + 4
        save = '-1'
        save2 = '1'
        replace = '255'
        need = '0'
        x_Adress = str((struct.unpack_from('I', d,x)))[1:-2]
        y_Adress = str((struct.unpack_from('I', d,y)))[1:-2]
        w_Adress = str((struct.unpack_from('I', d,w)))[1:-2]
        h_Adress = str((struct.unpack_from('I', d,h)))[1:-2]
        if y_Adress == replace:y_Adress='-1'
        elif y_Adress != need and y_Adress != save and y_Adress != save2: y_Adress = need
        if x_Adress == replace:x_Adress='-1'
        elif x_Adress != need and x_Adress != save and x_Adress != save2: x_Adress = need
        if w_Adress == replace: w_Adress = h_Adress = y_Adress = x_Adress = save
        if h_Adress == replace: h_Adress = w_Adress = y_Adress = x_Adress = save
        rects = {"rectX":x_Adress,"rectY":y_Adress,"rectW":w_Adress,"rectH":h_Adress}
        return rects
    def loadComposit(self, filename):
        #print "Site", self.__settings.getSite()
        if self.__settings.getSite() == 'mr':
            url = 'https://s.shadowlands.ru/zombiemr-res/res/compositions.soc'
        elif self.__settings.getSite() == 'ok':
            url = 'https://s.shadowlands.ru/zombieok-res/res/compositions.soc'
        else:
            url = 'https://s.shadowlands.ru/zombievk-res/res/compositions.soc'
        r = requests.get(url)
        with open('statistics\\'+self.__curuser+'\\compositions.soc', 'wb') as code:code.write(r._content)
        str_object1 = open ('statistics\\'+self.__curuser+'\\compositions.soc',  'rb' ). read ()
        str_object2 = zlib . decompress ( str_object1 )
        open ('statistics\\'+self.__curuser+'\\compositions' ,  'wb' ). write ( str_object2 )
        print

class GameItemReader():
    def __init__(self, settings):
        self.content_dict = {}
        #settings = Settings()
        self.__ignore_errors = settings.get_ignore_errors()
        self.__site = settings.getSite()


    def get(self, item_id):
        item_id = str(item_id).lstrip('@')
        return dict2obj(self.content_dict[item_id])

    def get_name(self, item):
        return self.get(item.item).name

    def read(self, filename):
        with open(filename) as f:
            self.contents = json.load(f)
        for content in self.contents:
            if 'id' not in content:
                logging.debug(u'there is no id: %s' % content)
            else:
                self.content_dict[content['id']] = content

    def _getModificationTime(self, filename):
        try:
            return time.localtime(os.path.getmtime(filename))
        except OSError:  # no such file
            return None

    def download(self, filename):
        try: last_modified_time = self._getModificationTime(filename)
        except: last_modified_time = None
        print 'Load items for site', self.__site,
        if self.__site == 'mr':
            url = 'https://jmr.shadowlands.ru/zombiemr/items' 
        elif self.__site == 'vk' or self.__site == 'ok':
            url = 'https://java.shadowlands.ru/zombievk/items'
        else:
            # url = 'http://java.shadowlands.ru/zombieok/items'
            url = 'https://jok.shadowlands.ru/zombieok/items'

        if last_modified_time == None or time.localtime(os.path.getmtime(filename)).tm_mday != time.localtime().tm_mday:
            if not self.__ignore_errors:
                data = Connection(url).getChangedDocument(
                    data={'lang': 'ru'},
                    last_client_time=last_modified_time
                    )
            else:
                while 1:
                    try:
                        #print 'Download items...',
                        data = Connection(url).getChangedDocument(data={'lang': 'ru'}, last_client_time=last_modified_time)
                        #print 'Items downloaded!',
                        # data_compressed = Connection(url).getChangedDocument(data={u'compress': u'true', 'lang': 'ru'}, last_client_time=last_modified_time)
                        # data = zlib.decompress(data_compressed)
                        #items = json.loads(data)
                        break
                    except: print 'Refresh download...'
                #with open(filename, 'w') as f: f.write(data.encode('utf-8'))
            if data:
                if os.path.isfile(filename): os.remove(filename)
                with open(filename, 'w') as f: f.write(data.encode('utf-8'))

    def pretty_write(self, filename):
        with open(filename, 'w') as f:
            pretty_dict = MyPrettyPrinter().pformat(self.content_dict)
            f.write(pretty_dict)



class LogicalItemReader(object):
    'defines item ids and names that are available to use'

    def __init__(self, game_item_reader):
        self._item_reader = game_item_reader

    def get_avail_names(self, game_state):
        return sorted(self.__get_items_available(game_state).keys())

    def get_by_name(self, item_name):
        items = self.__get_name_to_item()
        if item_name in items:
            return items[item_name]

    def is_item_available(self, item, game_state):
        level = game_state.get_state().level
        location_id = game_state.get_game_loc().get_location_id()
        location = self._item_reader.get(location_id)
        allowed_here = (not hasattr(location, 'allowCompositionIds') or \
                        item.id in location.allowCompositionIds) and \
                       (not hasattr(item, 'locations') or \
                        location_id in item.locations)
        is_a_type = item.type == self._get_item_type()
        allowed_for_level = not hasattr(item, 'level') or item.level <= level
        return is_a_type and allowed_here and allowed_for_level

    def __get_name_to_item(self):
        items = {}
        item_ids = self._get_all_item_ids()
        for item_id in item_ids:
            item = self._item_reader.get(item_id)
            items[item.name] = item
        return items

    def __get_items_available(self, game_state):
        items = self.__get_name_to_item()
        items = {k: v for k, v in items.iteritems()\
                      if self.is_item_available(v, game_state)}
        return items

    def _get_all_item_ids(self):
        raise NotImplementedError  # inherit and implement

    def _get_item_type(self):
        raise NotImplementedError  # inherit and implement
