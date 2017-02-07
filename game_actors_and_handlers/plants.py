# coding=utf-8
import logging
import time
import os
import ConfigParser
from game_state.game_types import GamePlant, GameFruitTree, GameSlag,\
    GameDigItem, GamePickItem, GameBuyItem, GameSellItem, GameUseStorageItem, GameFertilizeTree
from game_state.item_reader import LogicalItemReader
from game_state.base import BaseActor
from game_state.game_event import dict2obj, obj2dict


logger = logging.getLogger(__name__)

class FertilBot(BaseActor):

    def perform_action(self):
        if self.if_location_pirate(): return
        location = self._get_game_state().get_location_id()
        if location == 'un_02' or location == u'isle_light': return
        _locs = self.mega().fertil_tree_options()['locations']
        if _locs and (location not in _locs): return
        rezerv = self.mega().fertil_tree_options()['rezerv_RED_TREE_fertilizer']
        tree = self.mega().fertil_tree_options()['tree']
        print u'мы в удобрялке'
        for tr in range(len(tree)):
            tree[tr] = '@' + tree[tr].lstrip('@')
        fertil = '@RED_TREE_FERTILIZER'
        fertil_count = self._get_game_state().count_in_storage(fertil)
        if (fertil_count == None) or (fertil_count == 0) or (fertil_count - rezerv) < 1:
            # logger.info(u'Нет удобрений для деревьев')
            return
        logger.info(u'Имеется удобрений для деревьев %d'%(fertil_count))
        fertil_count -= rezerv
        fl_count = fertil_count
        harvestItems = self._get_game_location().get_all_objects_by_type(GameFruitTree.type)
        fert_all = []
        for harvestItem in harvestItems:
            if tree and (harvestItem.item not in tree): continue
            if not self._get_timer().has_elapsed(harvestItem.jobFinishTime):
                if not harvestItem.fertilized:
                    if harvestItem.type == GameFruitTree.type:
                        if fl_count > 0:
                            fert_event = GameFertilizeTree(itemId = unicode(fertil[1:]), objId = harvestItem.id)
                            harvestItem.jobFinishTime = 0 # self._get_timer()._get_current_client_time()
                            harvestItem.fertilized = True
                            fert_all += [fert_event]
                            fl_count -= 1

        if len(fert_all) > 0:
            self._get_events_sender().send_game_events(fert_all)
            logger.info(u'Удобрено %d деревьев' % (fertil_count-fl_count))
            self._get_game_state().remove_from_storage(fertil,fertil_count-fl_count)

        #{"type":"item","itemId":"RED_TREE_FERTILIZER","action":"fertilize","objId":20088}
        pass


class FertilPlantBot(BaseActor):

    def perform_action(self):
        if self.if_location_pirate(): return
        location = self._get_game_state().get_location_id()
        if location == 'un_02' or location == u'isle_light': return
        _locs = self.mega().fertil_options()['locations']
        if _locs and (location not in _locs): return
        rezerv = self.mega().fertil_options()['rezerv_RED_fertilizer']
        plants = self.mega().fertil_options()['plants']
        fertil = '@RED_FERTILIZER'
        fertil_count = self._get_game_state().count_in_storage(fertil)
        if (fertil_count == None) or (fertil_count == 0) or (fertil_count - rezerv) < 1:
            #logger.info(u'Нет красных удобрений')
            return
        logger.info(u'Имеются красные удобрения в количестве: %d' % (fertil_count))
        fertil_count -= rezerv
        fl_count = fertil_count
        harvestItems = self._get_game_location().get_all_objects_by_type(GamePlant.type)
        fert_all = []
        for harvestItem in harvestItems:
            if plants and (harvestItem.item not in plants): continue
            #logger.info(str(obj2dict(harvestItem)).encode('utf-8'))
            if not self._get_timer().has_elapsed(harvestItem.jobFinishTime):
                if not harvestItem.fertilized:
                    if harvestItem.type == GamePlant.type:
                        if fl_count > 0:
                            fert_event = GameFertilizeTree(itemId = unicode(fertil[1:]), objId = harvestItem.id)
                            harvestItem.jobFinishTime = 0  # self._get_timer()._get_current_client_time()
                            harvestItem.fertilized = True
                            fert_all += [fert_event]
                            fl_count -= 1
        if len(fert_all) > 0:
            self._get_events_sender().send_game_events(fert_all)
            logger.info(u'Удобрено %d растений на 100%%' % (fertil_count-fl_count))
            self._get_game_state().remove_from_storage(fertil, fertil_count-fl_count)

        #{"type":"item","itemId":"RED_FERTILIZER","action":"fertilize","objId":15104}
        #{u'rotate': 0L, u'fertilized': False, u'item': u'@P_27', u'jobFinishTime': u'-286129', u'jobStartTime': u'-586129', u'y': 36L, u'x': 38L, u'type':u'plant', u'id': 13358L}
        #{u'rotate': 0L, u'fertilized': True, u'item': u'@P_01', u'jobFinishTime': u'-8576', u'jobStartTime': u'-11657', u'y': 36L, u'x': 34L, u'type': u'plant', u'id': 13356L}
        #{u'rotate': 0L, u'fertilized': False, u'item': u'@P_01', u'jobFinishTime': u'290442', u'jobStartTime': u'-9558', u'y': 36L, u'x': 30L, u'type': u'plant', u'id': 6318L}
        pass


