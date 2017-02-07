# coding=utf-8
import logging
import time
from datetime import datetime, date, timedelta, time as dt_time
import ConfigParser
import random  as  random_number
# import os.path
import os
import glob
import re
from game_state.game_event import dict2obj, obj2dict
from game_state.base import BaseActor
from ctypes import windll

stdout_handle = windll.kernel32.GetStdHandle(-11)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
logger = logging.getLogger(__name__)


class AutoPirat(BaseActor):
    def perform_action(self):
        par = self.mega().auto_pirate_options()
        fill_box = par.get('fill_box',{})
        gop_company = par.get('gop_company',[])
        min_caravel_stuk = par.get('min_caravel_stuk',1)
        sostav = par.get('sostav')
        nahlebniki = par.get('nahlebniki',[])
        isle_go = par.get('isle_go','main')
        ignore_alien_stop = par.get('ignore_alien_stop',False)

        #=====================================================================

        if not hasattr(self._get_game_state().get_state(),'pirate'): return
        if self.location_id() != isle_go: return

        self.curuser = self._get_game_state().get_curuser()
        self.myid = self._get_game_state().get_my_id()

        dir = 'statistics\\_avto_pirate_' + str(sostav)
        if not os.path.isdir(dir): os.makedirs(dir)
        name_stop = dir + '\\STOP_' + self.curuser + '.txt'
        name_main = dir + '\\main_' + self.curuser + '.txt'
        name_info = dir + '\\info_' + self.curuser + '.ini'
        self.rewrite = False

        if str(self.myid) not in gop_company: return
        building = 'B_PIRATE_CARAVEL_2'
        build_reader = self._get_item_reader().get(building)
        if not hasattr(self._get_game_state(), 'ap_state'): self._get_game_state().ap_state = {}
        self.check_storage_pirate_box()
        has_build = self.check_ship(building,build_reader)
        self._get_game_state().ap_state['captain'] = False
        self._get_game_state().ap_state['go'] = False
        self._get_game_state().ap_state['wealth_roll'] = False
        self.init_ini(name_info)
        self.set_gop_count(gop_company)
        self.add_user_isle_main(name_main)

        if self._get_game_state().ap_state['ship_levelup'] < min_caravel_stuk:
            self.cprint(u'13Недостаточно достроенных каравелл')
            self.save_ap_state()
            return

        if not self.set_pirate_box():
            self.cprint(u'13Нет сундука или места под выставление')
            self.remove_user_isle_main(name_main)
            self.save_ap_state()
            return

        self.fill_pirate_box(fill_box)  # наполняем сундук инструментом

        while True:
            if self._get_game_state().get_state().pirate.state == 'AWAY':
                self.remove_user_isle_main(name_main)
                self.otchalivaem(0)
                self.save_ap_state()
                return
            elif not has_build:
                self.cprint(u'13Нет команд в кораблях, ждём...')
                self.add_alert(name_stop)
                break
            else:
                if self.get_alert(dir, name_stop, ignore_alien_stop):
                    if self.all_isle_main(gop_company, dir):
                        if self.get_alert_user(name_stop):
                            self.remove_alert(dir, name_stop)
                            break
                        else: break
                    else:
                        self.save_ap_state()
                        return
                else:  # стопа нет, отплываем
                    # self.wait_go(gop_company.index(str(self.myid)))
                    self.remove_user_isle_main(name_main)
                    self.otchalivaem(has_build[0].id)
                    self.save_ap_state()
                    return
        if self.all_isle_main(gop_company, dir):
            # настукиваем друзьям
            self.knock_in_ships(isle_go, gop_company + nahlebniki)
        self.save_ap_state()  # сохраняем ap_state
        return

    def clear_pirate_box(self):
        if len(self._get_game_state().get_state().pirate.instruments) == 0: return
        for object in self._get_game_state().get_state().gameObjects:
            if object.item == '@PIRATE_BOX' or object.item == '@PIRATE_BOX_2':
                clear_events = []
                for instr in self._get_game_state().get_state().pirate.instruments:
                    if not instr.count: continue
                    event = {
                            "type":"item",
                            "action":"moveInstrumentFromBox",
                            "count":instr.count,
                            "itemId":instr.item.lstrip('@')
                            }
                    clear_events.append(event)
                    self._get_game_state().add_from_storage(instr.item,instr.count)
                    instr.count = 0
                if clear_events:
                    self.send(clear_events)
                    logger.info(u'Убрали инструмент из сундука')
                break

    def fill_pirate_box(self,fill_box):
        for instr in self._get_game_state().get_state().pirate.instruments:
            if instr.count > 0: break
        else:
            if len(self._get_game_state().get_state().pirate.instruments) > 0: return
            for object in self._get_game_state().get_state().gameObjects:
                if object.item == '@PIRATE_BOX' or object.item == '@PIRATE_BOX_2':
                    fill_events = []
                    for instrument in fill_box.keys():
                        if fill_box[instrument] > 0 and self.has_in_storage(instrument,fill_box[instrument]):
                            event = {"type":"item","action":"moveInstrumentToBox","count":fill_box[instrument],"itemId":instrument}
                            fill_events.append(event)
                            self._get_game_state().get_state().pirate.instruments.append(dict2obj({u'count':fill_box[instrument], u'item': u'@'+instrument}))
                            self._get_game_state().add_from_storage(u'@'+instrument,-fill_box[instrument])
                    if fill_events:
                        self.send(fill_events)
                        logger.info(u'Наполнили сундук инструментом')
                    break

    def set_pirate_box(self):
        if self._get_game_state().get_state().pirate.state == 'PIRATE': return True
        if self._get_game_state().get_state().pirate.state == 'AWAY': return True
        if self._get_game_state().get_state().pirate.state != 'CITIZEN': return False
        if not self.check_storage_pirate_box(): return False

        objects = self._get_game().get_free_spaces().newObject(self._box)
        if len(objects) == 0:
            print u'Нет пустого места'
            return False
        maxY = -1
        for obj in objects:
            if obj.y > maxY:
                maxY = obj.y
                obj_maxY = obj

        obj_maxY.id = self.new_id()
        set_event = {
                "x":obj_maxY.x,
                "y":obj_maxY.y,
                "action":"placeFromStorage",
                "type":"item",
                "itemId":self._box.lstrip('@'),
                "objId":obj_maxY.id
                }
        self.send([set_event])
        self._get_game_state().get_state().gameObjects.append(obj_maxY)
        self._get_game_location().get_game_objects().append(obj_maxY)
        self._get_game_state().add_from_storageObjects(self._box, -1)
        self._get_game_state().get_state().pirate.state = 'PIRATE'
        self._get_game_state().ap_state['pirate_box'] = 'isle'
        logger.info(u'Выставили пиратский сундук')
        return True

    def check_storage_pirate_box(self):
        if self._get_game_state().get_state().pirate.state == 'PIRATE' or\
                self._get_game_state().get_state().pirate.state == 'AWAY':
            self._get_game_state().ap_state['pirate_box'] = 'isle'
            return False
        pirateBox = ['@PIRATE_BOX','@PIRATE_BOX_2']
        for box in pirateBox:
            if self._get_game_state().count_in_storageObjects(box) > 0:
                self._get_game_state().ap_state['pirate_box'] = 'storage'
                self._box = box
                return True
        self._get_game_state().ap_state['pirate_box'] = 'none'
        return False

    def check_ship(self,building,build_reader):
        ap_state = self._get_game_state().ap_state
        ap_state['ship'] = 0
        ap_state['ship_levelup'] = 0
        ap_state['ship_team'] = 0
        has_build = []
        for object in self._get_game_state().get_state().gameObjects:
            if (object.item == '@'+building):
                ap_state['ship'] += 1
                if object.level == len(build_reader.upgrades):
                    ap_state['ship_levelup'] += 1
                    if len(object.team) == build_reader.placesCount:
                        has_build.append(object)
                        ap_state['ship_team'] += 1
        return has_build

    def otchalivaem(self,id):
        # raw_input('-------------   END   ---------------')
        fol_cur = 'statistics\\' + self.curuser # короткое имя папки юзера
        if os.path.isfile(fol_cur + '\\stone_well.txt'):
            os.remove(fol_cur + '\\stone_well.txt')
        if os.path.isfile(fol_cur + '\\sw_run.txt'):
            os.remove(fol_cur + '\\sw_run.txt')
        if os.path.isfile(fol_cur + '\\chop_broot_id.txt'):
            os.remove(fol_cur + '\\sw_run.txt')
        if os.path.isfile(fol_cur + '\\brut_off.txt'):
            os.remove(fol_cur + '\\brut_off.txt')
        if os.path.isfile(fol_cur + '\\end_did.txt'):
            os.remove(fol_cur + '\\end_did.txt')
        if hasattr(self._get_game_state(), 'wealth_roll'):
            delattr(self._get_game_state(), 'wealth_roll')
        if hasattr(self._get_game_state(), 'brut'):
            delattr(self._get_game_state(), 'brut')

        if self._get_game_state().get_state().pirate.state == 'PIRATE':
            self._get_game_state().ap_state['captain'] = True
            event = {"type":"item","objId":id,"action":"sail"}
            self.cprint(u'14Отплываем капитаном!')
            cap = True
        else:
            self.clear_pirate_box()
            event = {"type":"pirate","action":"sail"}
            self.cprint(u'14Отплываем матросом!')
            cap = False
        self._get_game_state().set_game_loc_was = False
        self.send([event])
        self._get_game().handle_all_events()
        print u'Ждём загрузки острова',
        while not self._get_game_state().set_game_loc_was:
            print u'\b.',
            self._get_events_sender().send_game_events([])
            self._get_game().handle_all_events()
            if cap and self._get_game_state().get_state().pirate.state == 'AWAY':
                cap = False
                print ''
                self.cprint(u'14Планы поменялись... Отплываем матросом!')
                print u'Ждём загрузки острова',
                self.clear_pirate_box()
                self._get_game_state().ap_state['captain'] = False
                event = {"type":"pirate","action":"sail"}
                self.send([event])
                self._get_game().handle_all_events()
            time.sleep(0.2)
        print u'\b.'
        event = {"type":"action","action":"getMissions"}
        self.send([event])
        self._get_game().handle_all_events()
        self._get_game_state().get_state().pirate.state = 'AWAY'
        self._get_game_state().ap_state['go'] = True
        print u'Уплыли'
        self.__save_log()
        time.sleep(5)
        self._get_game().handle_all_events()

    def __save_log(self):
        if self._get_game_state().ap_state['captain']:
            cap = u'капитаном'
        else:
            cap = u'матросом'
        # _date = datetime.datetime.today().strftime(' %Y.%m.%d %H:%M:%S ')
        _date = time.strftime(' %Y.%m.%d %H:%M:%S ', time.localtime(time.time()))
        text = str(self.curuser) + u' ' + _date + u' отплыли ' + cap + u'\n'
        sostav = self.mega().auto_pirate_options()['sostav']
        # with open('statistics\\otplitiya.txt', 'a') as f: #'statistics\\'+self.curuser+'\otplitiya.txt'
        with open('statistics\\_avto_pirate_' + str(sostav) + '\\otplitiya.txt', 'a') as f: 
            f.write(text.encode('utf-8'))
        self.write_log(u'Отплыли ' + cap + u' на пиратский')

    def wait_go(self, ind):
        print(u'Ждём очереди отплытия, осталось секунд '),
        for i in range(ind*5, 0, -5):
            print str(i) + '...',
            time.sleep(5)
            self._get_game().handle_all_events()
        print 0

    # работа с флагами-файлами
    def all_isle_main(self, gop_company, dir):
        count_main = len(glob.glob(dir + '\\main_*.txt'))
        return (count_main == len(gop_company))

    def add_user_isle_main(self, name_main):
        if not os.path.isfile(name_main):
            with open(name_main, 'w') as f:
                f.write(' ')

    def remove_user_isle_main(self, name_main):
        if os.path.isfile(name_main):
            os.remove(name_main)

    def get_alert(self, dir, name_stop, ignore_alien_stop):
        if ignore_alien_stop:
            return os.path.isfile(name_stop)
        if glob.glob(dir + '\\STOP_*.txt'):
            return True
        return False

    def get_alert_user(self, name_stop):
        if os.path.isfile(name_stop):
            return True
        return False

    def add_alert(self, name_stop):
        if not os.path.isfile(name_stop):
            with open(name_stop, 'w') as f:
                f.write(' ')

    def remove_alert(self, dir, name_stop):
        if len(glob.glob(dir + '\\STOP_*.txt')) == 1:
            pause = 180
            sec = time.time()
            while pause:
                m = pause/60
                s = int(pause - m*60)
                self.cprint2(u"9\rДо снятия 'STOP' осталось ^15_%d:%d  " % (m,s))
                if (time.time() - sec) > 27:
                    self.send([])
                    sec = time.time()
                self._get_game().handle_all_events()
                while self._get_game().ping:
                    self._get_game().handle_all_events()
                time.sleep(1)
                pause -= 1
            self.cprint2(u"9\rДо снятия 'STOP' осталось ^15_%d:%d  " % (0,0))
            print
            if len(glob.glob(dir + '\\STOP_*.txt')) == 1:
                self.cprint(u'14Мы последние. Снимаем STOP!')
                logger.info(u'Сходим последний раз перед отплытием обстучать корабли')
            else:
                self.cprint(u'13Пока мы ждали стопорнул кто-то другой')
        if os.path.isfile(name_stop):
            os.remove(name_stop)

    # работа с параметрами в файле
    def save_ap_state(self):
        self._get_game_state().ap_state['pirate_state'] = self._get_game_state().get_state().pirate.state
        self._get_game_state().ap_state['id'] = self._get_game_state().get_my_id()
        self.set_name_section(self.curuser)
        if self.set_param_dict(self._get_game_state().ap_state):
            self.rewrite = True
        # print self.get_allparam()
        if self.rewrite:
            self.save()

    def set_gop_count(self, gop_company):
        self.set_name_section('global_info')
        dat = self.get_param('all_pirates')
        if dat and (int(eval(dat)) == len(gop_company)): return
        self.set_param('all_pirates',len(gop_company))
        self.rewrite = True


    # pirate_frends
    # что делаем
    def opt(self, option):
        options = self.mega().friends_pirat()['что делаем']
        return option in options

    def knock_in_ships(self, isle_go, friends):
        if self.if_location_pirate(): return
        if not friends: return
        logger.info(u'Идём по друзьям стучать в корабли')
        self.write_log(u'Идём по друзьям стучать в корабли')

        # настройки
        par = self.mega().friends_pirat()['параметры']
        shovels = par.get('shovels',50)
        max_monster = par.get('max_monster',99)
        con_user = par.get('con_user',50)
        color_print = par.get('color_print',False)
        circle_dig = par.get('circle_dig',False)
        only_first = par.get('only_first',False)
        sort_green = par.get('sort_green',False)

        # что копаем:
        favdecors = []
        favdecors_list = self.mega().friends_pirat()['что копаем']
        for f in favdecors_list:
            favdecors.extend(f)

        # author Vint, Loconaft, and other
        #----------------------------------------------------------------------------------------------------

        # if (not circle_dig) and hasattr(self._get_game_state(), 'all_visited') and self._get_game_state().all_visited:
            # logger.info('-------------   END   ---------------')
            # return # всех друзей прошли уже

        isle = 'main'

        curuser = str(self._get_game_state().get_curuser())
        self.myid = self._get_game_state().get_my_id()
        
        if str(self.myid) in friends:
            friends.remove(str(self.myid))

        self.antilag(1)  # антилаг загрузки, сек
        if hasattr(self._get_game_state(), 'playersInfo'):
            players_info = self._get_game_state().playersInfo
            len_playersInfo = len(players_info)
            # print u'Начальная длина playersInfo %d' % len_playersInfo
        else:
            players_info = []
            len_playersInfo = len(players_info)
            if color_print:
                self.cprint(u'12Инфа о друзьях не получена.')
            else:
                print u'Инфа о друзьях не получена.'

        if not os.path.isdir('statistics\\'+curuser+'\copatel'):
            os.makedirs('statistics\\'+curuser+'\copatel')
        fol_cop = 'statistics\\'+curuser+'\\copatel'

        userdig = 0
        global_lopat = 0
        self.air_num = 0
        cakelimit = False
        self._events = []
        state_min = [int(time.time()/60)]
        self.read_shovel_extra()
        self.statistics_start(color_print)

        # основной цикл обхода друзей
        for n_v in range(len(friends)):
            fid = friends[n_v]
            if hasattr(self._get_game_state(), 'playersInfo') and len_playersInfo != len(self._get_game_state().playersInfo):
                players_info = self._get_game_state().playersInfo
                add_playersInfo = len(players_info) - len_playersInfo
                len_playersInfo = len(players_info)
                if color_print:
                    self.cprint(u'4Произошло обновление players_info')
                else: logger.info(u'Произошло обновление players_info')
                print u'Длина playersInfo изменилась на %d' % add_playersInfo

            # консоль
            self.console_log(curuser,userdig,global_lopat)

            # проверяем зелёный ли друг
            if sort_green and hasattr(self._get_game_state(), 'playersInfo'):
                load = False
                for info in players_info:
                    if str(info.id) == str(fid):
                        load = True
                        break
                if load and not info.liteGameState.haveTreasure:
                    #print u'У друга всё выкопано!'
                    continue

            # проверяем забанен ли друг
            if sort_green and hasattr(self._get_game_state(), 'playersInfo'):
                load = False
                for info in players_info:
                    if str(info.id) == str(fid):
                        load = True
                        break
                if load and info.banned:
                    #print u'Друг в бане!'
                    continue

            name_user = self.name_user(fid)

            num_u = str(fid).ljust(20, " ")
            sp_n = u' '*(14-len(name_user))
            print ' '
            if color_print:
                self.cprint(u'9##### Идем к другу^14_'+num_u+u'^3'+name_user+sp_n+u'^15_%d/%d^9на^3_%s^9#####'%((n_v+1), len(friends), isle))
            else:
                logger.info(u'##### Идем к другу '+num_u+u' '+name_user+sp_n+u'%d/%d на %s #####'%((n_v+1), len(friends), isle))
            self._get_game_state().planeAvailable = True
            self.load_friend_isle(fid, isle)
            
            UserIsAway = self._get_game_state().get_state().isAway
            if UserIsAway: # True
                print u' ',
                self.cprint(u'71Друг давно не был в игре!!!')
           
            self.actions_list = {} # эвент хранилище
            self.actions_info = {} # эвент описания
            guardGrave = 0         # наличие сторожа
            objssvl = {}           # что копать
            cone_user = con_user
            countnyt = 0
            haveRemoteFertilizeFruit = True
            haveRemoteValentineTower = True
            
            if self._get_game_state().get_state().haveTreasure:
                alldigged = False
            else:
                alldigged = True
                logger.info(u'Здесь всё выкопано...')
                


            for object in self._get_game_location().get_game_objects():

                if object.type == 'guardGrave':
                    logger.info(u'------------ Сторож !!! ------------')
                    guardGrave = 1

                # разбивать тайники
                if object.type == 'friendTransformObject':
                    if self.opt('split_caches'):
                        if object.transformed:continue
                        name = self._get_item_reader().get(object.item).name
                        eventtrans = {"action":"remoteFriendTransform","type":"item","objId":object.id}
                        self._get_events_sender().send_game_events([eventtrans])
                        self.cprint(u'5Разбил %s' % name.upper())
                    continue


                # Стучим в Разные постройки
                if object.type == 'thanksgivingTable':
                    if self.opt('thanksgiving'):
                        day_stuk = self._get_game_state().get_state().remoteThanksgiving
                        reader_thanks = self._get_item_reader().get(object.item)
                        if (not self._get_game_state().planeAvailable) or len(day_stuk) >= 100 or object.usedPlatesCount >= reader_thanks.platesCount: continue
                        if hasattr(reader_thanks, 'endSellingDate') and int(reader_thanks.endSellingDate)/1000 < time.time(): continue
                        for days in day_stuk:
                            if str(fid) == str(days.user):
                                if color_print:
                                    self.cprint(u'4Сегодня мы уже стукнули у этого друга')
                                else:
                                    logger.info(u'Сегодня мы уже стукнули у этого друга')
                                self._get_game_state().planeAvailable = False
                                break
                        else:
                            readerGifts = self._get_item_reader().get(reader_thanks.gifts[0])
                            eventtrans = {
                                        "itemId": readerGifts.id, 
                                        "action": "remoteThanksgiving",
                                        "type": "item", 
                                        "objId": object.id
                                        }
                            self._get_events_sender().send_game_events([eventtrans])
                            apend_frend = {u'count': 0L, u'date': u'-19849562', u'user': str(fid)}
                            self._get_game_state().get_state().remoteThanksgiving.append(dict2obj(apend_frend))
                            self.cprint(u'5%s в %s' % (readerGifts.name,reader_thanks.name))
                            self._get_game_state().planeAvailable = False
                            self.air_num += 1
                    continue

                # Стучим в пиратский сундук
                if object.type == 'pirateBox':
                    if self.opt('pirateCheckin') and self._get_game_state().get_state().pirate.state == 'CITIZEN':
                        event = {"objId":object.id,"type":"item","action":"remotePirateCheckin"}
                        self._get_events_sender().send_game_events([event])
                        if color_print:
                            self.cprint(u'5Застукал Пиратский сундук')
                        else: logger.info(u'Застукал Пиратский сундук')
                    continue

                # Стучим в лодки
                if object.type == 'pirateShip':
                    if (self.opt('pirateBoats') or self.opt('pirateSchooner') or self.opt('pirateCaravel')) and\
                            (self._get_game_state().get_state().pirate.state == 'PIRATE') and object.level == 2:
                        if self.opt('pirateBoats') and object.item == u'@B_PIRATE_BOAT_2' and len(object.team) < 5:
                            if not str(self.myid) in str(object.team):
                                self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","action":"remotePirateJoinTeam"}])
                                if color_print:
                                    self.cprint(u'5Попросился в команду на Пиратскую Лодку!')
                                else: logger.info(u'Попросился в команду на Пиратскую Лодку!')
                            else:
                                if color_print:
                                    self.cprint(u'4Ты уже в команде на Пиратской Лодке')
                                else: logger.info(u'Ты уже в команде на Пиратской Лодке')
                        if self.opt('pirateSchooner') and object.item == u'@B_PIRATE_SCHOONER_2' and len(object.team) < 5:
                            if not str(self.myid) in str(object.team):
                                self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","action":"remotePirateJoinTeam"}])
                                if color_print:
                                    self.cprint(u'5Попросился в команду на Пиратскую Шхуну!')
                                else: logger.info(u'Попросился в команду на Пиратскую Шхуну!')
                            else:
                                if color_print:
                                    self.cprint(u'4Ты уже в команде на Пиратской Шхуне')
                                else: logger.info(u'Ты уже в команде на Пиратской Шхуне')
                        if self.opt('pirateCaravel') and object.item == u'@B_PIRATE_CARAVEL_2' and len(object.team) < 7:
                            if not str(self.myid) in str(object.team):
                                self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","action":"remotePirateJoinTeam"}])
                                if color_print:
                                    self.cprint(u'5Попросился в команду на Пиратскую Каравеллу!')
                                else: logger.info(u'Попросился в команду на Пиратскую Каравеллу!')
                            else:
                                if color_print:
                                    self.cprint(u'4Ты уже в команде на Пиратской Каравелле')
                                else: logger.info(u'Ты уже в команде на Пиратской Каравелле')
                    continue

                # Удобряем фруктовые деревья
                if object.type == "fruitTree":
                    if self.opt('fruitTree') and haveRemoteFertilizeFruit == True and (object.jobFinishTime > 0) and (len(self._get_game_state().get_state().remoteFertilizeFruitTree) < 20): # self._get_game_state().get_state().haveRemoteFertilizeFruit == True
                        #treefruit = ['FT_APPLE','FT_CHERRY','FT_MANDARINE','FT_LEMON','FT_SKULL','FT_EYE']
                        if self.fid_in_list(fid, self._get_game_state().get_state().remoteFertilizeFruitTree):
                            if color_print:
                                self.cprint(u'4Сегодня мы уже здесь полили')
                            else: logger.info(u'Сегодня мы уже здесь полили')
                            haveRemoteFertilizeFruit = False
                            continue
                        if color_print:
                            self.cprint(u'5Удобряем дерево!')
                        else: logger.info(u'Удобряем дерево!')
                        self._get_events_sender().send_game_events([{"action":"remoteFertilizeFruitTree","type":"item"}])
                        self._get_game_state().get_state().remoteFertilizeFruitTree.append({u'count': '0L', u'date': u'-2435527', u'user':fid})
                        haveRemoteFertilizeFruit = False
                    continue

                # Вскрываем сундук
                if object.type == 'pickup':
                    if self.opt('box'):
                        #open('sunduki.txt', 'a').write(str(obj2dict(object)) + "\n")
                        self.add_action('pickupbox', {"action":"pick","type":"item","objId":object.id})
                    continue

                # Ёлки
                if object.type == 'newYearTree' and 'B_SPRUCE_' in object.item:
                    if cakelimit: continue 
                    if self.opt('conifer') and countnyt < cone_user:
                        rem_ = self._get_game_state().get_state().remoteNewYear
                        if len(rem_) < 150:
                            if object.level < 2:
                                print u'Ёлка недостроена...'
                                continue
                            if len(rem_) > 0:
                                countmyg = 0
                                if self.myid_in_list(object, rem_, fid):
                                    if color_print:
                                        self.cprint(u'4Сегодня мы уже стукнули в эту ёлку')
                                    else: logger.info(u'Сегодня мы уже стукнули в эту ёлку')
                                    continue
                            usrs = len(object.users)
                            #Ёлки разной ёмкости.
                            if object.item == u'@B_SPRUCE_SMOLL' and usrs > 2: continue
                            if object.item == u'@B_SPRUCE_MIDDLE' and usrs > 5: continue
                            if object.item == u'@B_SPRUCE_BIG' and usrs > 14: continue

                            print u'Ложим пряник'
                            self.add_action('newyeartree', {"itemId":"CAKE_PACK_FREE1","action":"remoteNewYear","type":"item","objId":object.id})
                            self._get_game_state().get_state().remoteNewYear.append({u'treeId':object.id, u'user':fid})
                            countnyt += 1
                        else:
                            cakelimit = True
                            if False: # color_print:
                                self.cprint(u'8Исчерпан лимит на пряники...')
                            else: print u'Исчерпан лимит на пряники...'
                    continue

                # Мишка
                if object.type == 'monsterPit':
                    l = self._get_game_state().get_state().remoteMonsterPit
                    if self.opt('monster') and len(l) < 100:
                        if object.state == 'DIGGING':
                            mon_depth = sum(+int(i.depth )for i in object.users) # Глубина закопки мишки
                            if mon_depth > 99:
                                #print 'mon_depth', mon_depth, 'len(object.users)', len(object.users)
                                logger.info(u'За баксы не закапываем. Глубина %d м.'% mon_depth)
                                continue
                            if mon_depth > max_monster:
                                logger.info(u'Мишка закопан больше положенного. Глубина %d м.'% mon_depth)
                                continue
                            # Проверка на повторное закапывание в один день
                            if len(l) > 0:
                                if self.fid_in_list(fid, l):
                                    if color_print:
                                        self.cprint(u'4Сегодня мы уже зарывали этого мишку...')
                                    else: logger.info(u'Сегодня мы уже зарывали этого мишку...')
                                    continue
                            if color_print:
                                self.add_action('monster', {"itemId":"MONSTER_PIT_1_INSTRUMENT_PACK_DEFAULT","action":"remoteMonsterPit","type":"item","objId":object.id})
                                self.cprint(u'5Закапываем чудика. Закопало^15_%d^5человек на глубину ^15_%s ^5_м.'%(len(object.users), mon_depth))
                            else:
                                self.add_action('monster', {"itemId":"MONSTER_PIT_1_INSTRUMENT_PACK_DEFAULT","action":"remoteMonsterPit","type":"item","objId":object.id}, (u'Закапываем чудика. Закопало %d человек на глубину %s м.'%(len(object.users), mon_depth)))
                            #open('monster.txt', 'a').write(str(obj2dict(object))+"\n")
                            self._get_game_state().get_state().remoteMonsterPit.append({u'count': '0L', u'date': u'-5130168', u'user':fid})
                        else:
                            logger.info(u'Мишку нельзя закопать')
                    continue

                # Дерево страсти & сад бабочек
                if object.type == 'valentineTower':
                    if self.opt('valentine') and object.item == u'@VALENTIINE_TOWER':
                        l = self._get_game_state().get_state().remoteValentineCollect
                        if len(l) >= 300 or object.count <= 0: continue
                        # Проверка на повторный стук в один день
                        if len(l) > 0:
                            if self.fid_in_list(fid, l):
                                if color_print:
                                    self.cprint(u'4Сегодня мы уже стучали этому другу по дереву страсти...')
                                else: logger.info(u'Сегодня мы уже стучали этому другу по дереву страсти...')
                                continue
                        if object.level < 8:
                            if color_print:
                                self.cprint(u'5Стучим в Дерево Страсти!')
                            else:
                                logger.info(u'Стучим в Дерево Страсти!')
                            event_valentine = {"action":"remoteValentineCollect","type":"item","objId":object.id}
                            self._get_events_sender().send_game_events([event_valentine])
                            addUser = {u'count': '0L', u'date': '0L', u'user':str(fid)}
                            self._get_game_state().get_state().remoteValentineCollect.append(addUser)
                        else:
                            logger.info(u'Это дерево страсти уже построено')

                    ##### Стучим в сад бабочек #####
                    elif self.opt('valentine2') and object.item == u'@B_BUTTERFLY_GARDEN':
                        # self.cprint(u'1длина списка стукнутых^12_%d' % (len(l)))
                        # print 'object.level =', object.level
                        if len(l) >= 300 or object.count <= 0: continue  # or object.level > 4
                        for valent in l:
                            if valent.user == str(fid):
                                if color_print:
                                    self.cprint(u'4Сегодня мы уже стучали этому другу в сад...')
                                else: logger.info(u'Сегодня мы уже стучали этому другу в сад...')
                                break
                        else:
                            if color_print:
                                self.cprint(u'5Стукнул в сад бабочек!')
                            else: logger.info(u'Стукнул в сад бабочек!')
                            addUser = {u'count':0, u'date': -300000, u'user': str(fid)}
                            eventValent = {"type":"item","objId":object.id,"action":"remoteValentineCollect","id":None}
                            self._get_events_sender().send_game_events([eventValent])
                            self._get_game_state().get_state().remoteValentineCollect.append(dict2obj(addUser))
                    continue

                # КопАй!!!
                if self.opt('kopatel'):
                    if alldigged:
                        continue
                    if favdecors == None or len(favdecors) == 0:
                        continue
                    else:
                        name = object.item.lstrip('@')
                        if name in objssvl: # Уже есть такая
                            continue
                        # Добавляем в список объект для копания
                        if name in favdecors:
                            if only_first and len(objssvl) > 0: # Уже нашли, что покопать
                                now = objssvl.keys()[0]
                                if favdecors.index(name) < favdecors.index(now): # Индекс этого object меньше, чем того, что уже нашли, => он приоритетнее
                                    objssvl = {} # очистим и ниже добавим
                                else:
                                    continue
                            logger.info(u'####### Найдена декорация %s #######' % name)
                            objssvl[name] = object
            #logger.info(u'Перебор объектов закончен')

            # Покопаем
            if self.opt('kopatel'):
                if len(objssvl) <= 0:
                    if not alldigged:
                        logger.info(u'Нет объектов для копки')
                else:
                    objs = objssvl.values()
                    userdig += 1
                    lopat = 0
                    while True: # цикл копки
                        if lopat >= shovels: break
                        lopat += 1
                        if only_first:objdig = objs[0]
                        else:objdig = random_number.choice(objs)
                        #{"x":61,"y":48,"type":"item","id":46,"action":"remoteDig","objId":48447}
                        self.events_append({"objId":objdig.id,"x":objdig.x,"action":"remoteDig","y":objdig.y,"type":"item"})
                        #print u'Лопата:', lopat
                        if self.events_is_empty: # был слив очереди запросов
                            response = self.response_wait(['alert','pickup'])
                            if response == 'alert':
                                if 'SERVER_REMOTE_TREASURE_ALL_DIGGED' in self._get_game().alerts:
                                    logger.info(u'Всё выкопано!!!')
                                    lopat -= self._get_game().alerts.count('SERVER_REMOTE_TREASURE_ALL_DIGGED')
                                    break
                                if 'SERVER_REMOTE_TREASURE_NO_TRIES' in self._get_game().alerts:
                                    logger.info(u'Закончились лопаты!!!')
                                    lopat = 0
                                    break
                                if 'SERVER_SHOVEL_IS_BAD' in self._get_game().alerts:
                                    logger.info(u'Закончились лопаты!!!')
                                    lopat -= self._get_game().alerts.count('SERVER_SHOVEL_IS_BAD')
                                    break                                    

                            if response == 'pickup':
                                #print u'Можно копать дальше, ибо pickup'
                                pass

                    if lopat:
                        logger.info(u'Использовали "%d" лопат' % lopat)
                        global_lopat += lopat
                    self.events_free()

            # Переберём все экшены
            last_type_file = fol_cop+'\\last_type.txt'
            try:
                last_type = str(open(last_type_file).read())
            except:
                last_type = 'last_type'

            if last_type != 'last_type' and not (last_type in self.actions_list):
                logger.info(u'Типа экшена "%s" нет в очереди - начнём с начала' % last_type)
                last_type = 'last_type'

            for type in self.actions_list:
                #logger.info(u'Начинаем отсылать '+type)
                if last_type != 'last_type': # что-то в прошлый раз произошло
                    if last_type != type:
                        continue
                    else:
                        logger.info(u'Пропустим тип экшена "%s" - он не прошёл в прошлый раз' % last_type)
                        last_type = 'last_type'
                        continue
                open(last_type_file, 'w').write(str(type)) # запишем последний тип экшена и пропустим его, если в прошлый раз на нём произошла фатальная ошибка
                if type in self.actions_info:
                    logger.info(self.actions_info[type]) # выведем справочную инфу

                if type == 'pickupbox' and guardGrave == 1:
                    logger.info(u'Ничего вскрывать не будем, ибо сторож')
                    continue
                logger.info(u'Начинаем отсылать ' + type)

                for a in self.actions_list[type]: # Сам процесс отсылки эвентов
                    self.events_append(a)
                self.events_free()

            open(last_type_file, 'w').write(str('last_type')) # всё прошло удачно - сбросим type
            self._get_game().handle_all_events()

            cur_min = int(time.time()/60)
            if cur_min not in state_min:
                self.statistics(userdig, global_lopat, len(friends), color_print)
                self.pickups_mini(global_lopat)
                state_min.append(cur_min)

        # основной цикл обхода друзей

        self._get_game().handle_all_events()
        print ' '
        self.statistics(userdig, global_lopat, len(friends), color_print)
        self.pickups_mini(global_lopat)
        self.pickups()
        print

        self._get_game_state().all_visited = True
        self.go_home(color_print, isle_go)  # возвращаемся домой

        # идём на следующий круг
        return

    def name_user(self, fid):
        name_user = u'--------------'
        if hasattr(self._get_game_state(), 'friends_names') and self._get_game_state().friends_names.get(str(fid)) and self._get_game_state().friends_names.get(str(fid)) != u'Без имени':
            name_user = u"'" + self._get_game_state().friends_names.get(str(fid)) + u"'"
            #name_user = name_user.replace(u'\u0456', u'i').encode("cp866", "ignore")
        return name_user

    def read_shovel_extra(self):
        for object in self._get_game_state().get_state().storageItems:
            if object.item == '@SHOVEL_EXTRA':
                self.shovel_extra = object.count
                #print 'FIND: ', object.item, '  count = ', self.shovel_extra
                break
        else: self.shovel_extra = 0

    def antilag(self, time_wait):  # антилаг загрузки
        time.sleep(time_wait)
        self._get_game().handle_all_events()

    def statistics_start(self, color_print):
        self.st_rFFT = len(self._get_game_state().get_state().remoteFertilizeFruitTree)
        self.st_rMP = len(self._get_game_state().get_state().remoteMonsterPit)
        self.st_rNY = len(self._get_game_state().get_state().remoteNewYear)
        self.st_rVT = len(self._get_game_state().get_state().remoteValentineCollect)
        self.st_rT = len(self._get_game_state().get_state().remoteThanksgiving)
        # remoteThanksgiving - самолёт
        # remoteTrickTreating - шатёр
        # remoteThanksgiving - корзинка пасхальная
        print ' '
        self.cprint(u'9---  Start  ---')
        if color_print:
            self.cprint (u'9Сегодня полито деревьев:   ^15_%s' % (self.st_rFFT))
            self.cprint (u'9Сегодня закопано медведей: ^15_%s' % (self.st_rMP))
            self.cprint (u'9Застукано ёлок:            ^15_%s' % (self.st_rNY))
            self.cprint (u'9Стукнуто Деревьев Страсти: ^15_%s' % (self.st_rVT))
            self.cprint (u'9Стукнуто корзинок:         ^15_%s' % (self.st_rT))
            #self.cprint (u'9Стукнуто шатров:           ^15_%s' % (self.st_rT))
            #self.cprint (u'9Стукнуто самолётов:        ^15_%s' % (self.st_rT))
            self.cprint (u'9У нас есть золотых лопат:  ^15_%s' % (self.shovel_extra))
        else:
            print u'Сегодня полито деревьев:   ', self.st_rFFT
            print u'Сегодня закопано медведей: ', self.st_rMP
            print u'Застукано ёлок:            ', self.st_rNY
            print u'Стукнуто корзинок:         ', self.st_rT
            #print u'Стукнуто шатров:           ', self.st_rT
            #print u'Стукнуто самолётов:        ', self.st_rT
            print u'У нас есть золотых лопат:  ', self.shovel_extra
            #print 'haveTreasure ', self._get_game_state().get_state().haveTreasure  # копать
            #print 'haveRemoteFertilizeFruit ', self._get_game_state().get_state().haveRemoteFertilizeFruit  # поливать
            pass

    def statistics(self, userdig, global_lopat, len_friends, color_print):
        end_rFFT = len(self._get_game_state().get_state().remoteFertilizeFruitTree)
        end_rMP = len(self._get_game_state().get_state().remoteMonsterPit)
        end_rNY = len(self._get_game_state().get_state().remoteNewYear)
        end_rT = len(self._get_game_state().get_state().remoteThanksgiving)
        # remoteTrickTreating - шатёр
        # remoteThanksgiving - корзинка пасхальная
        # remoteThanksgiving - самолёт
        end_rVT = len(self._get_game_state().get_state().remoteValentineCollect)
        if len_friends:
            percent_userdig = round(userdig/(len_friends/float(100)), 1)
        else:
            percent_userdig = 0
        if userdig != 0:
            average_lopat = round(global_lopat/float(userdig), 1)
        else:
            average_lopat = 0

        print ' '
        self.cprint(u'9---  Статистика  сеанс/сегодня---')
        if color_print:
            self.cprint (u'9Полито деревьев:   ^15_%s/%d' % (end_rFFT- self.st_rFFT, end_rFFT))
            self.cprint (u'9Закопано медведей: ^15_%s/%d' % (end_rMP - self.st_rMP, end_rMP))
            self.cprint (u'9Застукано ёлок:    ^15_%s/%d' % (end_rNY - self.st_rNY, end_rNY))
            self.cprint (u'9Деревьев Страсти:  ^15_%s/%d' % (end_rVT - self.st_rVT, end_rVT))
            #self.cprint (u'9Стук в корзинки:   ^15_%s/%d' % (self.air_num, end_rT))
            #self.cprint (u'9Стук в шатры:      ^15_%s/%d' % (self.air_num, end_rT))
            #self.cprint (u'9Стук в самолёты:   ^15_%s/%d' % (self.air_num, end_rT))
            self.cprint (u'9Покопали у:        ^15_%s    ^9_юзеров,  ^15_%4.1f%%^9_от списка' % (userdig, percent_userdig))
            self.cprint (u'9Истратили:         ^15_%s    ^9_лопат,  ^15_~%4.1f ^9_на друга' % (global_lopat, average_lopat))
            self.cprint (u'9Осталось лопат:    ^15_%s' % (self.shovel_extra - global_lopat)) 
        else:
            print u'Сегодня полито деревьев:   ', end_rFFT- self.st_rFFT, '/', end_rFFT
            print u'Сегодня закопано медведей: ', end_rMP - self.st_rMP, '/', end_rMP
            print u'Застукано ёлок:            ', end_rNY - self.st_rNY, '/', end_rNY
            #print u'Стук в корзинки:           ', self.air_num, '/', end_rT
            #print u'Стук в шатры:              ', self.air_num, '/', end_rT
            #print u'Стук в самолётыы:          ', self.air_num, '/', end_rT
            print u'Покопали у:                ', userdig, u'    юзеров, ', percent_userdig, u'%% от списка'
            print u'Истратили:                 ', global_lopat, u'    лопат  ', '~' + average_lopat, u'на друга'
            print u'Осталось лопат:            ', self.shovel_extra - global_lopat

    def pickups_mini(self, global_lopat):
        if not hasattr(self._get_game_state(),'all_pickups'): return
        print
        self.cprint(u'9Общий профит:')
        boz = 0
        for pickup in self._get_game_state().all_pickups:
            if pickup.id == 'CR_666': boz = pickup.count
            elif pickup.type == 'coins': self.cprint(u'3Монет^15_%d' % (pickup.count))
            elif pickup.type == 'xp': self.cprint(u'3Опыта^15_%d' % (pickup.count))

        #lopat_boz = round(global_lopat/float(boz), 1)
        if boz:
            self.cprint(u'3Бозон Хигса^15_%d   ^15_~ %d^9_лопат/на бозон' % (boz, global_lopat/boz))
        else:
            self.cprint(u'3Бозон Хигса^15_%d' % (boz))

    def pickups(self):
        if not hasattr(self._get_game_state(),'all_pickups'): return
        #print 'all_pickups', obj2dict(self._get_game_state().all_pickups)
        print
        self.cprint(u'9Предметы:')
        for pickup in self._get_game_state().all_pickups:
            if pickup.type == 'storageItem' and pickup.id != 'CR_666':
                name = self._get_item_reader().get(pickup.id).name
                self.cprint(u'3%s^15_%d' % (name, pickup.count))
        print
        self.cprint(u'9Предметы коллекций:')
        for pickup in self._get_game_state().all_pickups:
            if pickup.type == 'collection':
                name = self._get_item_reader().get(pickup.id).name
                self.cprint(u'3%s^15_%d' % (name, pickup.count))
        print

    def add_action(self, type, action, info=False):
        if not type in self.actions_list:
            self.actions_list[type] = []
        self.actions_list[type].append(action)
        if info:
            self.actions_info[type] = info

    def events_append(self, event):
        self.events_is_empty = False
        self._events.append(event)
        if len(self._events) > 19:
            #logger.info(u'Сольём очередь бот Vint')
            self.events_free()

    def events_free(self):
        self.events_is_empty = True
        if self._events != []:self._get_events_sender().send_game_events(self._events)
        self._events = []
        
    def load_friend_isle(self, friend, isle):
        self._get_game().load_friend = True
        self._get_game_state().set_game_loc_was = False
        self._get_events_sender().send_game_events([{"action":"gameState","locationId":isle,"user":str(friend),"objId":None,"type":"gameState"}])
        time.sleep(0.2)
        self._get_game().handle_all_events()
        _first = True
        while not self._get_game_state().set_game_loc_was:
            if _first:
                print u'Ждём загрузки острова',
                _first = False
            print u'\b.',
            self._get_events_sender().send_game_events([])
            self._get_game().handle_all_events()
            time.sleep(0.2)
        print u'\b.'
        self._get_game().load_friend = False

    def go_home(self, color_print, isle_go):  # возвращаемся домой
        if color_print:
            self.cprint(u'13       Возвращаемся домой       ')
        else:
            logger.info(u'       Возвращаемся домой       ')
        self._get_game_state().set_game_loc_was = False
        self._get_events_sender().send_game_events([{
                "action":"gameState",
                "locationId":isle_go,
                "type":"gameState"
                }])
        time.sleep(0.2)
        self._get_game().handle_all_events()
        _first = True
        while not self._get_game_state().set_game_loc_was:
            if _first:
                print u'Ждём возвращения домой',
                _first = False
            print u'\b.',
            self._get_events_sender().send_game_events([])
            self._get_game().handle_all_events()
            time.sleep(0.2)
        print u'\b.'
        time.sleep(3)
        self._get_game().handle_all_events()

    def myid_in_list(self, object, rem_, fid):
        for _usr in obj2dict(rem_):
            if int(fid) == int(_usr['user']) and int(object.id) == int(_usr['treeId']):
                return True
        return False

    def myid_in_list2(self, object, rem_, fid):
        for _usr in obj2dict(rem_):
            if int(fid) == int(_usr['user']):
                return True
        return False        

    def fid_in_list(self, fid, list):
        for user in obj2dict(list):
            if str(fid) == user['user']:
                return True
        return False

    def response_wait(self, types=[]):
        for i in range(25): # сколько итераций ждём нужного ответа
            self._get_game().handle_all_events()
            if types:
                for type in types:
                    if type in self._get_game().res_types:
                        return type
            self._get_events_sender().send_game_events([])
            time.sleep(0.2)
            #print u'Ждём:', types
        return False

    def console_log(self,curuser,userdig,global_lopat):  # консоль
        end_rFFT = len(self._get_game_state().get_state().remoteFertilizeFruitTree)
        end_rMP = len(self._get_game_state().get_state().remoteMonsterPit)
        end_rNY = len(self._get_game_state().get_state().remoteNewYear)
        end_rT = len(self._get_game_state().get_state().remoteThanksgiving)
        # remoteThanksgiving - самолёт
        # remoteTrickTreating - шатёр
        # remoteThanksgiving - корзинка пасхальная

        # str(self.air_num)+'/'+str(end_rT)
        # str(end_rFFT- self.st_rFFT)+'/'+str(end_rFFT)
        # str(end_rMP - self.st_rMP)+'/'+str(end_rMP)
        # str(end_rNY - self.st_rNY)+'/'+str(end_rNY)
        # str(global_lopat)+'/'+str(self.shovel_extra - global_lopat) 
        # копали userdig, '    юзеров'
        os.system((u'title '+curuser+u' Дерев: '+str(end_rFFT-self.st_rFFT)+'/'+str(end_rFFT)+u'   Миша: '+str(end_rMP - self.st_rMP)+'/'+str(end_rMP)+u'  Ёлки: '+str(end_rNY - self.st_rNY)+'/'+str(end_rNY)+u'  ЮзКоп: '+str(userdig)+u'  Лопат: '+str(global_lopat)+'/'+str(self.shovel_extra - global_lopat)).encode('cp1251', 'ignore'))
        #os.system((u'title '+u'Корз: '+str(self.air_num)+'/'+str(end_rT)+u'  Дерев: '+str(end_rFFT-self.st_rFFT)+'/'+str(end_rFFT)+u'   Миша: '+str(end_rMP - self.st_rMP)+'/'+str(end_rMP)+u'  Ёлки: '+str(end_rNY - self.st_rNY)+'/'+str(end_rNY)+u'  ЮзКоп: '+str(userdig)+u'  Лопат: '+str(global_lopat)+'/'+str(self.shovel_extra - global_lopat)).encode('cp1251', 'ignore'))
        #os.system((u'title '+u'Air: '+str(self.air_num)+'/'+str(end_rT)+u'  Дерев: '+str(end_rFFT-self.st_rFFT)+'/'+str(end_rFFT)+u'   Миша: '+str(end_rMP - self.st_rMP)+'/'+str(end_rMP)+u'  Ёлки: '+str(end_rNY - self.st_rNY)+'/'+str(end_rNY)+u'  ЮзКоп: '+str(userdig)+u'  Лопат: '+str(global_lopat)+'/'+str(self.shovel_extra - global_lopat)).encode('cp1251', 'ignore'))
        pass


