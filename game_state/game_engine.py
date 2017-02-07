# -*- coding: utf-8 -*-
import os
# from os import walk
# import os.path
import sys
sys.path.append('./API')
import requests.api
import vkontakte.api
import game_state.vkutils
import game_state.mrutils
#import game_state.okutils
#import odnoklassniki.api
import logging
import random
import ssl
import re
import time
import datetime
import pprint
import socket
import urllib2
import ConfigParser
# import pdb
from ctypes import windll
import game_state.message_factory as message_factory
# from game_state.message_factory import *
from game_state.settings import Settings
from game_state.base import BaseActor
from _mega_options import MegaOptions
from game_state.free_space import FreeSpace
from game_state.item_reader import GameItemReader, GameCompositionReader
from game_state.game_event import dict2obj, obj2dict
from game_state.game_types import GameEVT, GameTIME, GameSTART, GameInfo, GameFertilizePlant, GamePlayGame, GameStartGainMaterial, GameStartTimeGainEvent
from game_state.brains import PlayerBrains
from game_actors_and_handlers.standing import Standing
from game_actors_and_handlers.gifts import AddGiftEventHandler
from game_actors_and_handlers.plants import PlantEventHandler, GameSeedReader
from game_actors_and_handlers.roulettes import GameResultHandler
from game_actors_and_handlers.cook_graves import RecipeReader
from game_actors_and_handlers.digger_graves import TimeGainEventHandler
from game_actors_and_handlers.workers import GainMaterialEventHandler
from game_actors_and_handlers.pickups import AddPickupHandler
from game_actors_and_handlers.location import GameStateEventHandler
from game_actors_and_handlers.missions import GetMissionsBot, ViewMissions

stdout_handle = windll.kernel32.GetStdHandle(-11)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute

logger = logging.getLogger(__name__)


class GameLocation():
    def __init__(self, item_reader, game_location, game_objects):
        self.__item_reader = item_reader
        self.__game_location = game_location
        if self.__game_location.id == 'main':
            openedAreas = self.__game_location.openedAreas
            maps = [str(i)+':'+str(j) for i in range(0,128) for j in range(48,100)]
            if 'second' in openedAreas:
                add=[str(i)+':'+str(j) for i in range(0,48) for j in range(0,48)]
                maps.extend(add)
            if 'mount' in openedAreas:
                add = [str(i)+':'+str(j) for i in range(62,128) for j in range(0,30)]
                maps.extend(add)
            objects = [object for object in game_objects if str(object.x)+':'+str(object.y) in maps]
            game_objects = objects
        self.__game_objects = game_objects
        self.__game_objects_dict = {obj.id:obj for obj in game_objects}
        self.__pickups = []

    def append_object(self, obj):
        self.get_game_objects().append(obj)

    def get_game_location(self):
        return self.__game_location

    def get_game_objects(self):
        return self.__game_objects

    def get_location_id(self):
        return self.__game_location.id

    def get_all_objects_by_types(self, object_types):
        objects = []
        for game_object in self.get_game_objects():
            item = self.__item_reader.get(game_object.item)
            if game_object.type in object_types or item.type in object_types:
                objects.append(game_object)
        return objects

    def get_all_objects_by_type(self, object_type):
        return self.get_all_objects_by_types([object_type])

    def get_object_by_id(self, obj_id):
        for game_object in self.get_game_objects():
            if game_object.id == obj_id:
                return game_object
        return None

    def log_game_objects(self):
        for gameObject in self.get_game_objects():
            # if gameObject.type != 'base':
                logger.info(obj2dict(gameObject))

    def remove_object_by_id(self, obj_id):
        for game_object in list(self.get_game_objects()):
            if game_object.id == obj_id:
                self.get_game_objects().remove(game_object)

    def get_pickups(self):
        return tuple(self.__pickups)

    def add_pickups(self, pickups):
        self.__pickups += pickups

    def remove_pickup(self, pickup):
        self.__pickups.remove(pickup)


class GameTimer(object):

    def __init__(self):
        self._client_time = 0
        self._start_time = 0

    def _get_client_time(self):
        random.seed()
        self._client_time = long(random.randrange(2800, 4000))
        self._start_time = time.time()
        return self._client_time

    def _get_current_client_time(self):
        '''
        returns the current in-game time (in milliseconds)
        '''
        currentTime = self._client_time
        currentTime += (time.time() - self._start_time) * 1000
        return currentTime

    def _add_sending_time(self, sending_time):
        self._client_time += sending_time

    def has_elapsed(self, time):
        #return int(time) <= self._get_current_client_time()
        return int(time)+3000 <= self._get_current_client_time()
        
    def has_elapsed_in(self, time, sec):
        return int(time) + 3000 - sec*1000 <= self._get_current_client_time()

    def client_time(self):
        return self._get_current_client_time()
        
    def has_time(self, time):
        return int(time) - self._get_current_client_time()


class GameEventsSender(object):
    def __init__(self, request_sender):
        self.__events_to_handle = []
        self.__request_sender = request_sender

    def print_game_events(self):
        if len(self.__events_to_handle) > 0:
            logger.debug("received events: %s" % self.__events_to_handle)

    def get_game_events(self):
        return list(self.__events_to_handle)

    def send_game_events(self, events=[]):
        '''
        Returns key (string) and time (int)
        '''
        if len(events) > 0:
            logger.debug("events to send: %s" % events)
        command = GameEVT(events=events)
        game_response = self.__request_sender.send(command)
        self.__events_to_handle += game_response.events

    def remove_game_event(self, event):
        self.__events_to_handle.remove(event)


class GameInitializer():
    def __init__(self, timer, site, selected_site, curuser):
        self.__timer = timer
        self.__site = site
        self.__selected_site = selected_site
        self.__selected_curuser = curuser

    def create_events_sender(self):
        return GameEventsSender(self.__request_sender)

    def start(self):
        logger.info(u'Подключаемся к игре...')
        # send TIME request (http://java.shadowlands.ru/zombievk/go)
        # handle redirect (save new url: http://95.163.80.20/zombievk)
        # parse auth key and time id
        session_key, server_time = self.get_time()

        # send START
        start_response, friendsid = self.start_game(server_time, session_key)
        logger.info(u'Игра подключена!')
        # id друзей в файл
        # try:
            # os.remove('friends_id.txt')
        # except:
            # pass  
        # with open('friends_id.txt', 'a') as f:
            # friends = ''
            # for fr_id in friendsid:
                # friends += str(fr_id) + '\n'
            # f.write(friends)
        return start_response, friendsid, server_time

    def get_time(self):
        '''
        Returns key (string) and time (int)
        '''
        self.__request_sender = self.__create_request_sender()
        key = self.__site.get_time_key()
        command = GameTIME(key=key)
        response = self.__request_sender.send(command)
        return response.key, response.time

    def __create_request_sender(self):
        api_user_id, game_auth_key, api_access_token, connection = self.__site.get_game_params()
        global my_id
        my_id = api_user_id
        #global api_session_key
        #api_session_key = api_access_token['session_key']
        self.__api_access_token = api_access_token
        self.__connection = connection
        self.__session = message_factory.Session(api_user_id, game_auth_key,
                                 client_version=Game.CLIENT_VERSION)
        factory = message_factory.Factory(self.__session, self.__selected_site, None)
        request_sender = RequestSender(factory,
                                       self.__connection, self.__timer)
        self.__factory = factory
        return request_sender

    def start_game(self, server_time, session_key):
        self.__factory.setRequestId(server_time)
        self.__factory.setSessionKey(session_key)
        client_time = self.__timer._get_client_time()
        start_time = time.time()
        #print client_time, start_time
        command, friendsid = self.__site.create_start_command(server_time, client_time, self.__selected_curuser)
        sending_time = (time.time() - start_time) * 1000
        self.__timer._add_sending_time(sending_time)
        return self.__request_sender.send(command),friendsid