class FertilPlantGreenBot(BaseActor): #Зеленые удобрения
    
    def perform_action(self):
        if self.if_location_pirate(): return
        location = self._get_game_state().get_location_id()
        if location == 'un_02' or location == u'isle_light': return
        _locs = self.mega().fertil_options()['locations']
        if _locs and (location not in _locs): return
        rezerv = self.mega().fertil_options()['rezerv_GREEN_fertilizer']
        plants = self.mega().fertil_options()['plants']
        fertil = '@GREEN_FERTILIZER'
        fertil_count = self._get_game_state().count_in_storage(fertil)
        if (fertil_count == None) or (fertil_count == 0) or (fertil_count - rezerv) < 1:
            #logger.info(u'Нет зелёных удобрений')
            return
        logger.info(u'Имеются зелёные удобрения в количестве: %d' % (fertil_count))
        fertil_count -= rezerv
        fl_count = fertil_count
        harvestItems = self._get_game_location().get_all_objects_by_type(GamePlant.type)
        fert_all = []
        for harvestItem in harvestItems:
            if plants and (harvestItem.item not in plants): continue
            if not self._get_timer().has_elapsed(harvestItem.jobFinishTime):
                if not harvestItem.fertilized:
                    if harvestItem.type == GamePlant.type:
                        if fl_count > 0:
                            fert_event = GameFertilizeTree(itemId = unicode(fertil[1:]), objId = harvestItem.id) 
                            harvestItem.jobFinishTime = 0 # self._get_timer()._get_current_client_time()
                            harvestItem.fertilized = True
                            fert_all += [fert_event]
                            fl_count -= 1
        if len(fert_all) > 0:
            self._get_events_sender().send_game_events(fert_all)
            logger.info(u'Удобрено %d растений на 30%%' % (fertil_count-fl_count))
            self._get_game_state().remove_from_storage(fertil,fertil_count-fl_count)