class KnockTeam(BaseActor):
    def perform_action(self):
        if self.location_id() != 'main': return
        if not hasattr(self._get_game_state().get_state(),'pirate'): return

        par = self.mega().knock_team()
        seaman = par.get('seaman',[])
        knock_time = par.get('knock_time',[])
        delta_t = par.get('na_vse_pro_vse',5)
        self.curuser = self._get_game_state().get_curuser()
        if (not knock_time) or (not seaman) or (self.curuser not in seaman): return
        
        if self.check_away(knock_time, delta_t): return
        if self.check_time_period(knock_time, delta_t):
            if self.set_pirate_box():
                # настукиваем друзьям
                self.knock_in_ships()
                self.waits(300)
            else:
                self.cprint(u'13Нет сундука или места под выставление')
                self.waits(20)
                return
        self.gdems(knock_time, delta_t)
        return


    def gdems(self, knock_time, delta_t):
        cur_dtime = datetime.now()
        if not knock_time: return
        for knock in knock_time:
            h = int(knock.split(':')[0])
            m = int(knock.split(':')[1])
            tt = cur_dtime
            tt = tt.replace(hour=h, minute=m, second=0)
            dlt = cur_dtime - tt
            total_dlt = dlt.total_seconds()
            # print total_dlt
            if total_dlt > -1 and total_dlt < (delta_t * 60):
                return
            elif total_dlt < 0:
                pause = abs(total_dlt) - 1
                break
            elif total_dlt == 0:
                time.sleep(0.3)
                return
        if pause:
            m = pause/60
            s = int(pause - int(m)*60)
            self.cprint(u'9Ждём следующего периода^15_%d:%d ^1_начало в %s' % (m,s,time.strftime('%H:%M:%S', time.localtime(time.time()))))
            sec = time.time()
            prov_away = time.time()
            while pause > 5:
                m = pause/60
                s = int(pause - int(m)*60)
                self.cprint2(u'9\rОсталось ждать^15_%d:%d  ' % (m,s))
                if (time.time() - sec) > 27:
                    self.send([])
                    sec = time.time()
                self._get_game().handle_all_events()
                while self._get_game().ping:
                    self._get_game().handle_all_events()
                time.sleep(5)
                if (time.time() - prov_away) > 60:
                    prov_away = time.time()
                    if self.check_away(knock_time, delta_t): return
                pause -= 5
            m = pause/60
            s = int(pause - int(m)*60)
            self.cprint2(u'9\rОсталось ждать^15_%d:%d  ' % (m,s))
            time.sleep(pause)
            self.cprint2(u'9\rОсталось ждать^15_%d:%d ^9_продолжаем работу' % (0,0))
            print

    def waits(self, pause):
        sec = time.time()
        global_w = time.time() + pause
        while global_w > time.time():
            if (time.time() - sec) > 27:
                self.send([])
                sec = time.time()
            self._get_game().handle_all_events()
            while self._get_game().ping:
                self._get_game().handle_all_events()
            time.sleep(1)

    def check_away(self, knock_time, delta_t):
        if self._get_game_state().get_state().pirate.state == 'AWAY':
            if self.check_time_period(knock_time, delta_t):
                if hasattr(self._get_game_state().get_state().pirate, 'captain'):
                    captain = str(self._get_game_state().get_state().pirate.captain)
                else:
                    captain = u'неизвестный'
                _date = time.strftime(' %Y.%m.%d %H:%M:%S ', time.localtime(time.time()))
                text = str(self.curuser) + u' ' + _date
                text += u' товарищ ' + captain + u' уплыл не вовремя! И кинул нас на палача.'
                with open('REDISKI.txt', 'a') as f: 
                    f.write(text.encode('utf-8'))
            self.otchalivaem(0)
            return True
        return False

    def check_time_period(self, knock_time, delta_t):
        cur_dtime = datetime.now()
        for knock in knock_time:
            h = int(knock.split(':')[0])
            m = int(knock.split(':')[1])
            tt = cur_dtime
            tt = tt.replace(hour=h, minute=m, second=0)
            dlt = cur_dtime - tt
            total_dlt = dlt.total_seconds()
            # print total_dlt
            if total_dlt > -1 and total_dlt < (delta_t * 60):
                return True
        return False
        
    def check_time_sliv(self, knock_time, delta_time_sliv):
        sdvig = timedelta(minutes=delta_time_sliv[0])
        delta_t = delta_time_sliv[1] - delta_time_sliv[0]
        cur_dtime = datetime.now()
        for knock in knock_time:
            h = int(knock.split(':')[0])
            m = int(knock.split(':')[1])
            tt = cur_dtime
            tt = tt.replace(hour=h, minute=m, second=0)
            tt = tt + sdvig
            dlt = cur_dtime - tt
            total_dlt = dlt.total_seconds()
            # print total_dlt
            if total_dlt > -1 and total_dlt < (delta_t * 60):
                return True
        return False

    def check_storage_pirate_box(self):
        if self._get_game_state().get_state().pirate.state == 'PIRATE' or\
                self._get_game_state().get_state().pirate.state == 'AWAY':
            # self._get_game_state().ap_state['pirate_box'] = 'isle'
            return False
        pirateBox = ['@PIRATE_BOX','@PIRATE_BOX_2']
        for box in pirateBox:
            if self._get_game_state().count_in_storageObjects(box) > 0:
                # self._get_game_state().ap_state['pirate_box'] = 'storage'
                self._box = box
                return True
        # self._get_game_state().ap_state['pirate_box'] = 'none'
        return False

    def set_pirate_box(self):
        if self._get_game_state().get_state().pirate.state == 'PIRATE': return True
        if self._get_game_state().get_state().pirate.state == 'AWAY': return True
        if self._get_game_state().get_state().pirate.state != 'CITIZEN': return False
        if not self.check_storage_pirate_box(): return False

        objects = self._get_game().get_free_spaces().newObject(self._box)
        if len(objects) == 0:
            print u'Нет пустого места'
            return False
        maxY = -1
        for obj in objects:
            if obj.y > maxY:
                maxY = obj.y
                obj_maxY = obj

        obj_maxY.id = self.new_id()
        set_event = {
                "x":obj_maxY.x,
                "y":obj_maxY.y,
                "action":"placeFromStorage",
                "type":"item",
                "itemId":self._box.lstrip('@'),
                "objId":obj_maxY.id
                }
        self.send([set_event])
        self._get_game_state().get_state().gameObjects.append(obj_maxY)
        self._get_game_location().get_game_objects().append(obj_maxY)
        self._get_game_state().add_from_storageObjects(self._box, -1)
        self._get_game_state().get_state().pirate.state = 'PIRATE'
        # self._get_game_state().ap_state['pirate_box'] = 'isle'
        logger.info(u'Выставили пиратский сундук')
        return True

    def otchalivaem(self,id):
        # raw_input('-------------   END   ---------------')
        fol_cur = 'statistics\\' + self.curuser # короткое имя папки юзера
        if os.path.isfile(fol_cur + '\\stone_well.txt'):
            os.remove(fol_cur + '\\stone_well.txt')
        if os.path.isfile(fol_cur + '\\sw_run.txt'):
            os.remove(fol_cur + '\\sw_run.txt')
        if os.path.isfile(fol_cur + '\\chop_broot_id.txt'):
            os.remove(fol_cur + '\\sw_run.txt')
        if os.path.isfile(fol_cur + '\\brut_off.txt'):
            os.remove(fol_cur + '\\brut_off.txt')
        if os.path.isfile(fol_cur + '\\end_did.txt'):
            os.remove(fol_cur + '\\end_did.txt')
        if hasattr(self._get_game_state(), 'wealth_roll'):
            delattr(self._get_game_state(), 'wealth_roll')
        if hasattr(self._get_game_state(), 'brut'):
            delattr(self._get_game_state(), 'brut')

        if self._get_game_state().get_state().pirate.state == 'AWAY':
            self.clear_pirate_box()
            event = {"type":"pirate","action":"sail"}
            self.cprint(u'14Отплываем матросом!')
            cap = False
        else: return
        self._get_game_state().set_game_loc_was = False
        self.send([event])
        self._get_game().handle_all_events()
        print u'Ждём загрузки острова',
        while not self._get_game_state().set_game_loc_was:
            print u'\b.',
            self._get_events_sender().send_game_events([])
            self._get_game().handle_all_events()
            time.sleep(0.2)
        print u'\b.'
        event = {"type":"action","action":"getMissions"}
        self.send([event])
        self._get_game().handle_all_events()
        self._get_game_state().get_state().pirate.state = 'AWAY'
        print u'Уплыли'
        time.sleep(5)
        self._get_game().handle_all_events()

    def clear_pirate_box(self):
        if len(self._get_game_state().get_state().pirate.instruments) == 0: return
        for object in self._get_game_state().get_state().gameObjects:
            if object.item in ['@PIRATE_BOX', '@PIRATE_BOX_2']:
                clear_events = []
                for instr in self._get_game_state().get_state().pirate.instruments:
                    if not instr.count: continue
                    event = {
                            "type":"item",
                            "action":"moveInstrumentFromBox",
                            "count":instr.count,
                            "itemId":instr.item.lstrip('@')
                            }
                    clear_events.append(event)
                    self._get_game_state().add_from_storage(instr.item,instr.count)
                    instr.count = 0
                if clear_events:
                    self.send(clear_events)
                    logger.info(u'Убрали инструмент из сундука')
                break


    # pirate_frends
    def opt(self, option):
        options = self.mega().friends_pirat()['что делаем']
        return option in options

    def knock_in_ships(self):
        par_ap = self.mega().auto_pirate_options()
        gop_company = par_ap.get('gop_company',[])
        nahlebniki = par_ap.get('nahlebniki',[])
        friends = gop_company + nahlebniki
        isle_go = 'main'
        
        if self.if_location_pirate(): return
        if not friends: return
        logger.info(u'Идём по друзьям стучать в корабли')
        self.write_log(u'Идём по друзьям стучать в корабли')

        # настройки
        par = self.mega().friends_pirat()['параметры']
        shovels = par.get('shovels',50)
        max_monster = par.get('max_monster',99)
        con_user = par.get('con_user',50)
        color_print = par.get('color_print',False)
        circle_dig = par.get('circle_dig',False)
        only_first = par.get('only_first',False)
        sort_green = par.get('sort_green',False)

        # что копаем:
        favdecors = []
        favdecors_list = self.mega().friends_pirat()['что копаем']
        for f in favdecors_list:
            favdecors.extend(f)

        # author Vint, Loconaft, and other
        #----------------------------------------------------------------------------------------------------

        # if (not circle_dig) and hasattr(self._get_game_state(), 'all_visited') and self._get_game_state().all_visited:
            # logger.info('-------------   END   ---------------')
            # return # всех друзей прошли уже

        isle = 'main'

        curuser = str(self._get_game_state().get_curuser())
        self.myid = self._get_game_state().get_my_id()
        
        if str(self.myid) in friends:
            friends.remove(str(self.myid))

        self.antilag(1)  # антилаг загрузки, сек
        if hasattr(self._get_game_state(), 'playersInfo'):
            players_info = self._get_game_state().playersInfo
            len_playersInfo = len(players_info)
            # print u'Начальная длина playersInfo %d' % len_playersInfo
        else:
            players_info = []
            len_playersInfo = len(players_info)
            if color_print:
                self.cprint(u'12Инфа о друзьях не получена.')
            else:
                print u'Инфа о друзьях не получена.'

        if not os.path.isdir('statistics\\'+curuser+'\copatel'):
            os.makedirs('statistics\\'+curuser+'\copatel')
        fol_cop = 'statistics\\'+curuser+'\\copatel'

        userdig = 0
        global_lopat = 0
        self.air_num = 0
        cakelimit = False
        self._events = []
        state_min = [int(time.time()/60)]
        self.read_shovel_extra()
        self.statistics_start(color_print)

        # основной цикл обхода друзей
        for n_v in range(len(friends)):
            fid = friends[n_v]
            if hasattr(self._get_game_state(), 'playersInfo') and len_playersInfo != len(self._get_game_state().playersInfo):
                players_info = self._get_game_state().playersInfo
                add_playersInfo = len(players_info) - len_playersInfo
                len_playersInfo = len(players_info)
                if color_print:
                    self.cprint(u'4Произошло обновление players_info')
                else: logger.info(u'Произошло обновление players_info')
                print u'Длина playersInfo изменилась на %d' % add_playersInfo

            # консоль
            self.console_log(curuser,userdig,global_lopat)

            # проверяем зелёный ли друг
            if sort_green and hasattr(self._get_game_state(), 'playersInfo'):
                load = False
                for info in players_info:
                    if str(info.id) == str(fid):
                        load = True
                        break
                if load and not info.liteGameState.haveTreasure:
                    #print u'У друга всё выкопано!'
                    continue

            # проверяем забанен ли друг
            if sort_green and hasattr(self._get_game_state(), 'playersInfo'):
                load = False
                for info in players_info:
                    if str(info.id) == str(fid):
                        load = True
                        break
                if load and info.banned:
                    #print u'Друг в бане!'
                    continue

            name_user = self.name_user(fid)

            num_u = str(fid).ljust(20, " ")
            sp_n = u' '*(14-len(name_user))
            print ' '
            if color_print:
                self.cprint(u'9##### Идем к другу^14_'+num_u+u'^3'+name_user+sp_n+u'^15_%d/%d^9на^3_%s^9#####'%((n_v+1), len(friends), isle))
            else:
                logger.info(u'##### Идем к другу '+num_u+u' '+name_user+sp_n+u'%d/%d на %s #####'%((n_v+1), len(friends), isle))
            self._get_game_state().planeAvailable = True
            self.load_friend_isle(fid, isle)
            
            UserIsAway = self._get_game_state().get_state().isAway
            if UserIsAway: # True
                print u' ',
                self.cprint(u'71Друг давно не был в игре!!!')
           
            self.actions_list = {} # эвент хранилище
            self.actions_info = {} # эвент описания
            guardGrave = 0         # наличие сторожа
            objssvl = {}           # что копать
            cone_user = con_user
            countnyt = 0
            haveRemoteFertilizeFruit = True
            haveRemoteValentineTower = True
            
            if self._get_game_state().get_state().haveTreasure:
                alldigged = False
            else:
                alldigged = True
                logger.info(u'Здесь всё выкопано...')
                


            for object in self._get_game_location().get_game_objects():

                if object.type == 'guardGrave':
                    logger.info(u'------------ Сторож !!! ------------')
                    guardGrave = 1

                # разбивать тайники
                if object.type == 'friendTransformObject':
                    if self.opt('split_caches'):
                        if object.transformed:continue
                        name = self._get_item_reader().get(object.item).name
                        eventtrans = {"action":"remoteFriendTransform","type":"item","objId":object.id}
                        self._get_events_sender().send_game_events([eventtrans])
                        self.cprint(u'5Разбил %s' % name.upper())
                    continue


                # Стучим в Разные постройки
                if object.type == 'thanksgivingTable':
                    if self.opt('thanksgiving'):
                        day_stuk = self._get_game_state().get_state().remoteThanksgiving
                        reader_thanks = self._get_item_reader().get(object.item)
                        if (not self._get_game_state().planeAvailable) or len(day_stuk) >= 100 or object.usedPlatesCount >= reader_thanks.platesCount: continue
                        if hasattr(reader_thanks, 'endSellingDate') and int(reader_thanks.endSellingDate)/1000 < time.time(): continue
                        for days in day_stuk:
                            if str(fid) == str(days.user):
                                if color_print:
                                    self.cprint(u'4Сегодня мы уже стукнули у этого друга')
                                else:
                                    logger.info(u'Сегодня мы уже стукнули у этого друга')
                                self._get_game_state().planeAvailable = False
                                break
                        else:
                            readerGifts = self._get_item_reader().get(reader_thanks.gifts[0])
                            eventtrans = {
                                        "itemId": readerGifts.id, 
                                        "action": "remoteThanksgiving",
                                        "type": "item", 
                                        "objId": object.id
                                        }
                            self._get_events_sender().send_game_events([eventtrans])
                            apend_frend = {u'count': 0L, u'date': u'-19849562', u'user': str(fid)}
                            self._get_game_state().get_state().remoteThanksgiving.append(dict2obj(apend_frend))
                            self.cprint(u'5%s в %s' % (readerGifts.name,reader_thanks.name))
                            self._get_game_state().planeAvailable = False
                            self.air_num += 1
                    continue

                # Стучим в пиратский сундук
                if object.type == 'pirateBox':
                    if self.opt('pirateCheckin') and self._get_game_state().get_state().pirate.state == 'CITIZEN':
                        event = {"objId":object.id,"type":"item","action":"remotePirateCheckin"}
                        self._get_events_sender().send_game_events([event])
                        if color_print:
                            self.cprint(u'5Застукал Пиратский сундук')
                        else: logger.info(u'Застукал Пиратский сундук')
                    continue

                # Стучим в лодки
                if object.type == 'pirateShip':
                    if (self.opt('pirateBoats') or self.opt('pirateSchooner') or self.opt('pirateCaravel')) and\
                            (self._get_game_state().get_state().pirate.state == 'PIRATE') and object.level == 2:
                        if self.opt('pirateBoats') and object.item == u'@B_PIRATE_BOAT_2' and len(object.team) < 5:
                            if not str(self.myid) in str(object.team):
                                self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","action":"remotePirateJoinTeam"}])
                                if color_print:
                                    self.cprint(u'5Попросился в команду на Пиратскую Лодку!')
                                else: logger.info(u'Попросился в команду на Пиратскую Лодку!')
                            else:
                                if color_print:
                                    self.cprint(u'4Ты уже в команде на Пиратской Лодке')
                                else: logger.info(u'Ты уже в команде на Пиратской Лодке')
                        if self.opt('pirateSchooner') and object.item == u'@B_PIRATE_SCHOONER_2' and len(object.team) < 5:
                            if not str(self.myid) in str(object.team):
                                self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","action":"remotePirateJoinTeam"}])
                                if color_print:
                                    self.cprint(u'5Попросился в команду на Пиратскую Шхуну!')
                                else: logger.info(u'Попросился в команду на Пиратскую Шхуну!')
                            else:
                                if color_print:
                                    self.cprint(u'4Ты уже в команде на Пиратской Шхуне')
                                else: logger.info(u'Ты уже в команде на Пиратской Шхуне')
                        if self.opt('pirateCaravel') and object.item == u'@B_PIRATE_CARAVEL_2' and len(object.team) < 7:
                            if not str(self.myid) in str(object.team):
                                self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","action":"remotePirateJoinTeam"}])
                                if color_print:
                                    self.cprint(u'5Попросился в команду на Пиратскую Каравеллу!')
                                else: logger.info(u'Попросился в команду на Пиратскую Каравеллу!')
                            else:
                                if color_print:
                                    self.cprint(u'4Ты уже в команде на Пиратской Каравелле')
                                else: logger.info(u'Ты уже в команде на Пиратской Каравелле')
                    continue

                # Удобряем фруктовые деревья
                if object.type == "fruitTree":
                    if self.opt('fruitTree') and haveRemoteFertilizeFruit == True and (object.jobFinishTime > 0) and (len(self._get_game_state().get_state().remoteFertilizeFruitTree) < 20): # self._get_game_state().get_state().haveRemoteFertilizeFruit == True
                        #treefruit = ['FT_APPLE','FT_CHERRY','FT_MANDARINE','FT_LEMON','FT_SKULL','FT_EYE']
                        if self.fid_in_list(fid, self._get_game_state().get_state().remoteFertilizeFruitTree):
                            if color_print:
                                self.cprint(u'4Сегодня мы уже здесь полили')
                            else: logger.info(u'Сегодня мы уже здесь полили')
                            haveRemoteFertilizeFruit = False
                            continue
                        if color_print:
                            self.cprint(u'5Удобряем дерево!')
                        else: logger.info(u'Удобряем дерево!')
                        self._get_events_sender().send_game_events([{"action":"remoteFertilizeFruitTree","type":"item"}])
                        self._get_game_state().get_state().remoteFertilizeFruitTree.append({u'count': '0L', u'date': u'-2435527', u'user':fid})
                        haveRemoteFertilizeFruit = False
                    continue

                # Вскрываем сундук
                if object.type == 'pickup':
                    if self.opt('box'):
                        #open('sunduki.txt', 'a').write(str(obj2dict(object)) + "\n")
                        self.add_action('pickupbox', {"action":"pick","type":"item","objId":object.id})
                    continue

                # Ёлки
                if object.type == 'newYearTree' and 'B_SPRUCE_' in object.item:
                    if cakelimit: continue 
                    if self.opt('conifer') and countnyt < cone_user:
                        rem_ = self._get_game_state().get_state().remoteNewYear
                        if len(rem_) < 150:
                            if object.level < 2:
                                print u'Ёлка недостроена...'
                                continue
                            if len(rem_) > 0:
                                countmyg = 0
                                if self.myid_in_list(object, rem_, fid):
                                    if color_print:
                                        self.cprint(u'4Сегодня мы уже стукнули в эту ёлку')
                                    else: logger.info(u'Сегодня мы уже стукнули в эту ёлку')
                                    continue
                            usrs = len(object.users)
                            #Ёлки разной ёмкости.
                            if object.item == u'@B_SPRUCE_SMOLL' and usrs > 2: continue
                            if object.item == u'@B_SPRUCE_MIDDLE' and usrs > 5: continue
                            if object.item == u'@B_SPRUCE_BIG' and usrs > 14: continue

                            print u'Ложим пряник'
                            self.add_action('newyeartree', {"itemId":"CAKE_PACK_FREE1","action":"remoteNewYear","type":"item","objId":object.id})
                            self._get_game_state().get_state().remoteNewYear.append({u'treeId':object.id, u'user':fid})
                            countnyt += 1
                        else:
                            cakelimit = True
                            if False: # color_print:
                                self.cprint(u'8Исчерпан лимит на пряники...')
                            else: print u'Исчерпан лимит на пряники...'
                    continue

                # Мишка
                if object.type == 'monsterPit':
                    l = self._get_game_state().get_state().remoteMonsterPit
                    if self.opt('monster') and len(l) < 100:
                        if object.state == 'DIGGING':
                            mon_depth = sum(+int(i.depth )for i in object.users) # Глубина закопки мишки
                            if mon_depth > 99:
                                #print 'mon_depth', mon_depth, 'len(object.users)', len(object.users)
                                logger.info(u'За баксы не закапываем. Глубина %d м.'% mon_depth)
                                continue
                            if mon_depth > max_monster:
                                logger.info(u'Мишка закопан больше положенного. Глубина %d м.'% mon_depth)
                                continue
                            # Проверка на повторное закапывание в один день
                            if len(l) > 0:
                                if self.fid_in_list(fid, l):
                                    if color_print:
                                        self.cprint(u'4Сегодня мы уже зарывали этого мишку...')
                                    else: logger.info(u'Сегодня мы уже зарывали этого мишку...')
                                    continue
                            if color_print:
                                self.add_action('monster', {"itemId":"MONSTER_PIT_1_INSTRUMENT_PACK_DEFAULT","action":"remoteMonsterPit","type":"item","objId":object.id})
                                self.cprint(u'5Закапываем чудика. Закопало^15_%d^5человек на глубину ^15_%s ^5_м.'%(len(object.users), mon_depth))
                            else:
                                self.add_action('monster', {"itemId":"MONSTER_PIT_1_INSTRUMENT_PACK_DEFAULT","action":"remoteMonsterPit","type":"item","objId":object.id}, (u'Закапываем чудика. Закопало %d человек на глубину %s м.'%(len(object.users), mon_depth)))
                            #open('monster.txt', 'a').write(str(obj2dict(object))+"\n")
                            self._get_game_state().get_state().remoteMonsterPit.append({u'count': '0L', u'date': u'-5130168', u'user':fid})
                        else:
                            logger.info(u'Мишку нельзя закопать')
                    continue

                # Дерево страсти & сад бабочек
                if object.type == 'valentineTower':
                    if self.opt('valentine') and object.item == u'@VALENTIINE_TOWER':
                        l = self._get_game_state().get_state().remoteValentineCollect
                        if len(l) >= 300 or object.count <= 0: continue
                        # Проверка на повторный стук в один день
                        if len(l) > 0:
                            if self.fid_in_list(fid, l):
                                if color_print:
                                    self.cprint(u'4Сегодня мы уже стучали этому другу по дереву страсти...')
                                else: logger.info(u'Сегодня мы уже стучали этому другу по дереву страсти...')
                                continue
                        if object.level < 8:
                            if color_print:
                                self.cprint(u'5Стучим в Дерево Страсти!')
                            else:
                                logger.info(u'Стучим в Дерево Страсти!')
                            event_valentine = {"action":"remoteValentineCollect","type":"item","objId":object.id}
                            self._get_events_sender().send_game_events([event_valentine])
                            addUser = {u'count': '0L', u'date': '0L', u'user':str(fid)}
                            self._get_game_state().get_state().remoteValentineCollect.append(addUser)
                        else:
                            logger.info(u'Это дерево страсти уже построено')

                    ##### Стучим в сад бабочек #####
                    elif self.opt('valentine2') and object.item == u'@B_BUTTERFLY_GARDEN':
                        # self.cprint(u'1длина списка стукнутых^12_%d' % (len(l)))
                        # print 'object.level =', object.level
                        if len(l) >= 300 or object.count <= 0: continue  # or object.level > 4
                        for valent in l:
                            if valent.user == str(fid):
                                if color_print:
                                    self.cprint(u'4Сегодня мы уже стучали этому другу в сад...')
                                else: logger.info(u'Сегодня мы уже стучали этому другу в сад...')
                                break
                        else:
                            if color_print:
                                self.cprint(u'5Стукнул в сад бабочек!')
                            else: logger.info(u'Стукнул в сад бабочек!')
                            addUser = {u'count':0, u'date': -300000, u'user': str(fid)}
                            eventValent = {"type":"item","objId":object.id,"action":"remoteValentineCollect","id":None}
                            self._get_events_sender().send_game_events([eventValent])
                            self._get_game_state().get_state().remoteValentineCollect.append(dict2obj(addUser))
                    continue

                # КопАй!!!
                if self.opt('kopatel'):
                    if alldigged:
                        continue
                    if favdecors == None or len(favdecors) == 0:
                        continue
                    else:
                        name = object.item.lstrip('@')
                        if name in objssvl: # Уже есть такая
                            continue
                        # Добавляем в список объект для копания
                        if name in favdecors:
                            if only_first and len(objssvl) > 0: # Уже нашли, что покопать
                                now = objssvl.keys()[0]
                                if favdecors.index(name) < favdecors.index(now): # Индекс этого object меньше, чем того, что уже нашли, => он приоритетнее
                                    objssvl = {} # очистим и ниже добавим
                                else:
                                    continue
                            logger.info(u'####### Найдена декорация %s #######' % name)
                            objssvl[name] = object
            #logger.info(u'Перебор объектов закончен')

            # Покопаем
            if self.opt('kopatel'):
                if len(objssvl) <= 0:
                    if not alldigged:
                        logger.info(u'Нет объектов для копки')
                else:
                    objs = objssvl.values()
                    userdig += 1
                    lopat = 0
                    while True: # цикл копки
                        if lopat >= shovels: break
                        lopat += 1
                        if only_first:objdig = objs[0]
                        else:objdig = random_number.choice(objs)
                        #{"x":61,"y":48,"type":"item","id":46,"action":"remoteDig","objId":48447}
                        self.events_append({"objId":objdig.id,"x":objdig.x,"action":"remoteDig","y":objdig.y,"type":"item"})
                        #print u'Лопата:', lopat
                        if self.events_is_empty: # был слив очереди запросов
                            response = self.response_wait(['alert','pickup'])
                            if response == 'alert':
                                if 'SERVER_REMOTE_TREASURE_ALL_DIGGED' in self._get_game().alerts:
                                    logger.info(u'Всё выкопано!!!')
                                    lopat -= self._get_game().alerts.count('SERVER_REMOTE_TREASURE_ALL_DIGGED')
                                    break
                                if 'SERVER_REMOTE_TREASURE_NO_TRIES' in self._get_game().alerts:
                                    logger.info(u'Закончились лопаты!!!')
                                    lopat = 0
                                    break
                                if 'SERVER_SHOVEL_IS_BAD' in self._get_game().alerts:
                                    logger.info(u'Закончились лопаты!!!')
                                    lopat -= self._get_game().alerts.count('SERVER_SHOVEL_IS_BAD')
                                    break                                    

                            if response == 'pickup':
                                #print u'Можно копать дальше, ибо pickup'
                                pass

                    if lopat:
                        logger.info(u'Использовали "%d" лопат' % lopat)
                        global_lopat += lopat
                    self.events_free()

            # Переберём все экшены
            last_type_file = fol_cop+'\\last_type.txt'
            try:
                last_type = str(open(last_type_file).read())
            except:
                last_type = 'last_type'

            if last_type != 'last_type' and not (last_type in self.actions_list):
                logger.info(u'Типа экшена "%s" нет в очереди - начнём с начала' % last_type)
                last_type = 'last_type'

            for type in self.actions_list:
                #logger.info(u'Начинаем отсылать '+type)
                if last_type != 'last_type': # что-то в прошлый раз произошло
                    if last_type != type:
                        continue
                    else:
                        logger.info(u'Пропустим тип экшена "%s" - он не прошёл в прошлый раз' % last_type)
                        last_type = 'last_type'
                        continue
                open(last_type_file, 'w').write(str(type)) # запишем последний тип экшена и пропустим его, если в прошлый раз на нём произошла фатальная ошибка
                if type in self.actions_info:
                    logger.info(self.actions_info[type]) # выведем справочную инфу

                if type == 'pickupbox' and guardGrave == 1:
                    logger.info(u'Ничего вскрывать не будем, ибо сторож')
                    continue
                logger.info(u'Начинаем отсылать ' + type)

                for a in self.actions_list[type]: # Сам процесс отсылки эвентов
                    self.events_append(a)
                self.events_free()

            open(last_type_file, 'w').write(str('last_type')) # всё прошло удачно - сбросим type
            self._get_game().handle_all_events()

            cur_min = int(time.time()/60)
            if cur_min not in state_min:
                self.statistics(userdig, global_lopat, len(friends), color_print)
                self.pickups_mini(global_lopat)
                state_min.append(cur_min)

        # основной цикл обхода друзей

        self._get_game().handle_all_events()
        print ' '
        self.statistics(userdig, global_lopat, len(friends), color_print)
        self.pickups_mini(global_lopat)
        self.pickups()
        print

        self._get_game_state().all_visited = True
        self.go_home(color_print, isle_go)  # возвращаемся домой

        # идём на следующий круг
        return

    def name_user(self, fid):
        name_user = u'--------------'
        if hasattr(self._get_game_state(), 'friends_names') and self._get_game_state().friends_names.get(str(fid)) and self._get_game_state().friends_names.get(str(fid)) != u'Без имени':
            name_user = u"'" + self._get_game_state().friends_names.get(str(fid)) + u"'"
            #name_user = name_user.replace(u'\u0456', u'i').encode("cp866", "ignore")
        return name_user

    def read_shovel_extra(self):
        for object in self._get_game_state().get_state().storageItems:
            if object.item == '@SHOVEL_EXTRA':
                self.shovel_extra = object.count
                #print 'FIND: ', object.item, '  count = ', self.shovel_extra
                break
        else: self.shovel_extra = 0

    def antilag(self, time_wait):  # антилаг загрузки
        time.sleep(time_wait)
        self._get_game().handle_all_events()

    def statistics_start(self, color_print):
        self.st_rFFT = len(self._get_game_state().get_state().remoteFertilizeFruitTree)
        self.st_rMP = len(self._get_game_state().get_state().remoteMonsterPit)
        self.st_rNY = len(self._get_game_state().get_state().remoteNewYear)
        self.st_rVT = len(self._get_game_state().get_state().remoteValentineCollect)
        self.st_rT = len(self._get_game_state().get_state().remoteThanksgiving)
        # remoteThanksgiving - самолёт
        # remoteTrickTreating - шатёр
        # remoteThanksgiving - корзинка пасхальная
        print ' '
        self.cprint(u'9---  Start  ---')
        if color_print:
            self.cprint (u'9Сегодня полито деревьев:   ^15_%s' % (self.st_rFFT))
            self.cprint (u'9Сегодня закопано медведей: ^15_%s' % (self.st_rMP))
            self.cprint (u'9Застукано ёлок:            ^15_%s' % (self.st_rNY))
            self.cprint (u'9Стукнуто Деревьев Страсти: ^15_%s' % (self.st_rVT))
            self.cprint (u'9Стукнуто корзинок:         ^15_%s' % (self.st_rT))
            #self.cprint (u'9Стукнуто шатров:           ^15_%s' % (self.st_rT))
            #self.cprint (u'9Стукнуто самолётов:        ^15_%s' % (self.st_rT))
            self.cprint (u'9У нас есть золотых лопат:  ^15_%s' % (self.shovel_extra))
        else:
            print u'Сегодня полито деревьев:   ', self.st_rFFT
            print u'Сегодня закопано медведей: ', self.st_rMP
            print u'Застукано ёлок:            ', self.st_rNY
            print u'Стукнуто корзинок:         ', self.st_rT
            #print u'Стукнуто шатров:           ', self.st_rT
            #print u'Стукнуто самолётов:        ', self.st_rT
            print u'У нас есть золотых лопат:  ', self.shovel_extra
            #print 'haveTreasure ', self._get_game_state().get_state().haveTreasure  # копать
            #print 'haveRemoteFertilizeFruit ', self._get_game_state().get_state().haveRemoteFertilizeFruit  # поливать
            pass

    def statistics(self, userdig, global_lopat, len_friends, color_print):
        end_rFFT = len(self._get_game_state().get_state().remoteFertilizeFruitTree)
        end_rMP = len(self._get_game_state().get_state().remoteMonsterPit)
        end_rNY = len(self._get_game_state().get_state().remoteNewYear)
        end_rT = len(self._get_game_state().get_state().remoteThanksgiving)
        # remoteTrickTreating - шатёр
        # remoteThanksgiving - корзинка пасхальная
        # remoteThanksgiving - самолёт
        end_rVT = len(self._get_game_state().get_state().remoteValentineCollect)
        if len_friends:
            percent_userdig = round(userdig/(len_friends/float(100)), 1)
        else:
            percent_userdig = 0
        if userdig != 0:
            average_lopat = round(global_lopat/float(userdig), 1)
        else:
            average_lopat = 0

        print ' '
        self.cprint(u'9---  Статистика  сеанс/сегодня---')
        if color_print:
            self.cprint (u'9Полито деревьев:   ^15_%s/%d' % (end_rFFT- self.st_rFFT, end_rFFT))
            self.cprint (u'9Закопано медведей: ^15_%s/%d' % (end_rMP - self.st_rMP, end_rMP))
            self.cprint (u'9Застукано ёлок:    ^15_%s/%d' % (end_rNY - self.st_rNY, end_rNY))
            self.cprint (u'9Деревьев Страсти:  ^15_%s/%d' % (end_rVT - self.st_rVT, end_rVT))
            #self.cprint (u'9Стук в корзинки:   ^15_%s/%d' % (self.air_num, end_rT))
            #self.cprint (u'9Стук в шатры:      ^15_%s/%d' % (self.air_num, end_rT))
            #self.cprint (u'9Стук в самолёты:   ^15_%s/%d' % (self.air_num, end_rT))
            self.cprint (u'9Покопали у:        ^15_%s    ^9_юзеров,  ^15_%4.1f%%^9_от списка' % (userdig, percent_userdig))
            self.cprint (u'9Истратили:         ^15_%s    ^9_лопат,  ^15_~%4.1f ^9_на друга' % (global_lopat, average_lopat))
            self.cprint (u'9Осталось лопат:    ^15_%s' % (self.shovel_extra - global_lopat)) 
        else:
            print u'Сегодня полито деревьев:   ', end_rFFT- self.st_rFFT, '/', end_rFFT
            print u'Сегодня закопано медведей: ', end_rMP - self.st_rMP, '/', end_rMP
            print u'Застукано ёлок:            ', end_rNY - self.st_rNY, '/', end_rNY
            #print u'Стук в корзинки:           ', self.air_num, '/', end_rT
            #print u'Стук в шатры:              ', self.air_num, '/', end_rT
            #print u'Стук в самолётыы:          ', self.air_num, '/', end_rT
            print u'Покопали у:                ', userdig, u'    юзеров, ', percent_userdig, u'%% от списка'
            print u'Истратили:                 ', global_lopat, u'    лопат  ', '~' + average_lopat, u'на друга'
            print u'Осталось лопат:            ', self.shovel_extra - global_lopat

    def pickups_mini(self, global_lopat):
        if not hasattr(self._get_game_state(),'all_pickups'): return
        print
        self.cprint(u'9Общий профит:')
        boz = 0
        for pickup in self._get_game_state().all_pickups:
            if pickup.id == 'CR_666': boz = pickup.count
            elif pickup.type == 'coins': self.cprint(u'3Монет^15_%d' % (pickup.count))
            elif pickup.type == 'xp': self.cprint(u'3Опыта^15_%d' % (pickup.count))

        #lopat_boz = round(global_lopat/float(boz), 1)
        if boz:
            self.cprint(u'3Бозон Хигса^15_%d   ^15_~ %d^9_лопат/на бозон' % (boz, global_lopat/boz))
        else:
            self.cprint(u'3Бозон Хигса^15_%d' % (boz))

    def pickups(self):
        if not hasattr(self._get_game_state(),'all_pickups'): return
        #print 'all_pickups', obj2dict(self._get_game_state().all_pickups)
        print
        self.cprint(u'9Предметы:')
        for pickup in self._get_game_state().all_pickups:
            if pickup.type == 'storageItem' and pickup.id != 'CR_666':
                name = self._get_item_reader().get(pickup.id).name
                self.cprint(u'3%s^15_%d' % (name, pickup.count))
        print
        self.cprint(u'9Предметы коллекций:')
        for pickup in self._get_game_state().all_pickups:
            if pickup.type == 'collection':
                name = self._get_item_reader().get(pickup.id).name
                self.cprint(u'3%s^15_%d' % (name, pickup.count))
        print

    def add_action(self, type, action, info=False):
        if not type in self.actions_list:
            self.actions_list[type] = []
        self.actions_list[type].append(action)
        if info:
            self.actions_info[type] = info

    def events_append(self, event):
        self.events_is_empty = False
        self._events.append(event)
        if len(self._events) > 19:
            #logger.info(u'Сольём очередь бот Vint')
            self.events_free()

    def events_free(self):
        self.events_is_empty = True
        if self._events != []:self._get_events_sender().send_game_events(self._events)
        self._events = []
        
    def load_friend_isle(self, friend, isle):
        self._get_game().load_friend = True
        self._get_game_state().set_game_loc_was = False
        self._get_events_sender().send_game_events([{"action":"gameState","locationId":isle,"user":str(friend),"objId":None,"type":"gameState"}])
        time.sleep(0.2)
        self._get_game().handle_all_events()
        _first = True
        while not self._get_game_state().set_game_loc_was:
            if _first:
                print u'Ждём загрузки острова',
                _first = False
            print u'\b.',
            self._get_events_sender().send_game_events([])
            self._get_game().handle_all_events()
            time.sleep(0.2)
        print u'\b.'
        self._get_game().load_friend = False

    def go_home(self, color_print, isle_go):  # возвращаемся домой
        if color_print:
            self.cprint(u'13       Возвращаемся домой       ')
        else:
            logger.info(u'       Возвращаемся домой       ')
        self._get_game_state().set_game_loc_was = False
        self._get_events_sender().send_game_events([{
                "action":"gameState",
                "locationId":isle_go,
                "type":"gameState"
                }])
        time.sleep(0.2)
        self._get_game().handle_all_events()
        _first = True
        while not self._get_game_state().set_game_loc_was:
            if _first:
                print u'Ждём возвращения домой',
                _first = False
            print u'\b.',
            self._get_events_sender().send_game_events([])
            self._get_game().handle_all_events()
            time.sleep(0.2)
        print u'\b.'
        time.sleep(3)
        self._get_game().handle_all_events()

    def myid_in_list(self, object, rem_, fid):
        for _usr in obj2dict(rem_):
            if int(fid) == int(_usr['user']) and int(object.id) == int(_usr['treeId']):
                return True
        return False

    def myid_in_list2(self, object, rem_, fid):
        for _usr in obj2dict(rem_):
            if int(fid) == int(_usr['user']):
                return True
        return False        

    def fid_in_list(self, fid, list):
        for user in obj2dict(list):
            if str(fid) == user['user']:
                return True
        return False

    def response_wait(self, types=[]):
        for i in range(25): # сколько итераций ждём нужного ответа
            self._get_game().handle_all_events()
            if types:
                for type in types:
                    if type in self._get_game().res_types:
                        return type
            self._get_events_sender().send_game_events([])
            time.sleep(0.2)
            #print u'Ждём:', types
        return False

    def console_log(self,curuser,userdig,global_lopat):  # консоль
        end_rFFT = len(self._get_game_state().get_state().remoteFertilizeFruitTree)
        end_rMP = len(self._get_game_state().get_state().remoteMonsterPit)
        end_rNY = len(self._get_game_state().get_state().remoteNewYear)
        end_rT = len(self._get_game_state().get_state().remoteThanksgiving)
        # remoteThanksgiving - самолёт
        # remoteTrickTreating - шатёр
        # remoteThanksgiving - корзинка пасхальная

        # str(self.air_num)+'/'+str(end_rT)
        # str(end_rFFT- self.st_rFFT)+'/'+str(end_rFFT)
        # str(end_rMP - self.st_rMP)+'/'+str(end_rMP)
        # str(end_rNY - self.st_rNY)+'/'+str(end_rNY)
        # str(global_lopat)+'/'+str(self.shovel_extra - global_lopat) 
        # копали userdig, '    юзеров'
        os.system((u'title '+curuser+u' Дерев: '+str(end_rFFT-self.st_rFFT)+'/'+str(end_rFFT)+u'   Миша: '+str(end_rMP - self.st_rMP)+'/'+str(end_rMP)+u'  Ёлки: '+str(end_rNY - self.st_rNY)+'/'+str(end_rNY)+u'  ЮзКоп: '+str(userdig)+u'  Лопат: '+str(global_lopat)+'/'+str(self.shovel_extra - global_lopat)).encode('cp1251', 'ignore'))
        #os.system((u'title '+u'Корз: '+str(self.air_num)+'/'+str(end_rT)+u'  Дерев: '+str(end_rFFT-self.st_rFFT)+'/'+str(end_rFFT)+u'   Миша: '+str(end_rMP - self.st_rMP)+'/'+str(end_rMP)+u'  Ёлки: '+str(end_rNY - self.st_rNY)+'/'+str(end_rNY)+u'  ЮзКоп: '+str(userdig)+u'  Лопат: '+str(global_lopat)+'/'+str(self.shovel_extra - global_lopat)).encode('cp1251', 'ignore'))
        #os.system((u'title '+u'Air: '+str(self.air_num)+'/'+str(end_rT)+u'  Дерев: '+str(end_rFFT-self.st_rFFT)+'/'+str(end_rFFT)+u'   Миша: '+str(end_rMP - self.st_rMP)+'/'+str(end_rMP)+u'  Ёлки: '+str(end_rNY - self.st_rNY)+'/'+str(end_rNY)+u'  ЮзКоп: '+str(userdig)+u'  Лопат: '+str(global_lopat)+'/'+str(self.shovel_extra - global_lopat)).encode('cp1251', 'ignore'))
        pass

