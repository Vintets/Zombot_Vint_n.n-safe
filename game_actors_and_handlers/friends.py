# -*- coding: utf-8 -*-
import sys
import logging
import  random  as  random_number
from game_state.game_types import GamePickPickup
from game_state.game_types import GameWoodGrave, GameWoodGraveDouble,\
    GamePickItem, GameWoodTree, GameGainItem, GamePickup, GameDigItem
from game_state.game_event import dict2obj, obj2dict
from game_state.base import BaseActor
import time
# import os.path
import os
##############################
from ctypes import windll
import sys
import re
import simplejson
 
stdout_handle = windll.kernel32.GetStdHandle(-11)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
##############################

logger = logging.getLogger(__name__)
 
 
class VisitingUsers(BaseActor): # author Vint, Loconaft, and other

    def opt(self, option): # что делаем
        options = self.mega().friends_options()['что делаем']
        return option in options

    def perform_action(self):
        if self.if_location_pirate(): return

        # настройки
        self.par = par = self.mega().friends_options()['параметры']
        color_print = par.get('color_print',False)
        friends_file = par.get('friends_file','')
        # legal_friends = par.get('legal_friends',False) # в методе
        level_down = par.get('level_down',False)
        sort_green = par.get('sort_green',False)
        shovels = par.get('shovels',300)
        shovels_chu_u = par.get('shovels_chu_u',300) 
        max_monster = par.get('max_monster',99)
        con_user = par.get('con_user',150)
        passing_number = par.get('passing_number',0)
        only_first = par.get('only_first',False)

        circle_dig = par.get('circle_dig',False)
        period_between = par.get('period_between',1440) # в минутах
        returned_main = par.get('returned_main',False)
        free_list = par.get('free_list',False)

        bot = par.get('bot',False)
        conifer_file = par.get('conifer_file',False)
        perron_file = par.get('perron_file',False)
        only_con_file = par.get('only_con_file',False)

        new_friends = par.get('new_friends',False)
        only_file_perron = par.get('only_file_perron',False)
        airplane_list = par.get('airplane_list',False)


        # что копаем:
        favdecors = []
        favdecors_list = self.mega().friends_options()['что копаем']
        for f in favdecors_list:
            favdecors.extend(f)

        # author Vint, Loconaft, and other
        #----------------------------------------------------------------------------------------------------


        # 'only_con_file':True,   # как прошли conifer_user.txt, другим не стучать


        curuser = str(self._get_game_state().get_curuser())
        self.myid = self._get_game_state().get_my_id()
        isle = 'main'
        per = ['D_PLATFORM', 'D_PLATFORM2', 'D_BOOT_SEREBRO']
        self.get_stat_pirate()
        conifer_user_len = 0

        if not os.path.isdir('statistics\\'+curuser+'\\copatel'): os.makedirs('statistics\\'+curuser+'\\copatel')
        fol_cur = 'statistics\\'+curuser # короткое имя папки юзера
        fol_cop = 'statistics\\'+curuser+'\\copatel'
        cfname = fol_cop+'\\countfnyt.txt' # задаём короткое имя пути к countfnyt.txt
        loname = fol_cop+'\\loaduser.txt'  # задаём короткое имя пути к loaduser.txt
        badname = fol_cop+'\\badname.txt'  # задаём короткое имя пути к badname.txt
        badusername = fol_cur+'\\baduser.txt'
        
        # читаем файл-счётчик
        countfnyt = self.read_countfnyt(circle_dig, period_between, cfname, loname, badname)

        if hasattr(self._get_game_state(), 'all_visited') and self._get_game_state().all_visited:
            return # всех друзей прошли уже

        friends, err = self.read_frends(friends_file)  # читаем список друзей
        if err: return

        self.antilag(1)  # антилаг загрузки, сек
        players_info, len_playersInfo = self.get_players_info(color_print)  # читаем players_info

        # Сортируем список друзей по уровню
        if level_down:
            friends = self.sort_level(color_print,players_info,friends)

        # friends = [''] 
        # 3689309721258149862 inbox, 3689309721258148238  bk  '13993154113567016316'  ТЕСТЫ!
        if friends == None or len(friends) == 0: return

        self.read_friends_del(fol_cur)                                          # читаем список нелегальных (удалённых)
        baduser = self.load_file(badusername)                                   # читаем файл baduser.txt
        white_list = self.load_file(fol_cur+'\\white_list.txt')                 # читаем файл white_list
        self.error_previous(baduser, loname, badname, badusername, white_list)  # сбой прошлой загрузки

        if new_friends:  # ходить только по новым друзьям
            friends_t, _temp = self.dop_fr_file(fol_cur, 'stable_user.txt')
            stable = friends_t
            if friends_t:
                friends = self.newFriends(friends_t)
                sort_green = False
                if os.path.isfile(cfname):
                    os.remove(cfname)
        elif airplane_list:  # ходить только по списку airplane
            friends_t, _temp = self.dop_fr_file(fol_cur, 'airplane_user.txt') # 'airplane_user.txt'  'circus_user.txt'
            if friends_t:
                airplane_user = friends_t
                friends = friends_t
                sort_green = False
                if os.path.isfile(cfname):
                    os.remove(cfname)
        elif only_file_perron:  # ходить только по списку с перронами
            print u'Грузим перроны'
            friends_t, perron_user_len = self.dop_fr_file(fol_cur, 'perron.txt')
            if friends_t:
                perron = friends_t
                friends = friends_t
                favdecors = per
                if os.path.isfile(cfname):
                    os.remove(cfname)
        elif conifer_file or perron_file or bot:  # добавлять в начало список conifer и/или perron и/иди Чудо Юдо
            if conifer_file:
                friends_t, conifer_user_len = self.dop_fr_file(fol_cur, 'conifer_user.txt')
                friends = self.filter_frends(friends, friends_t)  # убираем из frends friends_t
                friends = friends_t + friends
                part_conifer = False
            if perron_file:
                friends_t, perron_user_len = self.dop_fr_file(fol_cur, 'perron.txt')
                perron = friends_t
                friends = self.filter_frends(friends, friends_t)  # убираем из frends friends_t
                friends = friends_t + friends
            if bot:
                friends = ['[BOT]friend1','[BOT]friend2'] + friends

        if passing_number and countfnyt >= passing_number: # ограничиваем по числу
            return
        need_visit = len(friends) - countfnyt
        if need_visit <= 0: # всех друзей прошли уже
            self._get_game_state().all_visited = True
            return

        self.write_log(u'\tМы в копателе')
        if self.mega().err_log():
            self.write_gameSTATE(self._get_game_state().get_state())    # вывод в файлы gameSTATE и gameSTATE_R

        userdig = 0
        global_lopat = 0
        self.air_num = 0
        cakelimit = False
        all_cake = False
        self._events = []
        state_min = [int(time.time()/60)]
        self.shovel_extra = self._get_game_state().count_in_storage('@SHOVEL_EXTRA')
        self.statistics_start(color_print)

        if returned_main:
            island_sailing =  'main'
        else:
            island_sailing =  self.location_id()

        # читаем файл perron.txt
        if not (only_file_perron or perron_file):
            perron = self.load_file(fol_cur+'\\perron.txt')
        # читаем список ответных стуков (самолёта, шатра, корзинок)
        if not airplane_list or\
                (self.opt('airplane') or self.opt('tower') or self.opt('korzina') or self.opt('thanksgiving')):
            airplane_user = self.load_file(fol_cur+'\\airplane_user.txt')
        # читаем список ответных стуков ёлок
        # if not conifer_file:
        conifer_user = self.load_file(fol_cur+'\\conifer_user.txt')


