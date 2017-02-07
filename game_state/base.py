# coding=utf8
##############################
import logging
from ctypes import windll
import sys
import re
import time
import os.path
from math import ceil
import random  as  random_number
import ConfigParser
from game_state.game_event import dict2obj, obj2dict

stdout_handle = windll.kernel32.GetStdHandle(-11)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
##############################

logger = logging.getLogger(__name__)


class BaseActor(object):
    def __init__(self, item_reader, game_state, events_sender, 
                timer, game, options, mega, friendsid):
        self.__mega = mega
        self.__game = game
        self.__item_reader = item_reader
        self.__game_state = game_state
        self.__events_sender = events_sender
        self.__friendsid = friendsid
        if self.__class__.__name__ in options:
            self.__options = options[self.__class__.__name__]
        self.__timer = timer

    def _get_game(self):
        return self.__game

    def _get_options(self):
        return self.__options

    def mega(self):
        return self.__mega

    def get_friendsid(self):
        return self.__friendsid

    def _get_item_reader(self):
        return self.__item_reader

    def _get_game_state(self):
        return self.__game_state

    def _get_events_sender(self):
        return self.__events_sender

    def _get_timer(self):
        return self.__timer

    def _get_game_location(self):
        location = self._get_game_state().get_game_loc()
        return location

    def _get_player_brains(self):
        return self._get_game_state().get_brains()

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

    def location_id(self):
        return self._get_game_state().get_game_loc().get_location_id()

    def if_location_pirate(self):
        # пиратские острова : Остров сокровищ, Таинственный, Жуткий, Северный полюс, Остров сокровищ, Древний
        pirate_locs_id = ['exploration_isle1_random','exploration_isle2_random','exploration_isle3_random','exploration_snow1','exploration_isle1_1','exploration_isle4_random','exploration_independent_asteroid_random']
        return (self.location_id() in pirate_locs_id)

    def if_location_only_pirate(self):
        # пиратские острова : Остров сокровищ, Таинственный, Жуткий
        pirate_locs_id = ['exploration_isle1_random','exploration_isle2_random','exploration_isle3_random']
        return (self.location_id() in pirate_locs_id)

    def send(self, events):
        return self._get_events_sender().send_game_events(events)

    def money(self):
        return self._get_game_state().get_state().gameMoney

    def cash(self):
        return self._get_game_state().get_state().cashMoney

    def xp(self):
        return self._get_game_state().get_state().experience

    def my_level(self):
        return self._get_game_state().get_state().level

    def clock(self, timems):
        timems = int(timems)
        h = timems/1000/60/60
        m = timems/1000/60 - (h*60)
        s = round(timems/float(1000) - (timems/1000/60*60), 3)
        ms = timems - (timems/1000*1000)
        # print u'Время: %d:%d:%.3f'%(h,m,s)
        return str(h) + ':' + str(m) + ':' + str(s)

    def write_log(self, text, pref=''):
        if not self.mega().err_log(): return
        __date = time.strftime('%Y.%m.%d %H:%M:%S  ', time.localtime(time.time()))
        data = pref + __date + text + u'\n'
        with open('statistics\\log_' + self._get_game_state().get_curuser() + '.txt', 'a') as f:
            f.write(data.encode('utf-8'))

    def has_in_storage(self,item,count):
        return self._get_game_state().has_in_storage(item,count)

    def craft_item_count(self,item):
        if item == '@COINS': return self.money()
        if item == '@CASH': return self.cash()
        if item == '@XP': return self.xp()
        if item.startswith('@C_'):
            item_lstrip = item.lstrip('@')
            collectionItems = self._get_game_state().get_state().collectionItems
            return 0L if not hasattr(collectionItems,item_lstrip) else getattr(collectionItems,item_lstrip)
        if u'@BRAINS_' in item:
            brains_buy = self._get_game_state().get_state().buyedBrains # кол-во активаций мозгов (не самих мозгов)
            brains_const = self._get_game_state().get_state().brainsCount # количество постоянных (от уровня)
            brains_curr = 0 # счетчик кол-ва текущих мозгов
            # print u'current_client_time:', self._get_timer().client_time(), u' -', self.clock(self._get_timer().client_time())
            if len(brains_buy) <> 0:
                for buyed_brain in brains_buy:
                    # print u'count', buyed_brain.count, u' endTime', buyed_brain.endTime, u'  - ', self.clock(buyed_brain.endTime), u'осталось:'
                    if not self._get_timer().has_elapsed_in(buyed_brain.endTime, 7*60): # Кроме истекоющего времени < 7 мин.
                        brains_curr += buyed_brain.count
            # print u'В наличии мозгов', brains_const + brains_curr
            # print u'Из них постоянных:', brains_const
            return brains_const + brains_curr
        return self._get_game_state().count_in_storage(item)

    def add_crafted_item(self,item,count):
        if item == '@COINS':
            self._get_game_state().get_state().gameMoney += count
            return
        if item == '@CASH':
            self._get_game_state().get_state().cashMoney += count
            return
        if item == '@XP':
            self._get_game_state().get_state().experience += count
            return
        if item.startswith('@C_'):
            item_lstrip = item.lstrip('@')
            collectionItems = self._get_game_state().get_state().collectionItems
            has = 0L if not hasattr(collectionItems,item_lstrip) else getattr(collectionItems,item_lstrip)
            setattr(collectionItems,item_lstrip,has + count)
            return
        if item == u'@BRAINS_1':
            for i in range(count):
                self._get_game_state().get_state().buyedBrains.append(dict2obj({u'count': 1L, u'endTime': u'86400000'}))
            return
        if item == u'@BRAINS_8':
            for i in range(int(count/7)):
                self._get_game_state().get_state().buyedBrains.append(dict2obj({u'count': 8L, u'endTime': u'86400000'}))
            return
        self._get_game_state().add_from_storage(item, count)

    def __get_building_craft(self,building,craft_id):
        return filter(lambda(obj):obj.id == craft_id,self._get_item_reader().get(building).crafts)[0]

    def craft_available(self,building,craft_id):
        craft = self.__get_building_craft(building,craft_id)
        #проверка сколько можно макс сделать
        return min(self.craft_item_count(material.item) / material.count for material in craft.materials)

    def __find_building(self,building,craft_id):
        building_obj = []
        craft = self.__get_building_craft(building,craft_id)
        if ((u'@BRAINS_' in craft.result) or (u'@CASH' in craft.result)) and\
                self._get_game_state().get_state().playerStatus != u'@PS_HUMAN':
            return (building_obj, craft)
        for item in self._get_game_state().get_state().gameObjects:
            if (item.item == '@' + building) and (item.level >= craft.level):
                if not hasattr(item,'nextPlayTimes') or\
                        not hasattr(craft,'craftId') or\
                        not hasattr(item.nextPlayTimes, craft.craftId) or\
                        self._get_timer().has_elapsed(long(getattr(item.nextPlayTimes,craft.craftId))):
                    building_obj.append(item) # item.id
        return (building_obj, craft)

    def new_id(self):
        # next_id = max([_i.maxGameObjectId for _i in self._get_game_state().get_state().locationInfos])
        # for object in self._get_game_location().get_game_objects():
            # if object.id > next_id: next_id = object.id
        # next_id += 1
        has_max_id = [_i.maxGameObjectId for _i in self._get_game_state().get_state().locationInfos] + [_m.id for _m in self._get_game_location().get_game_objects()]
        if len(has_max_id) > 1:
            next_id = max(has_max_id) + 1
        elif len(has_max_id) == 1:
            next_id = has_max_id[0] + 1
        else:
            next_id = 1
        return next_id
        
        # next_id = max([_i.maxGameObjectId for _i in self._get_game_state().get_state().locationInfos] + [_m.id for _m in self._get_game_state().get_state().gameObjects]) + 1

    def craft_count(self,building,craft_id,count,max_count_once=500):
        if self.if_location_pirate(): return 0, ''
        building_obj, craft = self.__find_building(building,craft_id)
        if not building_obj: return (0, '')

        # craft = self.__get_building_craft(building,craft_id)
        name_result = self._get_item_reader().get(craft.result).name
        if max_count_once == 1:
            count = 1
        else:
            count = int(ceil(float(count) / craft.resultCount))
        if craft.result == u'@BRAINS_8': count = count/7
        count = min(count,self.craft_available(building,craft_id))
        if count <= 0: return (0, name_result)
        saved_count = count
        #sending
        if craft.delayTime > 0:
            action_count = min(count,len(building_obj))
            for build in building_obj:
                craft_event = {"itemId":craft_id,"objId":build.id,"action":"craft","type":"item"}
                if count > 0:
                    count -= 1
                    self.send([craft_event])
                    # ставим таймер кручения
                    if not hasattr(build,'nextPlayTimes'):
                        d = dict2obj({craft.craftId:str(craft.delayTime * 1000)}, 'nextPlayTimes')
                        setattr(build,'nextPlayTimes',d)
                    else:
                        setattr(build.nextPlayTimes,craft.craftId,str(craft.delayTime * 1000))
                else:
                    break
        else:
            action_count = count
            craft_event = {"itemId":craft_id,"objId":building_obj[0].id,"action":"craft","type":"item"}
            events = [craft_event] * min(count,max_count_once)
            while count > max_count_once:
                self.send(events)
                count -= max_count_once
            if count > 0:
                events = [craft_event] * count
                self.send(events)
        result = action_count * craft.resultCount
        if result:
            logger.info(u'Сделали %d шт. %s'%(result, name_result))
            
        #removing
        for material in craft.materials:
            self.add_crafted_item(material.item, -material.count * action_count)
        #adding
        self.add_crafted_item(craft.result, craft.resultCount * action_count)

        return (result, name_result)

    def craft_to(self,building,craft_id,count,max_count_once=500):
        if self.if_location_pirate(): return 0, ''
        building_obj, craft = self.__find_building(building,craft_id)
        if not building_obj: return (0, '')

        # craft = self.__get_building_craft(building,craft_id)
        name_result = self._get_item_reader().get(craft.result).name
        has = self.craft_item_count(craft.result)
        if has >= count:
            return (has, name_result)
        craft_count = (count - has)/craft.resultCount
        return self.craft_count(building,craft_id,craft_count,max_count_once)
        # return self.craft_count(building,craft_id,craft_count,max_count_once) + has

    def craft(self,options,building,craft_id,max_count_once=500):
        if self.if_location_pirate(): return 0, ''
        building_obj, craft = self.__find_building(building,craft_id)
        if not building_obj: return (0, '')
        
        rezerv = []
        for i in range(1,3):
            rez = options['rezerv_'+str(i)] if 'rezerv_'+str(i) in options.keys() else 0
            rezerv.append(rez)

        # craft = self.__get_building_craft(building,craft_id)
        name_result = self._get_item_reader().get(craft.result).name
        count_go = []
        for i in range(2):
            has = self.craft_item_count(craft.materials[i].item)
            can = int(float((has - rezerv[i])) / craft.materials[i].count)
            # print 'material', i, has
            count_go.append(can)
            if can < 1:
                # print u'сработал лимит', i+1, can
                return (0, name_result)
        has = self.craft_item_count(craft.result)
        if 'max_result' in options.keys():
            max_result = options['max_result']
            can = int(float((max_result - has)) / craft.resultCount)
            if can < 1:
                # print u'сработал предел результата', can
                return (0, name_result)
            count_go.append(can)
        count_go.sort()
        return self.craft_count(building,craft_id,count_go[0]*craft.resultCount,max_count_once)

        # {u'resultCount': 5L, u'name': u'\u041f\u044f\u0442\u044c \u043b\u043e\u043f\u0430\u0442', u'level': 3L, u'materials': [<game_state.game_event.GameMaterial object at 0x04B411B0>, <game_state.game_event.GameMaterial object at 0x04B41C70>], u'result': u'@SHOVEL_EXTRA', u'delayTime': 0L, u'id': u'1'}
        # {u'count': 10L, u'item': u'@S_12', u'notBeUsed': False}
        # {u'count': 2000L, u'item': u'@COINS', u'notBeUsed': False}

        # {u'delayTime': 0L, u'name': u'\u041c\u043e\u0437\u0433\u0438', u'level': 3L, u'materials': [{u'count': 2L, u'item': u'@R_12', u'notBeUsed': False}, {u'count':10L, u'item': u'@CR_31', u'notBeUsed': False}], u'result': u'@BRAINS_1', u'playerStatus': u'@PS_HUMAN', u'resultCount': 1L, u'id': u'1'},
        
        # {u'delayTime': 43200L, u'craftId': u'BABEL_1', u'name': u'\u0422\u0440\u0438 \u0437\u043e\u043c\u0431\u0430\u043a\u0441\u0430', u'level': 9L, u'materials': [{u'count': 1500000L, u'item': u'@COINS', u'notBeUsed': False}, {u'count': 3L, u'item': u'@CR_59', u'notBeUsed': False}], u'result': u'@CASH', u'playerStatus': u'@PS_HUMAN', u'resultCount': 3L, u'id': u'1'}
        pass


    def buy(self,options,max_count_once=100):
        if self.if_location_pirate(): return 0, ''
        if ('location' in options.keys()) and self.location_id() != options['location']: return
        building = options['building']
        name_result = self._get_item_reader().get(building).name
        action_count = 0
        if self.my_level() < self._get_item_reader().get(building).level: return        
        count = self.buy_available(building,options)
        if count < 1: return (action_count, name_result)

        # проверяем сколько уже есть
        if 'max_result' in options.keys():
            has_build = 0
            for item in self._get_game_state().get_state().gameObjects:
                if (item.item == '@' + building):
                    has_build += 1
            print u'Уже есть строений %s: %d шт.' % (name_result,has_build)
            need = options['max_result'] - has_build
            if need < 1: return (action_count, name_result)
            count = min(count, need)

        count = min(count, max_count_once)
        objects = self._get_game().get_free_spaces().newObject(building)
        if len(objects) == 0:
            print u'Нет пустого места для покупки', name_result
            return (action_count, name_result)  # Нет пустого места
        # print u'Есть место под', len(objects), u'шт.'
        for obj in objects:
            if count <= 0: break
            count -= 1
            action_count += 1
            buy_event = {"x":obj.x,"action":"buy","y":obj.y,"itemId":building,"type":"item","objId":obj.id}
            self.send([buy_event])
            #removing
            self.buy_removing_material(building,options)
            #adding
            self.add_crafted_item('@XP', self._get_item_reader().get(building).xp)
            self._get_game_state().get_state().gameObjects.append(obj)
            self._get_game_location().get_game_objects().append(obj)
            logger.info(u'Покупаем и ставим 1 шт. %s'%(name_result))
        return (action_count, name_result)

    def buy_removing_material(self,building,options):
        buyCoins = self._get_item_reader().get(building).buyCoins
        buyCash = self._get_item_reader().get(building).buyCash
        if buyCoins:
            self.add_crafted_item('@COINS', -buyCoins)
        if buyCash:
            self.add_crafted_item('@CASH', -buyCash)
        if hasattr(self._get_item_reader().get(building), 'buyItem'):
            buyItem = self._get_item_reader().get(building).buyItem
            if hasattr(buyItem, 'count') and buyItem.count:
                self.add_crafted_item(buyItem.item, -buyItem.count)

    def buy_available(self,building,options):
        #проверка сколько можно макс сделать
        buyCoins = self._get_item_reader().get(building).buyCoins
        buyCash = self._get_item_reader().get(building).buyCash
        count = []
        if buyCoins:
            if 'rezerv_1' in options.keys():
                count.append((self.money() - options['rezerv_1']) / buyCoins)
            else:
                count.append(self.money() / buyCoins)
        if buyCash:
            if 'rezerv_1' in options.keys():
                count.append((self.xp() - options['rezerv_1']) / buyCash)
            else:
                count.append(self.xp() / buyCash)
        if hasattr(self._get_item_reader().get(building), 'buyItem'):
            buyItem = self._get_item_reader().get(building).buyItem
            if hasattr(buyItem, 'count') and buyItem.count:
                has = self._get_game_state().count_in_storage(buyItem.item)
                if 'rezerv_1' in options.keys():
                    count.append((has - options['rezerv_1']) / buyItem.count)
                else:
                    count.append(has / buyItem.count)
        count.sort()
        if count[0] < 1:
            print u'Не хватает ресурсов чтобы сделать', self._get_item_reader().get(options['building']).name
        else:
            print u'Ресурсов хватает чтобы сделать', count[0]
        return count[0]

    def check_clock_works(self, par):
        working_hours = par.get('working_hours',{})
        if not working_hours: return True
        working_hours_from = working_hours.get('from','0:0').split(':')
        if len(working_hours_from) < 2: working_hours_from = ['0','0']
        working_hours_to = working_hours.get('to','23:59').split(':')
        if len(working_hours_to) < 2: working_hours_to = ['23','59']
        from_h = int(working_hours_from[0])
        from_m = int(working_hours_from[1])
        to_h = int(working_hours_to[0])
        to_m = int(working_hours_to[1])
        th = int(time.strftime('%H', time.localtime(time.time())))
        tm = int(time.strftime('%M', time.localtime(time.time())))
        if ((th > from_h) or (th == from_h and tm >= from_m)) and\
                ((th < to_h) or (th == to_h and tm < to_m)):
            return True
        return False

    # работа с pirate ini
    def init_ini(self, filename):
        self.filename = filename
        if not os.path.isfile(filename):
            self.new_ini()
        self.parser = ConfigParser.RawConfigParser()
        self.read_ini()

    def new_ini(self):
        with open(self.filename, 'w') as f:
            text = u'[global_info]\nall_pirates = 0\n\n'
            f.write(text.encode('UTF-8'))

    def read_ini(self):
        self.parser.read(self.filename)

    def set_name_section(self,section):
        self.sect = section
        if not self.parser.has_section(section):
            self.add_section(section)

    def work_section(self):
        return self.sect

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

    def set_param_dict(self, dict):
        rewrite = False
        for key in dict.keys():
            dat = self.get_param(key)
            if (not dat is None) and (dat == str(dict[key])): continue
            rewrite = True
            self.parser.set(self.sect, key, dict[key])
        return rewrite

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

    def print_ini(self):
        for sec in self.get_sections():
            self.set_name_section(sec)
            print sec
            print self.get_allparam()

    def write_gameSTATE(self, gameSTATE):
        curuser = str(self._get_game_state().get_curuser())
        # open('statistics\\'+curuser+'\gameSTATE.txt', 'w').write(str(obj2dict(gameSTATE)))
        gameSTATE = obj2dict(gameSTATE)
        self.target = open('statistics\\'+curuser+'\gameSTATE_R.txt', 'w')
        print '---All len---', len(gameSTATE.keys())
        self.target.write('---All len---'+str(len(gameSTATE.keys()))+"\n"+"\n")
        self.target.close()
        self.target = open('statistics\\'+curuser+'\gameSTATE_R.txt', 'a')
        self.__print_data_level(gameSTATE, 0, False)
        self.target.write(u'\n'+u'================================================================'+u'\n'+u'\n')
        self.target.close()
        # raw_input('-------------   END   ---------------')
        pass
        
    def __print_data_level(self, data, num=0, pr=False):
        if type(data) == dict:
            for el in data.keys():
                if type(data[el]) == int or type(data[el]) == float or type(data[el]) == long or type(data[el]) == str or type(data[el]) == bool:
                    if pr: print ' '*num*8+str(el).ljust(12, " ")+' = '+str(data[el])
                    text = ' '*num*8 + str(el).ljust(12, " ") + ' = ' + str(data[el]) +"\n"
                    self.target.write(text.encode("utf-8"))
                elif type(data[el]) == unicode:
                    if pr: print ' '*num*8+str(el).ljust(12, " ")+' = '+data[el]
                    text = ' '*num*8+str(el).ljust(12, " ")+' = '+data[el]+"\n"
                    self.target.write(text.encode("utf-8"))
                elif type(data[el]) == dict or type(data[el]) == list:
                    space = ' '*(21-len(str(el)))
                    if pr: print ' '*num*8+str(str(el)+space+' len '+str(len(data[el]))).ljust(31, " ")+str(type(data[el]))
                    text = ' '*num*8+str(str(el)+space+' len '+str(len(data[el]))).ljust(31, " ")+str(type(data[el])) +"\n"
                    self.target.write(text.encode("utf-8"))
                    self.__print_data_level(data[el], num+1, pr)
                else:
                    if pr: print 'unknown type'
                    text = 'unknown type' +"\n"
                    self.target.write(text.encode("utf-8"))
        elif type(data) == list:
            for el in data:
                if type(el) == int or type(el) == float or type(el) == long or type(el) == str or type(el) == bool:
                    if pr: print ' '*num*8+str(el)
                    text = ' '*num*8+str(el) +"\n"
                    self.target.write(text.encode("utf-8"))
                elif type(el) == unicode:
                    if pr: print ' '*num*8+str(el)
                    text = ' '*num*8+str(el) +"\n"
                    self.target.write(text.encode("utf-8"))
                elif type(el) == dict:
                    space = ' '*(21-len(el))
                    if pr: print ' '*num*8+str(type(el))+' len '+str(len(el))
                    text = ' '*num*8+str(type(el))+' len '+str(len(el)) +"\n"
                    self.target.write(text.encode("utf-8"))
                    self.__print_data_level(el, num+1, pr)
                elif type(el) == list:
                    space = ' '*(21-len(el))
                    if pr: print ' '*num*8+str(type(el))+' len '+str(len(el))
                    text = ' '*num*8+str(type(el))+' len '+str(len(el)) +"\n"
                    self.target.write(text.encode("utf-8"))
                    self.__print_data_level(el, num+1, pr)
                else:
                    if pr: print 'unknown type'
                    text = 'unknown type' +"\n"
                    self.target.write(text.encode("utf-8"))
        else:
            if pr: print 'unknown type 0'
            text = 'unknown type 0' +"\n"
            self.target.write(text.encode("utf-8"))