class ScrollBot(BaseActor):

    def perform_action(self):
        if not self.if_location_pirate(): return
        if not hasattr(self._get_game_state(), 'wealth_roll'):
            self._get_game_state().wealth_roll = 1
            sostav = self.mega().auto_pirate_options()['sostav']
            self.curuser = str(self._get_game_state().get_curuser())
            dir = 'statistics\\_avto_pirate_' + str(sostav)
            if not os.path.isdir(dir): os.makedirs(dir)
            name_info = dir + '\\info_' + self.curuser + '.ini'
            self.init_ini(name_info)
            if self.get_roll() or (not self.get_captain()) or (not self.get_all_pirates()): return
        else: return
        col = self.mega().scroll_options()['count']
        reserv = self.mega().scroll_options()['reserv']
        use_items = ['WEALTH_ROLL'] # это свитки, можно не только их бить
        self.set_roll() 
        for use_item in use_items:
            has_items = self._get_game_state().count_in_storage('@' + use_item)
            if col > has_items - reserv: col = has_items - reserv
            if col > 0:
                logger.info(u'Бьем "%s" в количестве = %d' % (self._get_item_reader().get(use_item).name, col))
                events = []
                for j in range(col):
                    sell_event = GameUseStorageItem(itemId=unicode(use_item), y = long(10), x = long(10))
                    self._get_events_sender().send_game_events([sell_event])
                    self._get_game_state().remove_from_storage('@' + use_item,1)
                logger.info(u'Разбито %d "%s"' % (col, self._get_item_reader().get(use_item).name))
        time.sleep(1)
        # exit(0)
        pass

    def get_roll(self):
        self.set_name_section(self.curuser)
        roll = self.get_param('wealth_roll')
        if (not roll is None): return eval(roll)
        else: return False

    def set_roll(self):
        if not self.get_roll():
            self.set_param('wealth_roll','True')
            self.save()

    def get_captain(self):
        captain = self.get_param('captain')
        if (not captain is None): return eval(captain)
        else: return False

    def get_all_pirates(self):
        self.set_name_section('global_info')
        ap = self.get_param('all_pirates')
        if (not ap is None): return eval(ap)
        else: return False


class UseEggItemBot(BaseActor):

    def perform_action(self):
        if self.if_location_pirate(): return
        # ЧИСЛО - это сколько оставляем
        use_items = self.mega().values_options()
        for use_item in use_items.keys():
            got_items = self._get_game_state().count_in_storage('@'+use_item)
            if got_items == 0 or (got_items <= use_items[use_item]): continue
            if got_items > use_items[use_item]: got_items = got_items-use_items[use_item] # учитываем ограничение
            if got_items > 100: got_items = 100 # ограничиваем по 100 за переход
            logger.info(u'Бьем "%s" в количестве = %d' % (self._get_item_reader().get(use_item).name, got_items))
            sell_event = GameUseStorageItem(itemId=unicode(use_item), y=long(15), x=long(15))
            sell_event9 = []
            for n in range(9):
                sell_event9.append(sell_event)
            for ev in range(got_items / 10):
                self._get_events_sender().send_game_events([sell_event])
                self._get_events_sender().send_game_events(sell_event9)
                self._get_game_state().remove_from_storage('@'+use_item,10)
                col = got_items / 10
                got_items -= 10
            if got_items > 0:
                self._get_events_sender().send_game_events([sell_event])
                self._get_game_state().remove_from_storage('@'+use_item,1)
                if (got_items-1) > 0:
                    event = []
                    for n in range(got_items-1):
                        event.append(sell_event)
                    self._get_events_sender().send_game_events(event)
                    self._get_game_state().remove_from_storage('@'+use_item,got_items-1)