class GameState(BaseActor):

    def __init__(self, start_response, item_reader, settings, curuser, friends, timer):
        self.__curuser = curuser
        self.__friends = friends
        self.__timer = timer
        self.__settings = settings
        self.__item_reader = item_reader
        self.__game_state = start_response.state
        game_state_event = start_response.params.event
        self.set_game_loc(game_state_event)
        #self.__player_brains = PlayerBrains(self.__game_state,self.get_game_loc(),item_reader)
        #total_brain_count = self.__player_brains.get_total_brains_count()
        #occupied_brain_count = self.__player_brains.get_occupied_brains_count()

        playerBrains = PlayerBrains(self.__game_state,self.get_game_loc(),item_reader,self.__timer)
        total_brain_count = playerBrains.get_total_brains_count()
        occupied_brain_count = playerBrains.get_occupied_brains_count()        
        ###############
        """
        if not hasattr(self.__game_state,'rectsObjects'):self.__game_state.rectsObjects=[]
        vip = ["@PIRATE_BOX","@PIRATE_BOX_2"]
        need_group = ['compositions','seed']
        compositions = GameItemReader()
        need_catalog = []
        for v in vip:
            if v not in need_catalog:need_catalog.append(v)
        for group in need_group:
            for item_ in self.__item_reader.get(group).items:
                if not item_ in need_catalog:need_catalog.append(item_)
        for item in need_catalog:
            read_item = self.__item_reader.get(item)
            if not hasattr(read_item,'objAnim'):continue
            for obj in read_item.objAnim:
                rectss = compositions.readComposit(obj,'compositions')
                objects = dict2obj({"objAnim":str(obj),"rects":rectss})
                self.__game_state.rectsObjects.append(objects)
        """
        
        if not hasattr(self.__game_state,'rectsObjects'):self.__game_state.rectsObjects=[]
        compositions = GameCompositionReader(self.__settings, self.__curuser)
        objAnims = compositions.readCompositnew()
        for anims in objAnims:
            rectss = compositions.readComposit(anims,'compositions')
            objects = dict2obj({"objAnim":str(anims),"rects":rectss})
            self.__game_state.rectsObjects.append(objects)
        ################
        
        #open('gameSTATE.txt', 'w').write(str(obj2dict(self.__game_state)))
        cou = 0
        for fgift in self.__game_state.freeGiftUsers:
            if fgift.blockedUntil > 0: cou += 1

        x1 = 0
        z = 0
        for burySlot in self.__game_state.burySlots:
            x1 += 1
            if (hasattr(burySlot, u"user") is True): z+=1

        Money = ''
        for i in range(len(str(self.__game_state.gameMoney)),0,-3):
          if i >= 3: Money = str(self.__game_state.gameMoney)[i-3:i]+'.'+Money
          else: Money = str(self.__game_state.gameMoney)[:i]+'.'+Money
        
        if hasattr(self.__game_state, "cashMoney"):
            zb = self.__game_state.cashMoney
        
        dub = self.count_in_storage('@DUBLON')
        
        """
        logger.info(u"Друзья: %d/%d" % (cou,self.__friends))
        #logger.info("")
        logger.info(u"Использование слотов для закопки друзей: %d/%d" % (z,x1))
        
        logger.info(u"Мозги: %d/%d" % (occupied_brain_count, total_brain_count))
        if len(self.__game_state.buyedBrains) <> 0:
            logger.info(u"Купленные:")
            x = 1
            for buyed_brain in self.__game_state.buyedBrains:
                ms = int(buyed_brain.endTime)-((int(buyed_brain.endTime)/1000)*1000)
                s = (int(buyed_brain.endTime)/1000)-(((int(buyed_brain.endTime)/1000)/60)*60)
                m = ((int(buyed_brain.endTime)/1000)/60)-((((int(buyed_brain.endTime)/1000)/60)/60)*60)
                h = ((int(buyed_brain.endTime)/1000)/60)/60
                logger.info(u"%d. Время окончания: %d:%d:%d.%d"%(x,h,m,s,ms))
                x += 1
        logger.info("")
        
        logger.info(u"Игрок: "+str(settings._currentUser))
        logger.info(u"Уровень игрока: "+str(self.__game_state.level))
        logger.info(u"Деньги игрока: "+Money[:-1])
        logger.info(u"Зомбаксов: %d" % (zb))
        logger.info(u"Дублонов: %d" % (dub))
        logger.info("")
        """

        print u'Друзья: %d/%d' % (cou,self.__friends)
        print
        # на принте
        self.cprint (u"1Слоты для закопки друзей: ^14_%d/%d" % (z,x1))
        self.cprint (u"1Мозги: ^14_%d/%d" % (occupied_brain_count, total_brain_count))
        
        if len(self.__game_state.buyedBrains) <> 0:
            print u"Купленные:"
            x = 1
            for buyed_brain in self.__game_state.buyedBrains:
                brain_time = self.__timer.has_time(buyed_brain.endTime)
                print u"%d. Кол-во: %d  Время окончания: %s"%(x,buyed_brain.count,self.clock2(brain_time))
                x += 1
        print
        
        self.cprint (u"1Игрок: ^13_%s" % (settings._currentUser))
        self.cprint (u"1Уровень игрока: ^12_%s" % (self.__game_state.level))
        self.cprint (u"1Деньги игрока:  ^14_%s  ^1монет" % (Money[:-1]))
        self.cprint (u"1Зомбаксов:      ^14_%d" % (zb))
        self.cprint (u"1Дублонов:       ^14_%d" % (dub))
        print

        os.system((u'title '+u"Акк: "+self.__curuser+u"   Lev: "+str(self.__game_state.level)+u'  Мозгов: ' + str(occupied_brain_count)+'/'+str(total_brain_count)+u' Слоты: '+str(z)+'/'+str(x1) + u'  ЗБ: '+str(zb) + u' Монет: '+str(Money[:-1])).encode('cp1251', 'ignore'))
        #os.system((u'title '+u"Акк: "+self.__curuser+u" Lev: "+str(self.__game_state.level)+u'  Мозгов: ' + str(occupied_brain_count)+'/'+str(total_brain_count)+u' Слоты: '+str(z)+'/'+str(x1)+u' Друзья: '+str(cou)+"/"+str(self.__friends) + '\n' + u'ЗБ: '+str(self.__game_state.cashMoney) + u' Монет: '+str(Money[:-1])).encode('cp1251', 'ignore'))
        #os.system((u'title '+u"Акк: "+self.__curuser+u" Уровень: "+str(self.__game_state.level)+u'  Мозгов: ' + str(occupied_brain_count)+'/'+str(total_brain_count)+u' Слоты: '+str(z)+'/'+str(x1)+u' Друзья: '+str(len(self.__game_state.freeGiftUsers))+"/"+str(self.__friends)+":"+str(cou)).encode('cp1251', 'ignore'))
        #os.system((u'title '+self.__curuser+u' Мозгов: ' + str(occupied_brain_count)+'/'+str(total_brain_count)+u' Слоты: '+str(z)+'/'+str(x1)+u' Друзья: '+str(len(self.__game_state.freeGiftUsers))+"/"+str(self.__friends)+":"+str(cou)).encode('cp1251', 'ignore'))
        pass
        
    # def get_free_spases(self):
        # return FreeSpace(self.__item_reader,self.__game_state,self.get_game_loc())

    def set_game_loc(self, game_state_event):
        self.set_game_loc_was = True
        self.__game_loc = GameLocation(self.__item_reader,
                                       game_state_event.location,game_state_event.gameObjects)
        for attr, val in game_state_event.__dict__.iteritems():
            self.__game_state.__setattr__(attr, val)
        #self.get_game_loc().log_game_objects()

    def get_location_id(self):
        return self.get_state().locationId

    def get_game_loc(self):
        return self.__game_loc

    def get_state(self):
        return self.__game_state

    def get_settings(self):
        return self.__settings

    def get_curuser(self):
        return self.__curuser

    def get_my_id(self):
        return my_id

    def get_brains(self):
        #return self.__player_brains
        return PlayerBrains(self.__game_state,self.get_game_loc(),self.__item_reader,self.__timer)

    def has_in_storage(self, item_id, count):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.storageItems:
            if hasattr(itemid, "item"):
                if itemid.item == item_id:
                    return itemid.count >= count
        return False

    def count_in_storage(self, item_id):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.storageItems:
            if hasattr(itemid, "item"):
                if itemid.item == item_id:
                    return itemid.count
        return 0

    def remove_from_storage(self, item_id, count):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.storageItems:
            if hasattr(itemid, "item"):
                if itemid.item != item_id: continue
                itemid.count -= count
                if itemid.count == 0:
                    self.__game_state.storageItems.remove(itemid)
                return True
        return False

    def add_from_storage(self, item_id, count):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.storageItems:
            if hasattr(itemid, "item"):
                if itemid.item == item_id:
                    itemid.count += count
                    return
        self.set_from_storage(item_id, count)

    def set_from_storage(self, item_id, count):
        itemid = dict2obj({u'item': item_id, u'count': count})
        self.__game_state.storageItems.append(itemid)

    def count_in_pirate_instruments(self, item_id):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.pirate.instruments:
            if itemid.item == item_id: return itemid.count
        return 0

    def remove_from_pirate_instruments(self, item_id, count):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.pirate.instruments:
            if hasattr(itemid, "item"):
                if itemid.item != item_id: continue
                itemid.count -= count
                return True
        return False

    def add_pirate_instruments(self, item_id, count):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.pirate.instruments:
            if hasattr(itemid, "item"): 
                if itemid.item == item_id:
                    itemid.count += count
                    return
        self.set_pirate_instruments(item_id, count)

    def set_pirate_instruments(self, item_id, count):
        itemid = dict2obj({u'item': item_id, u'count': count})
        self.__game_state.pirate.instruments.append(itemid)

    def count_in_storageObjects(self, item_id):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.storageGameObjects:
            if hasattr(itemid, "item"):
                if itemid.item == item_id:
                    return itemid.count
        return 0

    def remove_from_storageObjects(self, item_id, count):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.storageGameObjects:
            if hasattr(itemid, "item"):
                if itemid.item != item_id: continue
                itemid.count -= count
                if itemid.count == 0:
                    self.__game_state.storageGameObjects.remove(itemid)
                return True
        return False

    def add_from_storageObjects(self, item_id, count):
        item_id = item_id.lstrip('@')
        item_id = '@'+item_id
        for itemid in self.__game_state.storageGameObjects:
            if hasattr(itemid, "item"):
                if itemid.item == item_id:
                    itemid.count += count
                    return
        self.set_from_storageObjects(item_id, count)

    def set_from_storageObjects(self, item_id, count):
        itemid=dict2obj({u'item': item_id, u'count': count})
        self.__game_state.storageGameObjects.append(itemid)
        
    def clock2(self, timems):
        timems = int(timems)
        h = timems/1000/60/60
        m = timems/1000/60 - (h*60)
        s = timems/1000 - (timems/1000/60*60)
        # print u'Время: %d:%d:%d'%(h,m,s)
        return str(h) + ':' + str(m) + ':' + str(s)