# основной цикл обхода друзей
        for n_v in xrange(need_visit):
            if hasattr(self._get_game_state(), 'playersInfo') and len_playersInfo != len(self._get_game_state().playersInfo):
                players_info = self._get_game_state().playersInfo
                add_playersInfo = len(players_info) - len_playersInfo
                len_playersInfo = len(players_info)
                if color_print:
                    self.cprint(u'4Произошло обновление players_info')
                else: logger.info(u'Произошло обновление players_info')
                print u'Длина playersInfo изменилась на %d' % add_playersInfo

            n_v += countfnyt
            if passing_number and n_v >= passing_number: # ограничиваем по числу
                break

            fid = str(friends[n_v])
            if new_friends:
                if (n_v % 50) == 0:
                    with open(fol_cur+'\\stable_user.txt', 'w') as f:
                        f.write(str(stable))
                stable.append(str(fid))
            if (str(fid) in baduser) and (not str(fid) in white_list):
                print ' '
                if color_print:
                    self.cprint(u'4Пропускаем сбойного юзера^14_%s^15_%d' %(fid, n_v+1))
                else: logger.info(u'Пропускаем сбойного юзера %s $d' % (fid, n_v+1))
                self.inc_counter(cfname, n_v)  # увеличим счётчик
                continue

            metka = 0
            if bot: metka += 2
            if perron_file: metka += perron_user_len

            # консоль
            self.console_log(curuser,userdig,global_lopat)

            # проверяем зелёный ли друг
            if sort_green and hasattr(self._get_game_state(), 'playersInfo'):
                if not (conifer_file and n_v >= metka and n_v < (metka + conifer_user_len)):
                    load = False
                    for info in players_info:
                        if str(info.id) == str(fid):
                            load = True
                            break
                    if load and not info.liteGameState.haveTreasure:
                        #print u'У друга всё выкопано!'
                        self.inc_counter(cfname, n_v)  # увеличим счётчик
                        continue

            # проверяем если прошли список ёлок стучать без списка или нет
            if not (only_con_file and conifer_file and n_v < (metka + conifer_user_len)):
                all_cake = True

            # проверяем забанен ли друг
            if hasattr(self._get_game_state(), 'playersInfo'):
                load = False
                for info in players_info:
                    if str(info.id) == str(fid):
                        load = True
                        break
                if load and info.banned:
                    #print u'Друг в бане!'
                    self.inc_counter(cfname, n_v)  # увеличим счётчик
                    continue

            name_user = self.name_user(fid)

            num_u = str(fid).ljust(20, " ")
            sp_n = u' '*(14-len(name_user))
            print ' '
            if color_print:
                self.cprint(u'9##### Идем к другу^14_'+num_u+u'^3'+name_user+sp_n+u'^15_%d/%d^9на^3_%s^9#####'%((n_v+1), len(friends), isle))
                #self.cprint(u'9######### Идем к другу^14_%s^15_%d/%d^9на^3_%s^9#########'%(fid, (n_v+1), len(friends), isle))
            else:
                logger.info(u'##### Идем к другу '+num_u+u' '+name_user+sp_n+u'%d/%d на %s #####'%((n_v+1), len(friends), isle))
                #logger.info(u'Идём к другу "%s" на "%s", %d/%d' % (fid, isle, (n_v+1), len(friends)))
            self._get_game_state().planeAvailable = True
            self.load_friend_isle(fid, isle, loname, badname)
            
            UserIsAway = self._get_game_state().get_state().isAway
            if UserIsAway: # True
                print u' ',
                self.cprint(u'71Друг давно не был в игре!!!')
           
            self.actions_list = {} # эвент хранилище
            self.actions_info = {} # эвент описания
            guardGrave = 0         # наличие сторожа
            objssvl = {}           # что копать
            countnyt = 0
            haveRemoteFertilizeFruit = True
            haveRemoteValentineTower = True
            
            if self._get_game_state().get_state().haveTreasure:
                alldigged = False
            else:
                alldigged = True
                logger.info(u'Здесь всё выкопано...')
                
            if fid in conifer_user:
                cone_len = cone_user = conifer_user.count(fid)
                if cone_user > con_user: cone_user = con_user
                #cone_len = conifer_user.count(fid)
                if cone_len > cone_user:
                    for i in range(cone_len-cone_user):
                       conifer_user.remove(fid)
                    # with open(fol_cur+'\\conifer_user.txt', 'w') as f:
                        # f.write(str(conifer_user))
                    pass
            else: cone_user = con_user

            for object in self._get_game_location().get_game_objects():
                #open(str(fid)+'_objects.txt', 'a').write(str(obj2dict(object))+"\n")

                if object.type == 'guardGrave':
                    logger.info(u'------------ Сторож !!! ------------')
                    guardGrave = 1

                # Пополняем списки
                if object.item.lstrip('@') in per:
                    if isle == 'main' and (str(fid) not in perron):
                        perron.append(str(fid))
                        with open(fol_cur+'\\perron.txt', 'w') as f:
                           f.write(str(perron))

                # разбивать тайники
                if object.type == 'friendTransformObject':
                    if self.opt('split_caches'):
                        if object.transformed:continue
                        name = self._get_item_reader().get(object.item).name
                        eventtrans = {"action":"remoteFriendTransform","type":"item","objId":object.id}
                        self._get_events_sender().send_game_events([eventtrans])
                        self.cprint(u'5Разбил %s' % name.upper())
                    continue
                # haveThanksgivingAttempt = True   # новый параметр. Есть попытки ответного стука????

                ##### Стучим в Хеллоуинские постройки #####
                #блок кода
                ##### Стучим в Валентиновые постройки #####
                #блок кода

                # Стучим в Разные постройки
                if object.type == 'thanksgivingTable':
                    if self.opt('thanksgiving'):
                        if airplane_user == []:
                            if not free_list: continue
                        else:
                            if fid not in airplane_user: continue

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
                            if airplane_user != []:
                                airplane_user.remove(fid)
                                with open(fol_cur+'\\airplane_user.txt', 'w') as f:
                                    f.write(str(airplane_user))
                            self._get_events_sender().send_game_events([eventtrans])
                            apend_frend = {u'count': 0L, u'date': u'-19849562', u'user': str(fid)}
                            self._get_game_state().get_state().remoteThanksgiving.append(dict2obj(apend_frend))
                            self.cprint(u'5%s в %s' % (readerGifts.name,reader_thanks.name))
                            self._get_game_state().planeAvailable = False
                            self.air_num += 1
                    continue


                """
                # Стучим в самолёт
                if object.item == '@B_HOCKEY_AIRPLANE':
                    if self.opt('airplane'):
                        if airplane_user == []:
                            if not free_list: continue
                        else:
                            if fid not in airplane_user: continue
                        
                        re_ = self._get_game_state().get_state().remoteThanksgiving
                        if self._get_game_state().planeAvailable and object.usedPlatesCount < 5 and len(re_) < 100: # len(object.users) < 5
                            #print 'remoteThanksgiving', str(obj2dict(re_))
                            if len(re_) > 0:
                                if self.myid_in_list2(object, re_, fid):
                                    if color_print:
                                        self.cprint(u'4Сегодня мы уже стукнули в этот самолёт')
                                    else:
                                        logger.info(u'Сегодня мы уже стукнули в этот самолёт')
                                    self._get_game_state().planeAvailable = False
                                    continue
                            self.cprint(u'5Кладем билет в самолет')
                            if airplane_user != []:
                                airplane_user.remove(fid)
                                with open(fol_cur+'\\airplane_user.txt', 'w') as f:
                                    f.write(str(airplane_user))
                            self._get_game_state().get_state().remoteThanksgiving.append({u'treeId':object.id, u'user':fid})
                            self._get_events_sender().send_game_events([
                                {"itemId": "HOCKEY_BOX_01", "action": "remoteThanksgiving", "type": "item", "objId": object.id}])
                            self._get_game_state().planeAvailable = False
                            self.air_num += 1
                    continue

                # Стучим в шатёр
                if object.item == '@B_TENT_CIRCUS':
                    if self.opt('airplane'):
                        if airplane_user == []:
                            if not free_list: continue
                        else:
                            if fid not in airplane_user: continue
                        
                        re_ = self._get_game_state().get_state().remoteTrickTreating
                        if self._get_game_state().planeAvailable and len(re_) < 100:
                            if len(re_) > 0:
                                if self.myid_in_list2(object, re_, fid):
                                    if color_print:
                                        self.cprint(u'4Сегодня мы уже стукнули в этот шатёр')
                                    else:
                                        logger.info(u'Сегодня мы уже стукнули в этот шатёр')
                                    self._get_game_state().planeAvailable = False
                                    continue
                            self.cprint(u'5Стучим в шатёр')
                            if airplane_user != []:
                                airplane_user.remove(fid)
                                with open(fol_cur+'\\circus_user.txt', 'w') as f:
                                    f.write(str(airplane_user))
                            self._get_game_state().get_state().remoteTrickTreating.append(dict2obj({u'user':fid}))
                            self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","itemId":"BOW_PACK_DEFAULT","action":"remoteTrickTreating"}])
                            self._get_game_state().planeAvailable = False
                            self.air_num += 1
                    continue

                # Стучим в шатёр2
                if object.item == '@B_TENT_CIRCUS':
                    if self.opt('airplane'):
                        re_ = self._get_game_state().get_state().remoteTrickTreating
                        mm = False
                        for i in re_:
                            if int(fid) == int(i.user):
                                logger.info(u'Сегодня мы уже стукнули этому другу')
                                mm = True
                                break
                        if mm: continue
                        if len(re_) < 100:
                            logger.info(u'Стучим в шатёр')
                            self._get_game_state().get_state().remoteTrickTreating.append(dict2obj({u'user':fid}))
                            self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","itemId":"BOW_PACK_DEFAULT","action":"remoteTrickTreating"}])
                    continue
                """

                """
                # Стучим в мавзолей
                if object.item == '@B_MAUSOLEUM':
                    if self.opt('airplane'):
                        if airplane_user == []:
                            if not free_list: continue
                        else:
                            if fid not in airplane_user: continue
                        
                        re_ = self._get_game_state().get_state().remoteTrickTreating
                        if self._get_game_state().planeAvailable and len(re_) < 100:
                            if len(re_) > 0:
                                if self.myid_in_list2(object, re_, fid):
                                    if color_print:
                                        self.cprint(u'4Сегодня мы уже стукнули этому другу')
                                    else:
                                        logger.info(u'Сегодня мы уже стукнули этому другу')
                                    self._get_game_state().planeAvailable = False
                                    continue
                            self.cprint(u'5Стучим в Мавзолей')
                            if airplane_user != []:
                                airplane_user.remove(fid)
                                with open(fol_cur+'\\airplane_user.txt', 'w') as f:
                                    f.write(str(airplane_user))
                            self._get_game_state().get_state().remoteTrickTreating.append(dict2obj({u'user':fid}))
                            self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","itemId":"METALL_PACK_DEFAULT","action":"remoteTrickTreating"}])
                            self._get_game_state().planeAvailable = False
                            self.air_num += 1
                    continue
                """

                # Стучим в весеннее дерево
                if object.item == '@B_SAKURA':
                    if self.opt('airplane'):
                        if airplane_user == []:
                            if not free_list: continue
                        else:
                            if fid not in airplane_user: continue
                        
                        re_ = self._get_game_state().get_state().remoteTrickTreating
                        if self._get_game_state().planeAvailable and len(re_) < 100:
                            if len(re_) > 0:
                                if self.myid_in_list2(object, re_, fid):
                                    if color_print:
                                        self.cprint(u'4Сегодня мы уже стукнули этому другу в ВД')
                                    else:
                                        logger.info(u'Сегодня мы уже стукнули этому другу в ВД')
                                    self._get_game_state().planeAvailable = False
                                    continue
                            self.cprint(u'5Стучим в Весеннее дерево')
                            if airplane_user != []:
                                airplane_user.remove(fid)
                                with open(fol_cur+'\\airplane_user.txt', 'w') as f:
                                    f.write(str(airplane_user))
                            self._get_game_state().get_state().remoteTrickTreating.append(dict2obj({u'user':fid}))
                            self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","itemId":"SAKURA_PACK_DEFAULT","action":"remoteTrickTreating"}])
                            self._get_game_state().planeAvailable = False
                            self.air_num += 1
                    continue
                
                """
                # Стучим в весеннее дерево за ЗБ
                if object.item == '@B_SAKURA':
                    if self.opt('airplane'):
                        event = [{"objId":object.id,"type":"item","itemId":"SAKURA_PACK_LARGE","action":"remoteTrickTreating"}]
                        for n in range(100): # 10 раз
                            if self.cash > 10:
                                self.cprint(u'5Стучим в  Весеннее Дерево за 10 ЗБ')
                                self._get_events_sender().send_game_events(event)
                            else: break
                    continue
                """

                """
                # ver 0
                if object.item == '@B_MAUSOLEUM':
                    if self.opt('airplane'):
                        re_ = self._get_game_state().get_state().remoteTrickTreating
                        mm = False
                        for i in re_:
                            if int(fid) == int(i.user):
                                logger.info(u'Сегодня мы уже стукнули этому другу')
                                mm = True
                                break
                        if mm: continue
                        if len(re_) < 100:
                            self.cprint(u'5Стучим в шатёр')
                            self._get_game_state().get_state().remoteTrickTreating.append(dict2obj({u'user':fid}))
                            self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","itemId":"METALL_PACK_DEFAULT","action":"remoteTrickTreating"}])
                    continue
                """

                """
                # Кладем конфету в пасхальную корзинку
                if object.item == '@B_BASKETS_EASTER_2015':
                    if self.opt('korzina'):
                        if airplane_user == []:
                            if not free_list: continue
                        else:
                            if fid not in airplane_user: continue
                            
                        re_ = self._get_game_state().get_state().remoteThanksgiving
                        if self._get_game_state().planeAvailable and len(re_) < 100 and object.usedPlatesCount < 8:
                            if len(re_) > 0:
                                if self.myid_in_list2(object, re_, fid):
                                    if color_print:
                                        self.cprint(u'4Сегодня мы уже стукнули в эту корзинку')
                                    else:
                                        logger.info(u'Сегодня мы уже стукнули в эту корзинку')
                                    self._get_game_state().planeAvailable = False
                                    continue
                            self.cprint(u'5Кладем конфету в корзинку')
                            if airplane_user != []:
                                airplane_user.remove(fid)
                                with open(fol_cur+'\\airplane_user.txt', 'w') as f:
                                    f.write(str(airplane_user))
                            self._get_game_state().get_state().remoteThanksgiving.append(dict2obj({u'user':fid}))
                            self._get_events_sender().send_game_events([{"objId":object.id,"type":"item","itemId":"EASTER_BOX_1","action":"remoteThanksgiving"}])
                            self._get_game_state().planeAvailable = False
                            self.air_num += 1
                    continue
                # ответ Alert! SERVER_THANKSGIVING_NOT_ALLOW
                """

                """
                ##### Крутим рулетки у друзей #####
                if object.type == 'friendGamesBuilding':
                    reader_roll=self._get_item_reader().get(object.item)
                    if object.transformPlaysCount>=int(reader_roll.transformPlaysCount):continue
                    if hasattr(reader_roll,'upgrades'):
                        if object.level<len(reader_roll.upgrades):continue
                    if hasattr(reader_roll,'games') and reader_roll.games:
                        for game in reader_roll.games:
                            roll=True
                            needItem=game.playCost.item
                            needCount=int(game.playCost.count)
                            count_storage=self._get_game_state().count_in_storage(needItem)
                            if count_storage<needCount:continue
                            if hasattr(object,'usersNextPlaysTimes'):
                                nextPlay=obj2dict(object.usersNextPlaysTimes)
                                if nextPlay:
                                    for users in nextPlay:
                                        if users==user and not self._get_timer().has_elapsed(nextPlay[users]):roll=False
                            if not roll:continue
                            extraId=game.id
                            friendPlay={"extraId":extraId,"type":"game","action":"friendPlay","objId":object.id,"itemId":reader_roll.id}
                            self._get_events_sender().send_game_events([friendPlay])
                            print u'Крутнул рулетку в %s'%reader_roll.name
                            self._get_game_state().remove_from_storage(needItem, needCount)
                """

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
                    if fid in ['[BOT]friend1','[BOT]friend2']: continue
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
                        #open(fol_cur+'\\sunduki.txt', 'a').write(str(obj2dict(object)) + "\n")
                        self.add_action('pickupbox', {"action":"pick","type":"item","objId":object.id})
                    continue

                # Ёлки
                if object.type == 'newYearTree' and 'B_SPRUCE_' in object.item:
                    if cakelimit: continue
                    if self.opt('conifer') and countnyt < cone_user:
                        if conifer_file and conifer_user:
                            if (not all_cake) and (fid not in conifer_user): continue
                        else:
                            all_cake = True
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
                            if conifer_user != [] and fid in conifer_user:
                                conifer_user.remove(fid)
                                with open(fol_cur+'\\conifer_user.txt', 'w') as f:
                                    f.write(str(conifer_user))
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
                    # Овца овечная
                    if self.opt('valentine') and object.item == u'@CUPID_TREE':
                        l = self._get_game_state().get_state().remoteValentineCollect
                        if len(l) >= 300 or object.count <= 0: continue
                        # Проверка на повторный стук в один день
                        if len(l) > 0:
                            if self.fid_in_list(fid, l):
                                if color_print:
                                    self.cprint(u'4Сегодня мы уже стучали этому другу  В Афцу...')
                                else: logger.info(u'Сегодня мы уже стучали этому другу в Афцу...')
                                continue
                        if object.level < 8:
                            if color_print:
                                self.cprint(u'5Стучим в Афцу!')
                            else:
                                logger.info(u'Стучим в Афцу!')
                            event_valentine = {"action":"remoteValentineCollect","type":"item","objId":object.id}
                            self._get_events_sender().send_game_events([event_valentine])
                            addUser = {u'count': '0L', u'date': '0L', u'user':str(fid)}
                            self._get_game_state().get_state().remoteValentineCollect.append(addUser)
                        else:
                            logger.info(u'Эта Афца уже построена')

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

                    """
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
                    """

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
                    lopat = 0
                    while (self.shovel_extra - global_lopat - lopat) > 0: # цикл копки
                        # print u'копаем', objs[0].item.lstrip('@')
                        if (objs[0].item.lstrip('@') in per):
                            if lopat >= 300: break
                        elif (fid in ['[BOT]friend1','[BOT]friend2']):
                            if lopat >= shovels_chu_u: break
                        elif lopat >= shovels: break
                        lopat += 1
                        if only_first: objdig = objs[0]
                        else: objdig = random_number.choice(objs)
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

                    if lopat >= 0:
                        logger.info(u'Использовали "%d" лопат' % lopat)
                        global_lopat += lopat
                        userdig += 1
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
                logger.info(u'Начинаем отсылать '+type)

                for a in self.actions_list[type]: # Сам процесс отсылки эвентов
                    self.events_append(a)
                self.events_free()

            open(last_type_file, 'w').write(str('last_type')) # всё прошло удачно - сбросим type

            self.inc_counter(cfname, n_v)  # увеличим счётчик
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
        
        if new_friends:
            with open(fol_cur+'\\stable_user.txt', 'w') as f:
                f.write(str(stable))
            self.cprint(u'13Завершили обход всех^12_НОВЫХ^13_друзей')
        
        self.go_home(color_print, island_sailing)  # возвращаемся домой
        
        logger.info('-------------   END   ---------------')
        time.sleep(2)
        # идём на следующий круг
        return


    def inc_counter(self, cfname, n_v):  # увеличим счётчик
        with open(cfname, 'w') as f:
            f.write(str(n_v + 1))

    def filter_frends(self, friends, friends_t):
        for i in friends_t:
            try:
                friends.remove(i)
            except: pass
        return friends

    def get_players_info(self, color_print):  # читаем players_info
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
        return players_info, len_playersInfo

    def read_friends_del(self, fol_cur): # читаем список нелегальных (удалённых)
        if hasattr(self, 'friends_del'): return
        if os.path.isfile(fol_cur + '\\friends_del.txt'):
            with open(fol_cur + '\\friends_del.txt', 'r') as f:
                try:
                    self.friends_del = eval(f.read())
                except:
                    self.friends_del = []
        else: self.friends_del = []

    def load_file(self, name):  # читаем файл .txt
        if os.path.isfile(name):
            with open(name, 'r') as f:
                try:
                    data = eval(f.read())
                    return data
                except: pass
        return []

    def get_stat_pirate(self):  # читаем пиратский статус
        if hasattr(self._get_game_state().get_state().pirate,'state'):
            return self._get_game_state().get_state().pirate.state
        else:
            setattr(self._get_game_state().get_state().pirate, 'state', 'RETURNED')

    def read_frends(self, friends_file):  # читаем список друзей
        if friends_file:
            if os.path.isfile(friends_file):
                with open(friends_file, 'r') as f:
                    data = f.read()
                try:
                    friends = eval(data)
                except:
                    self.cprint(u'12Файл с друзьями %s имеет неверный формат' % friends_file)
                    logger.info('-------------------------------------')
                    return [], True
            else:
                self.cprint(u'12Друзья из файла %s не грузятся' % friends_file)
                logger.info('-------------------------------------')
                return [], True
        else:
            friends = self.get_friendsid()
        return friends, False

    def dop_fr_file(self, fol_cur, name_file): # читаем доп списки или список перронов онли
        if os.path.isfile(fol_cur + '\\' + name_file):
            with open(fol_cur + '\\' + name_file, 'r') as f:
                data = f.read()
            try:
                friends_t = eval(data)
                friends_t = list(set(friends_t))
                friends_t, state = self.legal(friends_t,fol_cur)
                _user_len = len(friends_t)
                # if state:
                    # with open(fol_cur + '\\' + name_file, 'w') as f:
                        # f.write(str(friends_t))
                return friends_t, _user_len
            except:
                self.cprint(u'12У списка %s неверный формат' % name_file)
            friends_t, state = self.legal(friends_t,fol_cur)
        self.cprint(u'12Нет списка %s' % name_file)
        # logger.info('-------------------------------------')
        return [], 0

    def read_countfnyt(self, circle_dig, period_between, cfname, loname, badname):  # читаем файл-счётчик
        if os.path.isfile(cfname):  # это проходит проверка на устарелость вайла счетчика.
            time_file = os.path.getmtime(cfname)
            ftime = time.strftime('%Y:%m:%d', time.localtime(time_file))
            cur_time = time.strftime('%Y:%m:%d', time.localtime(time.time()))
            # print 'ftime', ftime
            # print 'cur_time', cur_time
            # новый день
            if (ftime != cur_time) or\
                    (circle_dig and (time.time() - time_file) >= period_between*60):  # вышел период
                self.remove_files(cfname, loname, badname)  # чистим файлы
                self._get_game_state().all_visited = False
            else:
                with open(cfname, 'r') as f:
                    countfnyt = int(f.read())
                return countfnyt
        countfnyt = 0
        with open(cfname, 'w') as f:
            f.write(str(countfnyt))
        return countfnyt

    def remove_files(self, cfname, loname, badname):  # чистим файлы
        if os.path.isfile(cfname):
            os.remove(cfname)
        if os.path.isfile(loname):
            os.remove(loname)
        if os.path.isfile(badname):
            os.remove(badname)

    def error_previous(self, baduser, loname, badname, badusername, white_list):  # сбой прошлой загрузки
        if os.path.isfile(loname) and open(loname).read() == 'False':
            if os.path.isfile(badname):
                with open(badname, 'r') as f:
                    bad = str(f.read())
                if bad and (bad not in white_list):
                    with open(badusername, 'w') as f:
                        baduser.append(str(bad))
                        f.write(str(baduser)) # запишем сбойного юзера
            with open(loname, 'w') as f:
                f.write('True')
        if os.path.isfile(badname):  # подтираем файлы
            os.remove(badname)

    def new_baduser(self, badusername):
        with open(badusername, 'w') as f:
            f.write(str([]))
        return []

    def name_user(self, fid):  # имя друга
        name_user = u'--------------'
        if hasattr(self._get_game_state(), 'friends_names') and self._get_game_state().friends_names.get(str(fid)) and self._get_game_state().friends_names.get(str(fid)) != u'Без имени':
            name_user = u"'" + self._get_game_state().friends_names.get(str(fid)) + u"'"
            #name_user = name_user.replace(u'\u0456', u'i').encode("cp866", "ignore")
        return name_user

    def sort_level(self, color_print,players_info,friends):  # cортируем список друзей по уровню
        if players_info:
            fr_dict = {str(info.id) : info.level for info in players_info}
            fr_dict2 = {}
            for fr in friends:
                try:
                    level = fr_dict[str(fr)]
                except:
                    level = 0
                fr_dict2[str(fr)] = level
            # print u'длина playersInfo', len(fr_dict)
            # print u'длина friends    ', len(fr_dict2)
            friends_order = fr_dict2.items()
            friends_order.sort(key=lambda x: x[::-1], reverse=True)
            friends = [fr[0] for fr in friends_order]
        else:
            if color_print:
                self.cprint(u'4Не можем отсортировать по уровню, инфа о друзьях не получена.')
            else:
                logger.info(u'Не можем отсортировать по уровню, инфа о друзьях не получена.')
        return friends

    def antilag(self, time_wait):  # антилаг загрузки
        time.sleep(time_wait)
        self._get_game().handle_all_events()

    def statistics_start(self, color_print):
        self.st_rFFT = len(self._get_game_state().get_state().remoteFertilizeFruitTree)
        self.st_rMP = len(self._get_game_state().get_state().remoteMonsterPit)
        self.st_rNY = len(self._get_game_state().get_state().remoteNewYear)
        # self.st_rVT = len(self._get_game_state().get_state().remoteValentineCollect)
        # self.st_rT = len(self._get_game_state().get_state().remoteTrickTreating)
        # self.st_rT = len(self._get_game_state().get_state().remoteThanksgiving)
        # remoteThanksgiving - самолёт
        # remoteTrickTreating - шатёр
        # remoteThanksgiving - корзинка пасхальная
        print ' '
        self.cprint(u'9---  Start  ---')
        if color_print:
            self.cprint (u'9Сегодня полито деревьев:   ^15_%s' % (self.st_rFFT))
            self.cprint (u'9Сегодня закопано медведей: ^15_%s' % (self.st_rMP))
            self.cprint (u'9Застукано ёлок:            ^15_%s' % (self.st_rNY))
            # self.cprint (u'9Стукнуто Деревьев Страсти: ^15_%s' % (self.st_rVT))
            # self.cprint (u'9Стукнуто корзинок:         ^15_%s' % (self.st_rT))
            # self.cprint (u'9Стукнуто шатров:           ^15_%s' % (self.st_rT))
            #self.cprint (u'9Стукнуто самолётов:        ^15_%s' % (self.st_rT))
            self.cprint (u'9У нас есть золотых лопат:  ^15_%s' % (self.shovel_extra))
        else:
            print u'Сегодня полито деревьев:   ', self.st_rFFT
            print u'Сегодня закопано медведей: ', self.st_rMP
            print u'Застукано ёлок:            ', self.st_rNY
            # print u'Стукнуто корзинок:         ', self.st_rT
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
        # end_rT = len(self._get_game_state().get_state().remoteTrickTreating)
        # end_rT = len(self._get_game_state().get_state().remoteThanksgiving)
        # remoteTrickTreating - шатёр
        # remoteThanksgiving - корзинка пасхальная
        # remoteThanksgiving - самолёт
        end_rVT = len(self._get_game_state().get_state().remoteValentineCollect)
        percent_userdig = round(userdig/(len_friends/float(100)), 1)
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
            # self.cprint (u'9Деревьев Страсти:  ^15_%s/%d' % (end_rVT - self.st_rVT, end_rVT))
            # self.cprint (u'9Стук в корзинки:   ^15_%s/%d' % (self.air_num, end_rT))
            # self.cprint (u'9Стук в шатры:      ^15_%s/%d' % (self.air_num, end_rT))
            # self.cprint (u'9Стук в самолёты:   ^15_%s/%d' % (self.air_num, end_rT))
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

    def newFriends(self, friends):
        friends_legal = self.get_friendsid() # действующие друзья
        #state = False
        new = []
        for idf in friends_legal:
            if friends.count(str(idf)) == 0 and friends.count(int(idf)) == 0:
                new.append(str(idf))
        return new

    def legal(self, friends, fol_cur):  # фильтр легальных
        state = False
        legal_friends = self.par.get('legal_friends',False)
        if not legal_friends: return friends, state
        friends_legal = self.get_friendsid() # действующие друзья
        del_f = []
        for idf in friends:
            if friends_legal.count(str(idf)) == 0 and friends_legal.count(int(idf)) == 0:
                del_f.append(str(idf))
                for n in range(friends.count(idf)):
                    friends.remove(idf)
        if del_f:
            state = True
            sav = False
            for id in del_f:
                if id not in self.friends_del:
                    self.friends_del.append(id)
                    sav = True
            if sav:
                with open(fol_cur+'\\friends_del.txt', 'w') as f:
                    f.write(str(list(set(self.friends_del))))
        return friends, state

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

    def load_friend_isle(self, friend, isle, loname, badname):
        self._get_game().load_friend = True
        with open(loname, 'w') as f:
            f.write('False')
        with open(badname, 'w') as f:
            f.write(str(friend))
        self._get_game_state().set_game_loc_was = False
        self._get_events_sender().send_game_events([{"action":"gameState","locationId":isle,"user":str(friend),"objId":None,"type":"gameState"}])
        time.sleep(0.5)
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
        with open(loname, 'w') as f:
            f.write('True')

    def go_home(self, color_print, island_sailing):  # возвращаемся домой
        self.pick_pickups()
        self.write_log(u'\tВозвращаемся ИЗ КОПАТЕЛЯ')
        if color_print:
            self.cprint(u'13       Возвращаемся домой       ')
        else:
            logger.info(u'       Возвращаемся домой       ')
        self._get_game_state().set_game_loc_was = False
        self._get_events_sender().send_game_events([{
                "action":"gameState",
                "locationId":island_sailing,
                "type":"gameState"
                }])
        time.sleep(0.5)
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

    def pick_pickups(self):
        self._get_game().handle_all_events()
        pickups = self._get_game_location().get_pickups()
        if not pickups: return
        logger.info(u'Подбираем дроп...')
        all_pick = []
        for pickup in pickups:
            pick_event = GamePickPickup([pickup])
            all_pick += [pick_event]
            if len(all_pick) > 99:
                self._get_events_sender().send_game_events(all_pick)
                all_pick = []

        if len(all_pick) > 0:
            self._get_events_sender().send_game_events(all_pick)

        for pickup in pickups:
            self._get_game_location().remove_pickup(pickup)
        time.sleep(1)
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
        end_rT = len(self._get_game_state().get_state().remoteTrickTreating)
        # end_rT = len(self._get_game_state().get_state().remoteThanksgiving
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

    def printInfo(self,fol_cur):
        getInfo = self._get_game_state().playersInfo
        #print obj2dict(getInfo)
        #print dir(getInfo)
        #print players    
        for n in getInfo:  # .players
            print u'name            ', n.name
            print u'id              ', n.id
            print u'level           ', n.level
            print u'exp             ', n.exp
            print u'accessDate      ', n.accessDate
            print u'playerStatus    ', n.playerStatus
            print u'banned          ', n.banned
            print u'buried          ', n.buried            
            #print u'liteGameState', n.liteGameState
            print u'Хотелка wishlist', n.liteGameState.wishlist
            print u'userName        ', n.liteGameState.playerSettings.userName
            print u'haveTreasure    ', n.liteGameState.haveTreasure
            print
        #open(fol_cur+'\\getInfo.txt', 'a').write(str(getInfo)+"\n".encode('utf-8'))


"""
SERVER_PICKUPBOX_STOLEN   возможно сундук вскрыт
SERVER_TREASURE_FOUND - секретный клад
"""