class HarvesterBot(BaseActor):

    def perform_action(self):
        if self.if_location_pirate(): return
        current_loc = self._get_game_state().get_location_id()
        if current_loc == 'un_02': return

        par = self.mega().harvester_options()
        waits = par.get('waits', 0)

        plants = self._get_game_location().get_all_objects_by_type(GamePlant.type)
        trees = self._get_game_location().get_all_objects_by_type(GameFruitTree.type)  
        harvestItems = plants + trees

        pause = 0
        for harvestItem in list(plants):
            # print self._get_timer().has_time(harvestItem.jobFinishTime) + 3000
            has_time = self._get_timer().has_time(harvestItem.jobFinishTime) + 3000
            if has_time > 0 and has_time <= waits*1000 and has_time > pause:
                pause = has_time
        if int(pause):
            self.wait_harvest(int(pause))

        pick_name = {}
        pick_events = []
        for harvestItem in list(harvestItems):
            pick_event = self._pick_harvest(harvestItem,pick_name)
            if pick_event:
                pick_events.append(pick_event)
        if len(pick_name.keys()) > 0:
            for i in pick_name.keys():
                logger.info(u"Собрали %d '%s'"%(pick_name[i],i))
            self._get_events_sender().send_game_events(pick_events)

        slags = self._get_game_location().get_all_objects_by_type(GameSlag.type)
        dig_events = []
        dig_name={}
        for slag in list(slags):
            item = self._get_item_reader().get(slag.item)
            if item.name in dig_name.keys(): dig_name[item.name] += 1
            else: dig_name[item.name] = 1
            dig_event = GameDigItem(slag.id)
            dig_events.append(dig_event)
            # convert slag to ground
            slag.type = 'base'
            slag.item = '@GROUND'
        if len(dig_name.keys()) <> 0:
            self._get_events_sender().send_game_events(dig_events)
            for i in dig_name.keys():
                logger.info(u"Вскопали %d '%s'"%(dig_name[i],i))

    def _pick_harvest(self, harvestItem,pick_name):
        if self._get_timer().has_elapsed(harvestItem.jobFinishTime):
            # print u'время собирать', self._get_timer().has_elapsed(harvestItem.jobFinishTime), harvestItem.jobFinishTime
            item = self._get_item_reader().get(harvestItem.item)
            if item.name in pick_name.keys(): pick_name[item.name] += 1
            else: pick_name[item.name] = 1
            pick_event = GamePickItem(objId = harvestItem.id)

            # Добавляем в game_state информацию о собранном предмете
            if harvestItem.type == GameFruitTree.type:
                item_id = self._get_item_reader().get(harvestItem.item).storageItem
                temp = item_id
            else:
                item_id = harvestItem.item
                temp = item_id
                item_id = self._get_item_reader().get(item_id).storageItem
            # print temp, item_id, self._get_game_state().count_in_storage(item_id)
            # item_id = self.seed2storage_plant(item_id)
            # print u'Добавляем', item_id, u'на склад'
            self._get_game_state().add_from_storage(item_id,1)

            harvestItem.fertilized = False
            # Если собрали золиан - удалить обьект т.к. грядки больше нет
            if harvestItem.item in u'@P_43':
                self._get_game_location().remove_object_by_id(harvestItem.id)

            if harvestItem.type == GamePlant.type:
                # convert plant to slag
                harvestItem.type = GameSlag.type
                harvestItem.item = GameSlag(0L, 0L, 0L).item
            elif harvestItem.type == GameFruitTree.type:
                harvestItem.fruitingCount -= 1
                item = self._get_item_reader().get(harvestItem.item)
                harvestItem.jobFinishTime = self._get_timer()._get_current_client_time() + (item.fruitingTime+5)*1000
                if harvestItem.fruitingCount == 0:
                    pickup_box = dict2obj({'item': item.box,'type': "pickup",'id': harvestItem.id, u'y': harvestItem.y, u'x': harvestItem.x})
                    """
                    name = harvestItem.item[4:]
                    if name == 'MANDARINE': name = 'MANDARIN'
                    if name == 'CHERRY_WHITE': # FT_CHERRY_WHITE
                        name = '@D_MAIL_BOX_CHERRY'
                    else:
                        name = '@FT_PICKUP_BOX_' + name
                    pickup_box = dict2obj({'item': name,'type': "pickup",'id': harvestItem.id, u'y': harvestItem.y, u'x': harvestItem.x})
                    """
                    # remove fruit tree
                    self._get_game_location().remove_object_by_id(harvestItem.id)
                    self._get_game_location().append_object(pickup_box)
                    #print 'pickup_box', obj2dict(pickup_box)
                    
                    #FIND:  @FT_PICKUP_BOX_CHERRY   id =  23314
                    #{u'rotate': 0L, u'item': u'@FT_PICKUP_BOX_CHERRY', u'y': 4L, u'x': 116L, u'type': u'pickup', u'id': 23314L}
            return pick_event


    def seed2storage_plant(self, seed):
        if seed[0] == '@': seed = seed[1:]
        if seed[-1:] == 'R':seedst = seed[2:-1]
        elif seed[2:] == '26': seedst = '27'#перец Чили
        elif seed[2:] == '27': seedst = '29'#алые Розы
        elif seed[2:] == '28': seedst = '30'#смородина
        elif seed[2:] == '29': seedst = '28'#помидоры
        elif seed[2:] == '30': seedst = '32'#сон-трава
        elif seed[2:] == '32': seedst = '33'#капуста
        elif seed[2:] == '33': seedst = '34'#черная рука
        elif seed[2:] == '34': seedst = '35'#белая рука
        elif seed[2:] == '35': seedst = '36'#ананас
        elif seed[2:] == '36': seedst = '37'#тростник
        elif seed[2:] == '37': seedst = '38'#клубника
        elif seed[2:] == '38': seedst = '39'#картошка
        elif seed[2:] == '39': seedst = '40'#мозговница
        elif seed[2:] == '40': seedst = '41'#костяная нога
        elif seed[2:] == '41': seedst = '42'#виноград
        else: seedst = seed[2:]
        return '@S_'+seedst

    def wait_harvest(self, pause):
        # print 'pause', pause, int(pause/1000) + 1
        if int(pause/1000) == 0:
            time.sleep(1)
            return
        pause = pause + 1000
        m = pause/1000/60
        s = int(pause/float(1000) - int(m)*60)
        self.cprint(u'9Ждём урожая^15_%d:%d ^1_начало в %s' % (m,s,time.strftime('%H:%M:%S', time.localtime(time.time()))))
        sec = time.time()
        while pause > 5000:
            m = pause/1000/60
            s = int(pause/float(1000) - int(m)*60)
            self.cprint2(u'9\rОсталось ждать^15_%d:%d  ' % (m,s))
            if (time.time() - sec) > 22:
                self.send([])
                sec = time.time()
            self._get_game().handle_all_events()
            while self._get_game().ping:
                self._get_game().handle_all_events()
            time.sleep(5)
            pause -= 5000
        m = pause/1000/60
        s = int(pause/float(1000) - int(m)*60)
        self.cprint2(u'9\rОсталось ждать^15_%d:%d  ' % (m,s))
        time.sleep(pause/1000)
        self.cprint2(u'9\rОсталось ждать^15_%d:%d ^9_продолжаем работу' % (0,0))
        print