class Game(BaseActor):

    #CLIENT_VERSION = long(1362084734) (1378103895) (1382714383) (1406282412) (1414512369)
    CLIENT_VERSION = long(1435224991)


    def __init__(self, site, settings,
                 user_prompt, game_item_reader=None, gui_input=None):
        logger.info('Логинимся...')

        self.__selected_site = settings.getSite()
        self.__selected_curuser = settings.getCurUser()

        if not os.path.isdir('statistics'): os.makedirs('statistics')
        if not os.path.isdir('statistics\\'+self.__selected_curuser):
            os.makedirs('statistics\\'+self.__selected_curuser)

        self.__timer = GameTimer()
        self.__game_initializer = GameInitializer(self.__timer, site, self.__selected_site, self.__selected_curuser)
        self.__settings = settings

        self.__itemReader = game_item_reader
        self.__user_prompt = user_prompt
        self.__selected_seed = None
        self.__selected_recipe = None
        self.__selected_location = None
        self.__gui_input = gui_input
        
        # load settings
        self.__ignore_errors = settings.get_ignore_errors()
        self.__selected_recipe = settings.getUserCook()
        self.__selected_seed = settings.getUserSeed()
        self.__selected_sell = settings.getUserSell()
        self.__selected_send = settings.getUserSend()
        self.__setting_view = settings.GetUserView()
        self.__selected_loc_setting = settings.getUserLoc()
        self.__selected_dig_friends = settings.getUserDig()
        self.__selected_PremiumGifts = settings.getUserPremiumGifts()

        
        self.__mega = MegaOptions(self.__selected_curuser)
        self.__mega.print_group()


        print ''
        if self.__selected_seed <> None:
            if  (self.__selected_seed == 'None'): print u'Выбранные семена: ничего не сажать'
            else:
                if type(self.__selected_seed) == type(''): print u'Выбранные семена: везде "%s"'%str(self.__selected_seed)
                else:
                    print u'Выбранные семена (остров - семена):'
                    for loc in self.__selected_seed.keys():
                        if len(loc) > 8:
                            print u'\t%s\t-\t"%s"'%(str(loc),str(self.__selected_seed[loc]))
                        else: print u'\t%s\t\t-\t"%s"'%(str(loc),str(self.__selected_seed[loc]))
        print ''
        if self.__selected_recipe <> None:
            if  (self.__selected_recipe == 'None'): print u'Выбранные рецепты: ничего не варить'
            else:
                if type(self.__selected_recipe) == str or type(self.__selected_recipe) == unicode:
                    print u'Выбранные рецепты: везде "%s"'%str(self.__selected_recipe)
                elif type(self.__selected_recipe) == list and\
                        (type(self.__selected_recipe[0]) == str or type(self.__selected_recipe[0]) == unicode):
                    print u'Выбранные рецепты: везде "%s"'%str(', '.join(self.__selected_recipe))
                elif type(self.__selected_recipe) == list and type(self.__selected_recipe[0]) == tuple:
                    print u'Выбранные семена (рецепт - количество на складе):'
                    for _dat in self.__selected_recipe:
                        print u'\t%s\t-\t%d'%(str(_dat[0]), _dat[1])
                elif type(self.__selected_recipe) == dict:
                    print u'Выбранные семена (остров - рецепт):'
                    for loc in self.__selected_recipe.keys():
                        if len(loc) > 6: print u'\t%s\t-\t"%s"'%(str(loc),str(self.__selected_recipe[loc]))
                        else: print u'\t%s\t\t-\t"%s"'%(str(loc),str(self.__selected_recipe[loc]))
        if  (self.__selected_sell==None): print u'Предметы на продажу: ничего не продавать'
        else:
            print u'Предметы на продажу (предмет - сколько оставить):'
            for item in self.__selected_sell.keys():
                print u'\t"%s"\t\t-\t%d'%(str(item), self.__selected_sell[item])
        print ''
        print u'Настройки показа:'
        if  (self.__setting_view['pickup']): print u'\tПоказывать подбираемые предметы'
        else:  print u'\tНе показывать подбираемые предметы'
        if  (self.__setting_view['location_send']): print u'\tПоказывать перешедшую локацию'
        else:  print u'\tНе показывать перешедшую локацию'
        print ''

    def select_item(self, reader_class, prompt_string):
        item_reader = reader_class(self.__itemReader)
        available_items = item_reader.get_avail_names(self.__game_state_)
        item_name = self.__user_prompt.prompt_user(prompt_string,
                                                   available_items)
        return item_reader.get_by_name(item_name)

    def select_plant_seed(self):
        if self.__selected_seed is None:
            self.__selected_seed = self.select_item(GameSeedReader,
                                                    u'Семена для грядок:')

    def select_recipe(self):
        if self.__selected_recipe is None:
            self.__selected_recipe = self.select_item(RecipeReader,
                                                      u'Рецепт для поваров:')

    def select_location(self):
        print u'Доступные острова:'
        print u'(+ платный, - бесплатный, ? - пещера)'
        locations_nfree = [u'isle_01', 'isle_small', 'isle_star', 'isle_large', 'isle_moon', 'isle_giant', 'isle_xxl', 'isle_desert']
        locations_nwalk = [u'un_0'+str(x+1) for x in range(9)]

        locations = {}
        for location in self.get_game_state().locationInfos:
            name = self.__itemReader.get(location.locationId).name
            loc_log = location.locationId.ljust(18, ' ')
            if (location.locationId not in locations_nfree) and (location.locationId not in locations_nwalk):
                locations[name] = location
                print u'\t-\t'+loc_log+name
                #print u'\t-\t'+location.locationId+'\t'+name
            else:
                if (location.locationId not in locations_nfree):
                    print u'\t?\t'+loc_log+name
                else:
                    print u'\t+\t'+loc_log+name
        if locations:
            print u'Находимся на острове:'
            self.cprint (u'5        *       %s' % (self.__itemReader.get(self.get_game_loc().get_location_id()).name))
            print
            #location_name = self.__user_prompt.prompt_user(u'Выберите остров:',locations.keys())
            location_name = locations.keys()[0]
            if location_name in locations:
                self.__selected_location  = locations[location_name].locationId
            else:
                self.__selected_location  = self.get_game_loc().get_location_id()

    def select_location_logger(self): # logger
        logger.info(u'Доступные острова:')
        logger.info(u'(+ платный, - бесплатный, ? - пещера)')
        locations_nfree = [u'isle_01', 'isle_small', 'isle_star', 'isle_large', 'isle_moon', 'isle_giant', 'isle_xxl', 'isle_desert']
        locations_nwalk = [u'un_0'+str(x+1) for x in range(9)]

        locations = {}
        for location in self.get_game_state().locationInfos:
            name = self.__itemReader.get(location.locationId).name
            loc_log = location.locationId.ljust(18, ' ')
            if (location.locationId not in locations_nfree) and (location.locationId not in locations_nwalk):
                locations[name] = location
                logger.info('\t-\t'+loc_log+name)
                #logger.info('\t-\t'+location.locationId+'\t'+name)
            else:
                if (location.locationId not in locations_nfree):
                    logger.info('\t?\t'+loc_log+name)
                else:
                    logger.info('\t+\t'+loc_log+name)
        if locations:
            logger.info(u'Находимся на острове:')
            logger.info(u'   *       '+self.__itemReader.get(self.get_game_loc().get_location_id()).name)
            logger.info("")
            #location_name = self.__user_prompt.prompt_user(u'Выберите остров:',locations.keys())
            location_name = locations.keys()[0]
            if location_name in locations:
                self.__selected_location  = locations[location_name].locationId
            else:
                self.__selected_location  = self.get_game_loc().get_location_id()

    def get_user_setting(self, setting_id):
        return self.__settings.get

    def running(self):
        if self.__gui_input:
            running = self.__gui_input.running
        else:
            running = lambda: True
        return running()

    def start(self):

        SetConsoleTextAttribute(stdout_handle, 0x0001 | 0x0070)
        game_state = self.get_game_state
        wait_refresh = self.__mega.wait_refresh_sec()        
        while(self.running()):
            try:
                # load items dictionary
                if self.__itemReader is None:
                    print u'Загружаем словарь объектов...  ',
                    item_reader = GameItemReader(self.__settings)
                    item_reader.download('items.txt')
                    item_reader.read('items.txt')
                    self.__itemReader = item_reader
                    print u'Словарь объектов загружен'
                    compositions = GameCompositionReader(self.__settings,self.__selected_curuser)
                    print u'Загружаю размеры обьектов...'
                    compositions.loadComposit('compositions')

                start_response,self.__friendsid,self.__server_time = self.__game_initializer.start()
                # Save Game_state
                # open("game_state.txt","w").write(str(obj2dict(start_response)))
                
                self.__game_events_sender = self.__game_initializer.create_events_sender()

                self.save_game_state(start_response)
                self.__game_state_.get_state().log_print = False
                
                # GetMissionsBot(self.__itemReader, self.__game_state_, self.__game_events_sender, self._get_timer(),{}).perform_action()
                
                self.select_location()
                # self.select_plant_seed()
                # self.select_recipe()
                self.create_all_actors()

                # TODO send getMissions
                # TODO handle getMissions response
                
                # self.clear_auto_pirate()
                if self.__mega.storage2file()['activated']:
                    self._storage2file()
                self.load_friends_names()
                if self.__mega.get_load_info_users():
                    self.load_info_users()
                
                self.eventLoop()
                if not self.__mega.get_loop():
                    exit(0)

            except urllib2.HTTPError, e:
                raise e
            except (socket.timeout, urllib2.HTTPError, urllib2.URLError):
                seconds = random.randint(wait_refresh[0], wait_refresh[1])
                logger.error('Timeout occurred, retrying in %s seconds...'
                             % seconds)
                time.sleep(seconds)
            except (socket.error, ssl.SSLError) as e:
                seconds = random.randint(wait_refresh[0], wait_refresh[1])
                logger.error('Socket error occurred, retrying in %s seconds...'
                             % seconds)
                time.sleep(seconds)
            except message_factory.GameError, e:
                time.sleep(1)
                if not self.__ignore_errors: # 0
                    raise e

    def save_game_state(self, start_response):
        # parse game state
        self.__game_state_ = GameState(start_response, self.__itemReader, self.__settings, self.__selected_curuser, len(self.__friendsid), self.__timer)

    def get_game_loc(self):
        return self.__game_state_.get_game_loc()

    def get_game_state(self):
        return self.__game_state_.get_state()

    def clear_auto_pirate(self):
        parser = ConfigParser.RawConfigParser()
        parser.read('avto_pirate.ini')
        try:
            parser.add_section('global_info')
        except ConfigParser.DuplicateSectionError:
            pass
        parser.set('global_info', 'all_pirates', '0')
        with open('avto_pirate.ini', 'wb') as fp:
            parser.write(fp)

    def load_friends_names(self):        
        try:
            with open('statistics\\'+self.__selected_curuser+'\\friends_names.txt', 'r') as f:
                self.__game_state_.friends_names = eval(f.read())
        except:
            self.__game_state_.friends_names = {}

    def load_friends_active_game(self):
        try:
            with open('statistics\\'+self.__selected_curuser+'\\friends_active_game.txt', 'r') as f:
                self.__game_state_.friends_active_game = eval(f.read())
        except:
            self.__game_state_.friends_active_game = {}
        for friends_id in self.__friendsid:
            self.__game_state_.friends_active_game.setdefault(friends_id, ['0', '0'])
        with open('statistics\\'+self.__selected_curuser+'\\friends_active_game.txt', 'w') as f:
            f.write(str(self.__game_state_.friends_active_game))

    def load_info_users(self):
        self.__game_state_.get_state().log_print = False
        players = []
        all = len(self.__friendsid)
        current = 0
        for num_pl in range(all):
            players.append(self.__friendsid[num_pl])
            if len(players) == 100 or num_pl == all - 1:
                events = {"type":"players","id":3,"action":"getInfo","players":players}
                self.__game_events_sender.send_game_events([events])
                current += len(players)
                sys.stdout.write(u'\rЗагружаем информацию о друзьях ... %d%% ' % (current*100/all))
                self.handle_all_events()
                players = []
        sys.stdout.write('\r\n')
        print
        #time.sleep(2)
        self.__game_state_.get_state().log_print = True

    def load_info_users_old(self):
        friends_copy = self.__friendsid[:]
        players = []
        print u'Загружаем информацию о друзьях',
        while len(friends_copy):
            players.append(friends_copy.pop())
            if len(players) == 100:
                events = {"type":"players","id":3,"action":"getInfo","players":players}
                self.__game_events_sender.send_game_events([events])
                print u'\b.',
                self.handle_all_events()
                players = []
        if players:
            events = {"type":"players","id":3,"action":"getInfo","players":players}
            self.__game_events_sender.send_game_events([events])
            print u'\b.',
            self.handle_all_events()    
        print u'\b.'
        #self.wait(2)
        #time.sleep(2)
        pass

    def _storage2file(self):  # вывод склада фейков-пиратов
        predmet = self.__mega.storage2file()['predmet']
        collect = self.__mega.storage2file()['collect']
        
        item = '@CASH'
        name = self.__itemReader.get(item).name
        count = self.__game_state_.get_state().cashMoney
        zb = u'' + name.ljust(28, ' ') + item.ljust(28, ' ') + unicode(count) +'\n'
        item = '@COINS'
        name = self.__itemReader.get(item).name
        count = self.__game_state_.get_state().gameMoney
        coins = u'' + name.ljust(28, ' ') + item.ljust(28, ' ') + unicode(count) +'\n'
        item = '@DUBLON'
        name = self.__itemReader.get(item).name
        count = self.__game_state_.count_in_storage('@DUBLON')
        dublon = u'' + name.ljust(28, ' ') + item.ljust(28, ' ') + unicode(count) +'\n'

        giftCoins = 35000
        for loc_info in self.__game_state_.get_state().locationInfos:
            giftCoins += loc_info.giftCoins
        for obj in self.__game_state_.get_state().gameObjects:
            if '_SKLAD_' in obj.item:
                reader = self.__itemReader.get(obj.item).giftCoinses[0]
                if obj.level == reader.level:
                    giftCoins += reader.count
                # "giftCoinses":[{"level":3,"count":5000}
        item = 'giftCoins'
        name = u'Лимит подарков'
        gc = u'' + name.ljust(28, ' ') + item.ljust(28, ' ') + unicode(giftCoins) +'\n'

        item = 'giftCoinsFree'
        name = u'Свободный лимит'
        giftCoinsFree = giftCoins - self.__game_state_.get_state().receivedGiftsCoins
        gco = u'' + name.ljust(28, ' ') + item.ljust(28, ' ') + unicode(giftCoinsFree) +'\n'

        storage1 = u''
        for mat in predmet:
            name = self.__itemReader.get(mat).name
            count = self.__game_state_.count_in_storage(mat)
            storage1 += u'' + name.ljust(28, ' ') + mat.ljust(28, ' ') + unicode(count) +'\n'

        storage3 = u''
        for item in collect:
            name = self.__itemReader.get(item).name
            coll = []
            for num in range(1,6):
                if hasattr(self.__game_state_.get_state().collectionItems, item + '_' + str(num)):
                    coll.append(getattr(self.__game_state_.get_state().collectionItems, item + '_' + str(num)))
            if len(coll) < 5:
                count = 0
            else:
                count = min(coll)
            storage3 += u'' + name.ljust(28, ' ') + item.ljust(28, ' ') + unicode(count) +'\n'

        text = gc + gco + zb + coins + dublon
        text += '\n'+'\n' + storage1
        text += '\n'+'\n' + storage3
        # text += '\n'+'\n' + storage2 + '\n'

        curuser = str(self.__game_state_.get_curuser())
        with open('statistics\storage_'+curuser+'.txt', 'w') as f:
           f.write(text.encode('utf-8'))

    def wait(self, pause):
        print u'Загружаем информацию о друзьях',
        while pause > 0:
            print u'\b.',
            time.sleep(0.2)
            pause -= 0.2
        print u'\b.'

    def eventLoop(self):
        '''
        in a loop, every 30 seconds
        send EVT request
        handle EVT response
        '''
        refresh_min = self.__mega.refresh_min()
        ref_min = []
        while(self.running()):
            condition = self.perform_all_actions()
            if condition == 100:
                logger.info(u'Принудительно перезапускаем')
                break
            time.sleep(0.3)
            
            cur_time = self.__timer._get_current_client_time()
            min = int(int(cur_time/1000)/60)
            # if min not in ref_min:
                # if (refresh_min-min) == 1: logger.info(u'Перезагрузка через %s минуту'%str(refresh_min-min))
                # elif ((refresh_min-min) >= 2) and ((refresh_min-min) <= 4): logger.info(u'Перезагрузка через %s минуты'%str(refresh_min-min))
                # else: logger.info(u'Перезагрузка через %s минут'%str(refresh_min-min))
                # ref_min += [min]
            if min not in ref_min:
                if (refresh_min - min) == 1: self.cprint(u'1Перезагрузка через ^4_%s^1минуту'%str(refresh_min-min))
                elif ((refresh_min - min) >= 2) and ((refresh_min-min) <= 4): self.cprint(u'1Перезагрузка через ^4_%s^1минуты'%str(refresh_min - min))
                else: self.cprint(u'1Перезагрузка через :^4_%s^1минут'%str(refresh_min-min))
                ref_min += [min]
            if min >= refresh_min:
                ref_min = []
                break

    def create_all_actors(self):
        options = {'SeederBot': self.__selected_seed,
                   'CookerBot': self.__selected_recipe,
                   'SendColl':self.__selected_send,
                   'SellBot':self.__selected_sell,
                   # 'ChangeLocationBot':self.__selected_location,
                   'ChangeLocationBot':self.__selected_loc_setting,
                   'DigBot':self.__selected_dig_friends,
                   'PremiumGifts':self.__selected_PremiumGifts
                   }
        events_sender = self.__game_events_sender
        timer = self._get_timer()
        item_reader = self.__itemReader
        game_state = self.__game_state_
        actor_classes = self.__mega.actor_options()

        self.free_spaces = FreeSpace(item_reader, game_state, events_sender, timer, self, options, self.__mega, self.__friendsid)
        self.__actors = [Standing(item_reader, game_state, events_sender, timer, self, options, self.__mega, self.__friendsid)]
        for actor_class in actor_classes:
            self.__actors.append(
                actor_class(item_reader, game_state, events_sender, timer, self, options, self.__mega, self.__friendsid))

    def perform_all_actions(self):
        game_state = self.__game_state_
        '''
        Assumes that create_all_actors is called before
        '''
        self.title()
        all_time = []
        for actor in self.__actors:
            # time_one = time.time()
            condition = actor.perform_action()
            # time_two = time.time()
            # logger.info(u'Класс %s' % (str(actor).split()[0].split('.')[-1]))
            # logger.info(u'Выполнялся %f' % (time_two-time_one))
            # all_time += [[str(actor).split()[0].split('.')[-1],(time_two-time_one)]]
            self.handle_all_events()
            # pdb.set_trace()
            if condition == 100: break
        # open('time.txt','a').write(str(all_time) + '\n\n')
        self.__game_events_sender.send_game_events()
        self.handle_all_events()
        if hasattr(game_state,'getcoins') and game_state.getcoins > 0:
            logger.info(u'Подобрали %d монет' % (game_state.getcoins))
            del game_state.getcoins
        if hasattr(game_state,'getxp') and game_state.getxp > 0:
            logger.info(u'Подобрали %d опыта' % (game_state.getxp))
            del game_state.getxp
        if condition == 100: return 100
        # exit()

    def handle_all_events(self):
        self.alerts = []
        self.res_types = []
        self.game_result = []
        self.ping = False
        self.__game_events_sender.print_game_events()
        for event in self.__game_events_sender.get_game_events():
            self.handleEvent(event)

    def handleEvent(self, event_to_handle):
        log_print = self.__game_state_.get_state().log_print
        # print (obj2dict(event_to_handle))
        # if event_to_handle.action[:4] != 'ping' and\
                    # event_to_handle.action != 'getInfo':  # event_to_handle.type != 'gameState' and\
            # with open('statistics\\'+self.__selected_curuser+'\\event_to_handle.txt', 'a') as f:
                # f.write(str(obj2dict(event_to_handle)).encode('utf-8')+'\n'+'-----------------------------------------------------------------------------------\n')
        # if event_to_handle.action != 'getInfo':
            # with open('statistics\\'+self.__selected_curuser+'\\events.txt', 'a') as f:
                # f.write(str(obj2dict(event_to_handle)).encode('utf-8')+"\n"+"\n")
        self.res_types.append(event_to_handle.type)
        if event_to_handle.type == 'alert': # and not (event_to_handle.msg in self.alerts):
            if not (event_to_handle.msg in self.alerts):
                logger.info('Alert! '+event_to_handle.msg)
            # коррекция удобренных деревьев
            if event_to_handle.msg == 'SERVER_REMOTE_FERTILIZE_FRUIT_TREE_NOT_FOUND':
                #print dir(self.__game_state_.get_state())
                self.cprint(u'4Дерево нельзы полить, удаляем из списка')
                nop = self.__game_state_.get_state().remoteFertilizeFruitTree.pop()
            else:
                self.alerts.append(event_to_handle.msg)
            # print 'Alert! ', event_to_handle.msg, ' type = ', event_to_handle.type
            # if event_to_handle.msg == 'SERVER_NEW_YEAR_GIFT_NOT_ALLOW':
                # self.__game_state_.nyna = 1    
            # if event_to_handle.msg == 'SERVER_REMOTE_TREASURE_ALL_DIGGED':
                # self.__game_state_.alldigged = 1
            # if event_to_handle.msg == 'SERVER_REMOTE_FERTILIZE_FRUIT_TREE_NOT_FOUND':
                # self.__game_state_.get_state().haveRemoteFertilizeFruit = False
            
        elif event_to_handle.action == 'getInfo': # and event_to_handle.type == 'playersInfo':
            self.add_users_info(event_to_handle)
        elif event_to_handle.type == 'monsterPitDigEvent':
            name = self.addName(event_to_handle)
            sms = u'Сосед ' + name + u' закопал нам медведя на ' + unicode(event_to_handle.count) + u' м.'
            if log_print: logger.info(u'%s' % sms)
            self.add_action_frends(sms)
        elif event_to_handle.type == 'pirateShip':
            name = self.addName(event_to_handle)
            sms = u'Сосед ' + name + u' вошёл в команду корабля'
            if log_print: logger.info(u'%s' % sms)
            self.add_action_frends(sms)
        elif event_to_handle.action == u'pirateCheckin':
            name = self.addName(event_to_handle)
            sms = u'Сосед ' + name + u' застукал наш пиратский сундук'
            logger.info(u'%s' % sms)
            self.add_action_frends(sms)
        elif event_to_handle.action == u'sendThanksgivingGift':  # event_to_handle.type == u'thanksgivingTable'
            name = self.addName2(event_to_handle)
            count1 = str(event_to_handle.user.present.count)
            item1 = event_to_handle.user.present.item
            sms = u'Сосед ' + name + u' стукнул нам в туковую. Получили ' + count1 + u' шт. ' + item1[1:]
            if log_print: logger.info(u'%s' % sms)
            self.add_action_frends(sms)
        elif event_to_handle.type == u'pirateDeath':
            logger.info(u'Вышло время застуканного сундука. Мы больше не пираты')
            self.__game_state_.get_state().pirate.state = 'DEAD'
        elif event_to_handle.type == u'pirateState':
            self.__game_state_.get_state().pirate.state = event_to_handle.state
        elif event_to_handle.action == u'readyToSail':
            #{u'action': u'readyToSail', u'ship': u'@B_PIRATE_SCHOONER_2', u'captain': u'13559763416637162308', u'type': u'pirateSail'}
            name = self.addName(event_to_handle)
            sms = u'Сосед ' + name + u' отплыл на пиратский остров'
            if log_print: logger.info(u'%s' % sms)
            self.add_action_frends(sms)
            self.__game_state_.get_state().pirate.state = 'AWAY'
            self.__game_state_.get_state().pirate.ship = event_to_handle.ship
            self.__game_state_.get_state().pirate.captain = event_to_handle.captain
        elif event_to_handle.action == 'exchange':
            name = self.addName(event_to_handle)
            torg = unicode(event_to_handle.objId)
            sms = u'Сосед ' + name + u' произвёл обмен у торговца ' + torg
            if log_print: logger.info(u'%s' % sms)
            self.add_action_frends(sms)
        elif event_to_handle.type == 'bridge':
            if log_print: logger.info(u'Туристы потеряли чемодан')
        elif event_to_handle.action == u'completeMission' and event_to_handle.type == u'npc':
            sms = u'Мы выполнили  желание "Любви"'
            if log_print: logger.info(u'%s' % sms)
        elif event_to_handle.action == 'addGift':
            AddGiftEventHandler(self.get_game_state()).handle(event_to_handle, log_print)
        elif event_to_handle.action[:4] == 'ping':
            # print 'PING', event_to_handle.action
            self.ping = True
            if event_to_handle.action[:5] == 'ping1':
                time.sleep(0.005)
                self.__game_events_sender.send_game_events([])
            elif event_to_handle.action[:5] == 'ping2':
                time.sleep(0.05)
                self.__game_events_sender.send_game_events([])
        elif event_to_handle.type == 'exploration' and hasattr(event_to_handle, 'gameObjects'):
            for obj in list(event_to_handle.gameObjects):
                if obj.item == u'@B_STONE_WELL':
                    self.get_game_loc().remove_object_by_id(obj.id)
                #print u'Добавим', obj.item.ljust(27, " "), ' id = ', obj.id
                self.get_game_loc().append_object(obj)
        elif event_to_handle.type == 'pirateEnemy' and event_to_handle.action == 'alreadyHitted':
            # {u'action': u'alreadyHitted', u'health': 2L, u'objId': -8328L, u'type': u'pirateEnemy'}
            pass
        elif event_to_handle.action == 'add' and event_to_handle.type == 'pickup':
            AddPickupHandler(self.__itemReader, self.get_game_loc(),self.__game_state_,self.__setting_view).handle(event_to_handle)
        elif event_to_handle.type == GameFertilizePlant.type:
            PlantEventHandler(self.get_game_loc()).handle(event_to_handle)
        #elif event_to_handle.type == GamePlayGame.type:
        elif event_to_handle.type == 'dailyBonus' or event_to_handle.type == 'wizardNpcPlay' or event_to_handle.type == GamePlayGame.type:
            self.game_result.append(event_to_handle.type)
            GameResultHandler(self.__itemReader,self.get_game_loc(),self.__game_state_).handle(event_to_handle)
        elif event_to_handle.type == GameStartGainMaterial.type:
            GainMaterialEventHandler(self.__itemReader, self.get_game_loc(),
                                     self.__timer).handle(event_to_handle)
        elif event_to_handle.type == GameStartTimeGainEvent.type:
            TimeGainEventHandler(self.__itemReader, self.get_game_loc(),
                                 self.__timer).handle(event_to_handle)
        elif event_to_handle.type == 'gameState':
            #print 'gameState'
            #with open('events.txt', 'a') as f:
            #    f.write(str(obj2dict(event_to_handle)).encode('utf-8')+"\n"+"\n")
            self.__game_state_.gameObjects = event_to_handle.gameObjects #объекты
            GameStateEventHandler(self.__game_state_, self.__server_time,self.__setting_view).handle(event_to_handle)
        elif event_to_handle.type == 'mission':
            # ViewMissions(self.__itemReader, self.__setting_view).handle(event_to_handle)
            pass
        # elif event_to_handle.type == 'playersInfo': # информация о пользователе
            # self.__game_state_.playersInfo = event_to_handle.players
        elif event_to_handle.action == 'buried' or event_to_handle.action == 'cook' or\
                event_to_handle.type == 'newYearTree' or event_to_handle.action == 'changeObject' or\
                event_to_handle.action == 'buyedBrains' or event_to_handle.action == 'releaseBrains' or\
                event_to_handle.action == 'stopRequest' or event_to_handle.type == 'pirateCapture' or\
                event_to_handle.action == 'sendNewYearGift':
            pass
        elif event_to_handle.action == 'changeTask' or event_to_handle.action == 'completeTask' or\
                event_to_handle.action == 'completeMission': # миссии Любви
            pass
        else:
            # self.logUnknownEvent(event_to_handle)
            pass
        self.__game_events_sender.remove_game_event(event_to_handle)

    def get_free_spaces(self):
        return self.free_spaces

    def add_action_frends(self, sms):
        with open('statistics\\'+self.__selected_curuser+'\\action_frends.txt', 'a') as f:
            _time = datetime.datetime.today().strftime("%Y.%m.%d %H:%M:%S")
            sms = _time + u' ' + sms + u'\n'
            f.write(sms.encode('utf-8'))
                
    def add_users_info(self, event_to_handle):
        self.__game_state_.resp = True
        if not hasattr(self.__game_state_, 'playersInfo'):
            self.__game_state_.playersInfo = event_to_handle.players
        else:
            for new_info in event_to_handle.players:
                for info in self.__game_state_.playersInfo:
                    if new_info.id == info.id:
                        del info
                        break
            self.__game_state_.playersInfo.extend(event_to_handle.players)

        data = {}
        for n in event_to_handle.players:
            #if hasattr(self.__game_state_, 'friends_names') and self.__game_state_.friends_names.get(n.id): continue # если уже есть
            #print n
            #print 'n.id', n.id
            if hasattr(n, 'name') and n.name:
                name_ = n.name
                while '{' in name_ or '}' in name_ or '[' in name_ or ']' in name_ or '^' in name_ or\
                        u'«' in name_ or u'»' in name_:
                    for l in u'{}[]^«»':
                        name_ = name_.replace(l, '')
                if u'\u0456' in name_:
                    name_ = name_.replace(u'\u0456', u'i')
                #print n.name.replace(u'\u0456', u'i').encode("cp866", "ignore")
                #print n.name.decode('unicode-escape').replace(u'\u0456', u'i')
            else:
                name_ = u''
                #name_ = u'Без имени'
            data[n.id] = name_

        if data:
            if hasattr(self.__game_state_, 'friends_names'):
                self.__game_state_.friends_names.update(data)
            else:
                self.__game_state_.friends_names = data
            if self.__mega.save_users_id_nick():
                with open('statistics\\'+self.__selected_curuser+'\\friends_names.txt', 'w') as f:
                    text = u"{"
                    for el in self.__game_state_.friends_names.keys():
                        if text != u"{": text += u", "
                        text += u"u'" + el + u"': u'" + self.__game_state_.friends_names[el] + u"'"
                    text += u"}"
                    f.write(text.encode("UTF-8", "ignore")) # сохраняем friends_names.txt

        if 0: #  списки ниже 20 уровня и забаненных
            try:
                with open('statistics\\'+self.__selected_curuser+'\\low_level.txt', 'r') as f:
                    self.__game_state_.low_level = eval(f.read())
            except:
                self.__game_state_.low_level = []
            try:
                with open('statistics\\'+self.__selected_curuser+'\\banned.txt', 'r') as f:
                    self.__game_state_.banned = eval(f.read())
            except:
                self.__game_state_.banned = []
            lovl = []
            banned = []
            for n in event_to_handle.players:
                if hasattr(n, 'level') and int(n.level) < 20 and (n.id not in self.__game_state_.low_level): lovl.append(n.id)
                if hasattr(n, 'banned') and n.banned and (n.id not in self.__game_state_.banned): banned.append(n.id)
            if lovl:
                self.__game_state_.low_level.extend(lovl)
                with open('statistics\\'+self.__selected_curuser+'\\low_level.txt', 'w') as f:
                    f.write(str(self.__game_state_.low_level))
            if banned:
                self.__game_state_.banned.extend(banned)
                with open('statistics\\'+self.__selected_curuser+'\\banned.txt', 'w') as f:
                    f.write(str(self.__game_state_.banned))
        
        # self.add_friends_active_game(event_to_handle)  # обновляем инфу о последнем посещении
        pass
        
    def add_friends_active_game(self, event_to_handle):
        data = [datetime.date.today().strftime("%Y.%m.%d"), datetime.date.today().strftime("%j")]
        for n in event_to_handle.players:
            if n.liteGameState.haveTreasure:
                self.__game_state_.friends_active_game[n.id] = data
        with open('statistics\\'+self.__selected_curuser+'\\friends_active_game.txt', 'w') as f:
            f.write(str(self.__game_state_.friends_active_game))

    def addName(self, event_to_handle):
        if hasattr(event_to_handle, 'user'):
            id = event_to_handle.user
            if hasattr(self.__game_state_, 'friends_names') and self.__game_state_.friends_names.get(id) and self.__game_state_.friends_names.get(id) != u'':
                name = u" '" + self.__game_state_.friends_names.get(id) + u"'"
                name = name.replace(u'\u0456', u'i').encode("UTF-8", "ignore")
                name = unicode(name, "UTF-8")
                #print name.replace(u'\u0456', u'i').encode("cp866", "ignore")
            else: name = u''
            id_name = unicode(id).ljust(20, " ") + (name).ljust(16, " ")
        else: id_name = u' ' * 35
        return id_name

    def addName2(self, event_to_handle):
        if hasattr(event_to_handle, 'user'):
            #print 'event_to_handle.user', event_to_handle.user
            #print 'event_to_handle.user.id', event_to_handle.user.id
            #print 'event_to_handle.user.present.count', event_to_handle.user.present.count
            
            id = event_to_handle.user.id
            if hasattr(self.__game_state_, 'friends_names') and self.__game_state_.friends_names.get(id) and self.__game_state_.friends_names.get(id) != u'':
                name = u" '" + self.__game_state_.friends_names.get(id) + u"'"
                name = name.replace(u'\u0456', u'i').encode("UTF-8", "ignore")
                name = unicode(name, "UTF-8")
                #print name.replace(u'\u0456', u'i').encode("cp866", "ignore")
            else: name = u''
            id_name = unicode(id).ljust(20, " ") + (name).ljust(16, " ")
        else: id_name = u' ' * 35
        return id_name
        
    def logUnknownEvent(self, event_to_handle):
        curuser = self.__selected_curuser
        t = datetime.datetime.today().strftime(' %Y.%m.%d %H:%M:%S ')
        logger = logging.getLogger('unknownEventLogger')
        #logger.info(pprint.pformat(obj2dict(event_to_handle)))
        with open('f_unknownEvent.txt', 'a') as f:
            f.write(str(curuser)+t+str(obj2dict(event_to_handle))+'\n')
            f.write('-----------------------------------------------------------------------------------\n')

    def _get_timer(self):
        return self.__timer

    def get_request_sender(self):
        return self.__request_sender
        
    def cprint(self, cstr):
        clst = cstr.split('^')
        color = 0x0001
    
        for cstr in clst:
            dglen = re.search("\D", cstr).start()
            color = int(cstr[:dglen])
            text = cstr[dglen:]
            if text[:1] == "_": text = text[1:]
            SetConsoleTextAttribute(stdout_handle, color | 0x0070) #78
            print text,
        #sys.stdout.flush()
        print ""
        SetConsoleTextAttribute(stdout_handle, 0x0001 | 0x0070)

    def title(self):
        playerBrains = self.__game_state_.get_brains()
        total_brain_count = playerBrains.get_total_brains_count()
        occupied_brain_count = playerBrains.get_occupied_brains_count()
        #total_brain_count = self.__game_state_.get_brains().get_total_brains_count()
        #occupied_brain_count = self.__game_state_.get_brains().get_occupied_brains_count()
        #print total_brain_count, occupied_brain_count

        x1 = 0
        z = 0
        #print dir(self.__game_state_)
        for burySlot in self.__game_state_.get_state().burySlots: #можно так self.get_game_state().burySlots
            x1 += 1
            if (hasattr(burySlot, u"user") is True): z += 1

        Money=''
        for i in range(len(str(self.__game_state_.get_state().gameMoney)),0,-3):
            if i >= 3: Money=str(self.__game_state_.get_state().gameMoney)[i-3:i]+'.'+Money
            else: Money=str(self.__game_state_.get_state().gameMoney)[:i]+'.'+Money

        if hasattr(self.__game_state_.get_state(), "cashMoney"):
            zb = self.__game_state_.get_state().cashMoney

        dub = self.__game_state_.count_in_storage('@DUBLON')
        os.system((u'title '+self.__selected_curuser+u"  Lev:"+str(self.__game_state_.get_state().level)+u' Мозги:' + str(occupied_brain_count)+'/'+str(total_brain_count)+u' Слоты:'+str(z)+'/'+str(x1) + u'  ЗБ:'+str(zb) + u' Монет:'+str(Money[:-1]) + u' Дуб:'+str(dub)).encode('cp1251', 'ignore'))


class RequestSender(object):
    def __init__(self, message_factory, connection, _time):
        self.__factory = message_factory
        self.__connection = connection
        self.__time = _time

    def send(self, data):
        data = obj2dict(data)
        assert 'type' in data
        if data['type'] == 'EVT':
            data['time'] = int(self.__time._get_current_client_time())
            # print 'TIME', data['time']
        request = self.__factory.createRequest(data)
        return dict2obj(request.send(self.__connection))

    def set_url(self, url):
        self.__connection.setUrl(url)

    def clear_session(self):
        self.__factory.setSessionKey(None)

    def reset_request_id(self):
        request_id = message_factory._getInitialId()
        self.__factory.setRequestId(request_id)

    def set_auth_key(self, auth_key):
        self.__factory.set_auth_key(auth_key)