class SeederBot(BaseActor):  # Посейка по складу GirlKris

    def perform_action(self):
        # Чтобы сажал растение наименьшее на складе, указываем в settings.ini вместо семени значение 'All'. 
        # Чтобы сажал розы и лилии в соотношении 2:1, указываем значение 'RL'.
        # Например:  seed_item = {'main':'P_12','isle_03':'All','other':'RL'}
        # Список исключений что НЕ сажаем, если посадка по минимальному складу:
        no_seed = ['@ZOLIAN1','@ZOLIAN2','@FT_APPLE','@FT_CHERRY',
                              '@FT_MANDARINE','@FT_LEMON','@FT_EYE','@FT_SKULL','@FT_CHERRY_WHITE',
                              '@P_45','@P_46','@P_47','@P_48','@P_49','@P_50','@P_60','@P_61','@P_63','@P_64','@P_03','@P_14','@COFFEE_TREE', '@P_65']

        #======================================================================

        if self.if_location_pirate(): return
        location = self._get_game_state().get_location_id()
        if location == 'un_02' or location == u'isle_light': return   
        seed_items = self._get_options()
        if (seed_items <> None) and (seed_items <> 'None'):
            buy_events = []
            grounds = self._get_game_location().get_all_objects_by_type('ground')
            if type(seed_items) == type(''): seed_item = self._get_item_reader().get(seed_items)
            elif type(seed_items) == type({}):
                if location in seed_items.keys(): seed_id = seed_items[location]
                else: seed_id = seed_items.get('other', None)
                if seed_id == 'None' or seed_id == None: return
                if seed_id == 'All':
                    fruit_min = []
                    fruit_min_count = 2000000000 # При достижении 2147483648 скорее всего уйдёт в минус
                    for seed_ in self._get_item_reader().get('seed').items:
                        if seed_ in no_seed: continue
                        seed_reader=self._get_item_reader().get(seed_)
                        if self._get_game_state().get_state().level < int(seed_reader.level):
                            if not seed_reader.id in self._get_game_state().get_state().shopOpened:
                                continue
                        #seed_item = self._get_item_reader().get(seed_)
                        #fruit = self._get_game_state().seed2storage_plant(seed_)
                        fruit = self._get_item_reader().get(seed_).storageItem
                        fruit_count = self._get_game_state().count_in_storage(fruit)
                        #print seed_item.name+" - "+str(fruit_count)
                        if fruit_count < fruit_min_count:
                            fruit_min.append(seed_)
                            fruit_min_count = fruit_count
                    if fruit_min == []: return
                    seed_id = fruit_min[-1]
                    seed_item = self._get_item_reader().get(seed_id)
                    while (not self._is_seed_available(seed_item)) and len(fruit_min) > 1:
                        print u'Нельзя здесь сажать', seed_item.name, seed_id
                        temp = fruit_min.pop()
                        seed_id = fruit_min[-1]
                        seed_item = self._get_item_reader().get(seed_id)

                if seed_id == 'RL':
                    roses = 'P_27'
                    lilies = 'P_15'
                    #roses_storage = self._get_game_state().seed2storage_plant(roses)
                    #lilies_storage = self._get_game_state().seed2storage_plant(lilies)
                    roses_storage = self._get_item_reader().get(roses).storageItem
                    lilies_storage = self._get_item_reader().get(lilies).storageItem
                    roses_count = self._get_game_state().count_in_storage(roses_storage)
                    lilies_count = self._get_game_state().count_in_storage(lilies_storage)
                    if roses_count > lilies_count*2:
                        seed_id = 'P_15'
                    else:
                        seed_id = 'P_27'
                seed_item = self._get_item_reader().get(seed_id)
                #print seed_item.name, seed_id

            else:
                if seed_items_ in no_seed: return
                seed_item = seed_items

            if not self._is_seed_available(seed_item):
                logger.info(u'Это растение здесь сажать запрещено')
                return
            all_event = []
            for ground in list(grounds):
                item = self._get_item_reader().get(ground.item)
                buy_event = GameBuyItem(unicode(seed_item.id),
                                        ground.id,
                                        ground.y, ground.x)
                all_event += [buy_event]
                buy_events.append(buy_event)
                ground.type = u'plant'
                ground.item = unicode(seed_item.id)

            if len(all_event) > 0:
                if seed_item.buyCoins*len(all_event) > self.money(): return
                self._get_events_sender().send_game_events(buy_events)
                self._get_game_state().get_state().gameMoney -= self._get_item_reader().get(seed_item.id).buyCoins*len(all_event)
                logger.info(u'Посеяли %d "%s"'%(len(all_event),seed_item.name))
                logger.info(u'Потратили денег на семена %d'%(seed_item.buyCoins*len(all_event)))

    def _is_seed_available(self, seed_item):
        seed_reader = GameSeedReader(self._get_item_reader())
        game_state = self._get_game_state()
        return seed_reader.is_item_available(seed_item, game_state)
        
    def seed2storage_plant(self, seed):
        if seed[0] == '@': seed = seed[1:]
        if seed[-1:] == 'R':seedst = seed[2:-1]
        elif seed[2:] == '26': seedst = '27'#перец Чили
        elif seed[2:] == '27': seedst = '29'#алые Розы
        elif seed[2:] == '28': seedst = '30'#смородина
        elif seed[2:] == '29': seedst = '28'#помидоры
        elif seed[2:] == '30': seedst = '32'#сон-трава
        elif seed[2:] == '32': seedst = '33'#капуста
        elif seed[2:] == '33': seedst = '34'#черная рука
        elif seed[2:] == '34': seedst = '35'#белая рука
        elif seed[2:] == '35': seedst = '36'#ананас
        elif seed[2:] == '36': seedst = '37'#тростник
        elif seed[2:] == '37': seedst = '38'#клубника
        elif seed[2:] == '38': seedst = '39'#картошка
        elif seed[2:] == '39': seedst = '40'#мозговница
        elif seed[2:] == '40': seedst = '41'#костяная нога
        elif seed[2:] == '41': seedst = '42'#виноград
        else: seedst = seed[2:]
        return '@S_'+seedst


class GameSeedReader(LogicalItemReader):

    def _get_item_type(self):
        return 'seed'

    def _get_all_item_ids(self):
        return self._item_reader.get('shop').seed


class PlantEventHandler(object):
    def __init__(self, game_location):
        self.__game_location = game_location

    def handle(self, event_to_handle):
        gameObject = self.__game_location.get_object_by_id(
            event_to_handle.objId
        )
        if gameObject is None:
            logger.critical("OMG! No such object")
            return
        else:
            gameObject.fertilized = False
            #logger.info(u'Растение посажено')
            gameObject.jobFinishTime = event_to_handle.jobFinishTime
            gameObject.jobStartTime = event_to_handle.jobStartTime


class SeederBot_old(BaseActor):
    def perform_action(self):
        # Активация
        # {"x":3,"type":"item","y":22,"action":"useStorageItem","itemId":"BS_BUFF_FIX_HARVEST_1"}
        # {"x":3,"type":"item","y":22,"action":"useStorageItem","itemId":"BS_BUFF_FIX_DIGGER1"}
        # GameUseStorageItem(itemId=unicode("BS_BUFF_FIX_HARVEST_1"), y=long(22), x=long(3))
        # GameUseStorageItem(itemId=unicode("BS_BUFF_FIX_DIGGER1"), y=long(22), x=long(3))
        # 5-мин урожай
        # max_harv_time = 0
        # for l in self._get_game_state().get_state().buffs.list:
            # if 'BUFF_FIX_HARVEST' in l.item:
                # exp_time = float(l.expire.endDate)
                # if max_harv_time < exp_time :
                    # max_harv_time = exp_time

        # time_harvest = (max_harv_time-self._get_timer()._get_current_client_time())/1000.0
        # time_harvest = int(time_harvest)
        # if time_harvest < 0: time_harvest = 0
        # s = time_harvest-int((int(time_harvest/60.0)-(int(int(time_harvest/60.0)/60.0)*60))*60)-int((int(int(time_harvest/60.0)/60.0))*60*60)
        # m = int(time_harvest/60.0)-(int(int(time_harvest/60.0)/60.0)*60)
        # h = int(int(time_harvest/60.0)/60.0)
        # if time_harvest <> 0: logger.info(u'Осталось 5-мин урожая: %d:%d:%d' % (h,m,s))

        if self.if_location_pirate(): return
        location = self._get_game_state().get_location_id()
        if location == 'un_02' or location == u'isle_light': return
        seed_items = self._get_options()
        if (seed_items <> None) and (seed_items <> 'None'):
            buy_events = []
            grounds = self._get_game_location().get_all_objects_by_type('ground')
            if type(seed_items) == type(''): seed_item = self._get_item_reader().get(seed_items)
            elif type(seed_items) == type({}):
                if location in seed_items.keys(): seed_id = seed_items[location]
                else: seed_id = seed_items['other']
                if seed_id == 'None': return
                seed_item = self._get_item_reader().get(seed_id)
            else: seed_item = seed_items
            if not self._is_seed_available(seed_item):
                logger.info(u'Это растение здесь сажать запрещено')
                return
            all_event = []
            for ground in list(grounds):
                item = self._get_item_reader().get(ground.item)
                buy_event = GameBuyItem(unicode(seed_item.id),
                                        ground.id,
                                        ground.y, ground.x)
                all_event += [buy_event]
                buy_events.append(buy_event)
                ground.type = u'plant'
                ground.item = unicode(seed_item.id)

            if len(all_event) > 0:
                self._get_events_sender().send_game_events(buy_events)
                self._get_game_state().get_state().gameMoney -= self._get_item_reader().get(seed_item.id).buyCoins*len(all_event)
                logger.info(u'Посеяли %d "%s"'%(len(all_event),seed_item.name))
                logger.info(u'Потратили денег на семена %d'%(self._get_item_reader().get(seed_item.id).buyCoins*len(all_event)))

    def _is_seed_available(self, seed_item):
        seed_reader = GameSeedReader(self._get_item_reader())
        game_state = self._get_game_state()
        return seed_reader.is_item_available(seed_item, game_state)
