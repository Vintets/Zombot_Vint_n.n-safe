# coding=utf-8
import logging
import sys
import time
import datetime
import os.path
import os
import ConfigParser
from game_state.game_types import GamePickItem, GameGainItem, GamePickup
from game_state.game_event import dict2obj, obj2dict
from game_state.base import BaseActor
from game_actors_and_handlers.auto_pirat import AutoPirat, KnockTeam

logger = logging.getLogger(__name__)


class PirateTreeCut(BaseActor):

    def perform_action(self):
        par = self.mega().chop_options()
        options = par.get('action',[])
        if not (u'квестовый остров' in options):
            if not self.if_location_pirate(): return  # для квестовых островов - отключаем

        curuser = str(self._get_game_state().get_curuser())
        myid = self._get_game_state().get_my_id()
        par_kt = self.mega().knock_team()
        seaman = par_kt.get('seaman',[])
        actor_options = self.mega().actor_options()
        auto_pirat = False
        knock_team = False
        for ap1 in actor_options:
            if issubclass(ap1, AutoPirat):
                auto_pirat = True
            elif issubclass(ap1, KnockTeam) and (curuser in seaman):
                knock_team = True

        self.patch = 'statistics\\' + curuser  # короткое имя папки юзера
        sw_name = self.patch + '\\stone_well.txt'

        try:
            seaman_return = self.mega().auto_pirate_options()['seaman_return']
        except:
            seaman_return = False
            
        if seaman_return and (auto_pirat or knock_team) and\
                hasattr(self._get_game_state().get_state().pirate, 'captain') and\
                str(self._get_game_state().get_state().pirate.captain) != str(myid):
            self.cprint(u'14Есть команда автоплавателей и мы НЕ капитан')
            self.write_log(u'Есть команда автоплавателей и мы НЕ капитан')
            self.go_home(curuser)  # возвращаемся домой
            return
        
        # self.create_map()
        enemies = self._get_game_location().get_all_objects_by_type("pirateEnemy")
        missionEnemy = self._get_game_location().get_all_objects_by_type(u'missionEnemy')
        enemies.extend(missionEnemy)

        # читаем список колодцев stone_well.txt
        self.load_stone_well(sw_name)

        # читаем список времени кручения
        sw_run = self.load_sw_run()

        # подключаем колодец если время кручения позволяет
        self.add_stone(sw_run)

        instruments = []        # переменная для инструментов
        sklad = False
        resources = self._get_game_location().get_all_objects_by_type('chop')
        if resources:
            # Пинатель
            self.pinatel_silver(options,enemies)

            if not self.if_location_pirate():
                sklad = True # Предметы на складе
                for item in self._get_game_state().get_state().storageItems:
                    if hasattr(item, 'item'):
                        if '@CHOP_' in item.item:
                            instruments.append(dict2obj({"item":item.item, "count": item.count}))
            else: instruments = self._get_game_state().get_state().pirate.instruments

            CHOP_MACHETE,CHOP_AXE,CHOP_HAMMER,CHOP_TRIDENT = self.get_instr_count(instruments)
            print
            print u'Инструмента перед рубкой М-Т-К-Тр:', str(CHOP_MACHETE)+'-'+str(CHOP_AXE)+'-'+str(CHOP_HAMMER)+'-'+str(CHOP_TRIDENT)

            resources_dict = {resource : resource.x for resource in resources}
            resources_order = resources_dict.items()
            if (u'хитрые условия' in options):
                if (CHOP_MACHETE > 250 and CHOP_HAMMER > 250):
                    self._get_game_state().many_chop = 1  # проставили many_chop если мачете и кирки за 250
                if not hasattr(self._get_game_state(), 'many_chop'): # рублено не много, будем сортировать
                    if (u'ломиться вглубь острова' in options):
                        resources_order.sort(key=lambda x: x[::-1], reverse=True)  # ресурсы отсортированные по X
            else:
                self._get_game_state().many_chop = 1
                if (u'ломиться вглубь острова' in options):
                    resources_order.sort(key=lambda x: x[::-1], reverse=True)  # ресурсы отсортированные по X

            self.cprint(u'1Ресурсов видно:^4_%d' % len(resources_order))
            all_block = True
            for resource in resources_order:
                resource = resource[0]
                #print 'Obj: ', resource.item.ljust(27, " "), ' id = ', resource.id
                #print 'resource ', resource,' ', resource.x 
                #print obj2dict(resource)
                if enemies:
                    enemy_here = 0
                    for enemy in enemies:
                        if (((enemy.x - resource.x)**2+(enemy.y - resource.y)**2)**0.5) <= 15:
                            enemy_here = 1
                            break
                    if(enemy_here == 1):
                        self._get_game_location().remove_object_by_id(resource.id)
                        logger.info('Сильвер мешает вырубке ' + str(resource.id))
                        continue
                                
                tool_needed = resource.chopCount
                type_of_res = resource.item
                type_of_instrument = self._get_item_reader().get(type_of_res).chopInstrumentType
                    
                # сортируем что рубим, а что нет
                if (not hasattr(self._get_game_state(), 'many_chop')): # рублено не много, ограничиваем траты
                    if type_of_instrument == '@CIT_MACHETE':                     # мачете
                        pass
                    elif type_of_instrument == '@CIT_TRIDENT':                  # трезубец
                        pass
                    elif type_of_instrument == '@CIT_AXE':                       # топоры
                        if CHOP_AXE > 600 or tool_needed == 10 or tool_needed == 15 or tool_needed == 16 or tool_needed > 49:
                            pass
                        else: continue
                    elif type_of_instrument == '@CIT_HAMMER':                    # кирки
                        if ('CH_BLACKSTONE' in type_of_res) or ('CH_GREENSTONE' in type_of_res) or ('CH_WHITESTONE' in type_of_res) or ('CH_CRYSTALSTONE' in type_of_res) or tool_needed > 49:
                            pass
                        else: continue 

                for tool in instruments:
                    #print "self._get_item_reader().get(tool.item).chopInstrumentType", self._get_item_reader().get(tool.item).chopInstrumentType
                    #print "type_of_instrument", type_of_instrument
                    if not hasattr(tool, "item"):
                        print u'Нет итема', obj2dict(tool)
                        continue
                    if self._get_item_reader().get(tool.item).chopInstrumentType == type_of_instrument and tool.count > 0: #= tool_needed:
                        # if type_of_instrument == '@CIT_HAMMER' and tool_needed == 100:
                            # tool_needed = 50
                            # logger.info(u'Снижаем удар киркой до 50')

                        if tool.count < tool_needed:
                            if type_of_instrument == '@CIT_TRIDENT':
                                tool_needed = tool.count
                                logger.info(u'Рубим неполный')
                            else: continue

                        #print "resource ", str(obj2dict(resource))
                        gain_event = {"type":"chop","objId":resource.id,"instruments":{self._get_item_reader().get(tool.item).id:tool_needed},"action":"chop"}
                        logger.info(u'Рубим ' + 
                            (self._get_item_reader().get(type_of_res).name).ljust(20, ' ') +
                            (self._get_item_reader().get(tool.item).name).ljust(6, ' ') + 
                            str(tool_needed).rjust(2, ' ') + 
                            u'L, id ' + str(gain_event['objId']))
                        # logger.info(u"Рубим " + str(self._get_item_reader().get(tool.item).id).ljust(13, ' ')+str(tool_needed).rjust(3, ' ')+u'L, id '+str(gain_event['objId']))
                        #logger.info(u"Рубим " + str(self._get_item_reader().get(tool.item).id)+', '+str(tool_needed)+u'L, id '+str(gain_event['objId']))
                        #logger.info(u"Рубим " + str(type_of_instrument)+u' instruments:'+str(self._get_item_reader().get(tool.item).id)+', '+str(tool_needed)+u'L, id '+str(gain_event['objId']))
                        self._get_events_sender().send_game_events([gain_event])
                        if resource.chopCount == tool_needed:
                            self._get_game_location().remove_object_by_id(resource.id)
                        else:
                            resource.chopCount -= tool_needed
                        tool.count -= tool_needed
                        if sklad:
                            #print 'type_of_instrument', type_of_instrument, 'tool.item', tool.item, 'ins', ins
                            self._get_game_state().remove_from_storage(tool.item, tool_needed)
                        break

            CHOP_MACHETE2,CHOP_AXE2,CHOP_HAMMER2,CHOP_TRIDENT2 = self.get_instr_count(instruments)
            if  CHOP_MACHETE-CHOP_MACHETE2 or CHOP_AXE-CHOP_AXE2 or CHOP_HAMMER-CHOP_HAMMER2 or CHOP_TRIDENT-CHOP_TRIDENT2:
                print u'Инструмента после рубки  М-Т-К-Тр:', str(CHOP_MACHETE2)+'-'+str(CHOP_AXE2)+'-'+str(CHOP_HAMMER2)+'-'+str(CHOP_TRIDENT2)
            else:
                if self.location_id() == 'exploration_isle3_random' and\
                        self._get_game_location().get_all_objects_by_type('chop'):
                    self.open_treasures(options,enemies)
                    self.wait_rullets(par,enemies)
                    return
                    
            # открываем сокровища
            self.open_treasures(options,enemies)
            return
        else:
            logger.info('Не осталось ресурсов для добычи')
            if auto_pirat:
                self.go_home(curuser)  # возвращаемся домой домой
                return
            else:
                raw_input('-------------   END   ---------------')

    def get_instr_count(self,instruments,CHOP_MACHETE=0,CHOP_AXE=0,CHOP_HAMMER=0,CHOP_TRIDENT=0):
        for tool in instruments:
            if hasattr(tool, 'item'):
                if tool.item == '@CHOP_MACHETE': CHOP_MACHETE = tool.count
                if tool.item == '@CHOP_AXE': CHOP_AXE = tool.count
                if tool.item == '@CHOP_HAMMER': CHOP_HAMMER = tool.count
                if tool.item == '@CHOP_TRIDENT': CHOP_TRIDENT = tool.count
        return (CHOP_MACHETE,CHOP_AXE,CHOP_HAMMER,CHOP_TRIDENT)

    def pinatel_silver(self,options,enemies):  # Пинатель
        if (u'пинатель сильверов' in options) and enemies:
            if not hasattr(self, 'enemies'):self.enemies = []
            for enemy in enemies:
                if enemy.id in self.enemies: continue
                print u'Шуганём сильвера ' + str(enemy.id)
                self._get_events_sender().send_game_events([{"type":"pirateEnemy","objId":enemy.id,"action":"hit"}])
                self.enemies.append(enemy.id)
                #self._get_game_location().remove_object_by_id(enemy.id)
                pass

    def open_treasures(self,options,enemies):  # открываем сокровища
        if u'вскрытие сокровищ' in options:
            resources_s = self._get_game_location().get_all_objects_by_type('pirateCaptureObject')
            if resources_s:
                for resource in resources_s:
                    if enemies:
                        enemy_here = 0
                        for enemy in enemies:
                            if (((enemy.x - resource.x)**2+(enemy.y - resource.y)**2)**0.5) <= 15:
                                enemy_here = 1
                                break
                        if(enemy_here == 1):
                            self._get_game_location().remove_object_by_id(resource.id)
                            logger.info('Сильвер мешает взять '+str(resource.id))
                            continue
                    if resource.captured:
                        self._get_game_location().remove_object_by_id(resource.id)
                        continue

                    _name = self._get_item_reader().get(resource.item).name
                    logger.info(u'Захватываем %s %d' % (_name, resource.id))
                    # print obj2dict(resource)

                    gain_event = {"type":"pirateCapture","objId":resource.id,"action":"capture"}
                    self._get_events_sender().send_game_events([gain_event])
                    if (resource.item in [u'@PIRATE_CAPTURE_SLOT', u'@PIRATE_CAPTURE_BARREL']):
                        self.new_rulets(resource)
                    else:
                        self._get_game_location().remove_object_by_id(resource.id)
            else:
                # logger.info("Нет неоткрытых сокровищ")
                pass

    def new_rulets(self,resource):
        id = resource.id
        new_item = self._get_item_reader().get(resource.item).success.inside
        new_reader = self._get_item_reader().get(new_item)
        print u'Переделываем %s id %s в рулетку %s' % (resource.item, id, new_item)
        new_obj = {u'rotate': 0L, u'level': 0L, u'nextPlayTimes': {new_reader.games[0].id:u"-90000"}, u'playsCounts': {}, u'item': new_item, u'y': resource.y, u'x': resource.x, u'type': new_reader.type, u'id': id}
        # print 'new_obj', new_obj
        # удаляем старый
        self._get_game_location().remove_object_by_id(id)
        
        self._get_game_location().get_game_objects().append(dict2obj(new_obj))
        time.sleep(0.2)
        self._get_game().handle_all_events()

    def load_stone_well(self, sw_name):  # читаем список колодцев stone_well.txt
        if not hasattr(self, 'stone_well'):
            if os.path.isfile(sw_name):
                with open(sw_name, 'r') as f:   
                    self.stone_well = eval(f.read())
            else:
                self.stone_well = []
            for stone in self.stone_well:
                if self._get_game_location().get_object_by_id(stone[u'id']):
                    print u'Этот колодец уже открыт', stone[u'id']

    def load_sw_run(self):  # читаем список времени кручения
        try:
            with open(self.patch + '\\sw_run.txt', 'r') as f:
                sw_run = eval(f.read())
        except:
            sw_run = {}
        return sw_run

    def add_stone(self,sw_run):  # подключаем колодец если время кручения позволяет
        add = {}
        for stone in self.stone_well:
            if self._get_game_location().get_object_by_id(stone[u'id']):
                #print u'Этот колодец уже открыт', stone[u'id']
                continue
            else:
                if sw_run.get(stone[u'id']) == None or sw_run.get(stone[u'id']) < time.time():
                    print u'Добавляем колодец', stone[u'id']
                    # self._get_game_state().get_state().gameObjects.append(dict2obj(stone))
                    self._get_game_location().get_game_objects().append(dict2obj(stone))
                    add[stone[u'id']] = time.time() + 308
        if add != {}:
            sw_run.update(add)
            with open(self.patch + '\\sw_run.txt', 'w') as f:
                f.write(str(sw_run))

    def go_home(self,curuser):  # возвращаемся домой
        self._get_game_state().get_state().pirate.state = 'RETURNED'
        self.cprint(u'14Возвращаемся домой')
        self.__save_log(curuser)
        self._get_game_state().set_game_loc_was = False
        event = {"type":"pirate","action":"returnFromSail"}
        self.send([event])
        self._get_game().handle_all_events()
        event = {"type":"action","action":"getMissions"}
        self.send([event])
        self._get_game().handle_all_events()
        print u'Ждём загрузки острова',
        while not self._get_game_state().set_game_loc_was:
            print u'\b.',
            self._get_events_sender().send_game_events([])
            self._get_game().handle_all_events()
            time.sleep(0.2)
        print u'\b.'
        time.sleep(1)
        self._get_game().handle_all_events()
        self._get_game_state().get_state().pirate.state = 'RETURNED'
        if hasattr(self._get_game_state().get_state().pirate, 'ship'):
            delattr(self._get_game_state().get_state().pirate, 'ship')
        if hasattr(self._get_game_state().get_state().pirate, 'captain'):
            delattr(self._get_game_state().get_state().pirate, 'captain')
        if os.path.isfile(self.patch + '\\brut_off.txt'):
            os.remove(self.patch + '\\brut_off.txt')
        if hasattr(self, 'stone_well'):
            delattr(self, 'stone_well')

    def __save_log(self,curuser):
        _date = datetime.datetime.today().strftime(' %Y.%m.%d %H:%M:%S ')
        text = str(curuser) + u' ' + _date + u' возвращаемся домой ' + u'\n'
        sostav = self.mega().auto_pirate_options()['sostav']
        # with open('statistics\\otplitiya.txt', 'a') as f:
        with open('statistics\\_avto_pirate_' + str(sostav) + '\\otplitiya.txt', 'a') as f: 
            #'statistics\\'+self.curuser+'\otplitiya.txt'
            f.write(text.encode('utf-8'))
        self.write_log(u'Возвращаемся домой с пиратского')

    def fillToLimit(self,game):
        storageCount = self._get_game_state().count_in_storage(game.item)
        if storageCount < game.limit: return True
        else:return False

    def enemyStatus(self,building,enemies):
        loc = self._get_game_state().get_game_loc().get_location_id()
        if not enemies or loc == u'main': return False
        for enemy in enemies:
            if (((enemy.x - building.x)**2 + (enemy.y - building.y)**2)**0.5) <= 15:
                return True
        return False

    def wait_rullets(self,par,enemies):
        self._get_game().handle_all_events()
        while self._get_game().ping:
            self._get_game().handle_all_events()
        waiting = par.get('waits',1)
        buildings = self._get_game_location().get_all_objects_by_type('building')
        pause = 300000
        times_elapsed = []
        for building in buildings:
            if self.enemyStatus(building,enemies): continue
            building_item = self._get_item_reader().get(building.item)
            if not building_item.games: continue
            for game in building_item.games:
                # if game.type == 'fillToLimit' and not self.fillToLimit(game): return
                if hasattr(game, 'playsCount'):
                    playsCounts = building.playsCounts.__dict__
                    if playsCounts.has_key(game.id) and int(playsCounts[game.id]) >= game.playsCount:
                        continue

                next_play_times = building.nextPlayTimes.__dict__
                if not next_play_times.has_key(game.id):
                    next_play_times[game.id] = -300000
                next_play = int(next_play_times[game.id])
                t = next_play + 2000 - self._get_timer().client_time()
                if t <= 0: t = 0
                times_elapsed.append(t)
        times_elapsed.sort()
        st_time = times_elapsed[0]
        pause = st_time
        for tim in times_elapsed:
            if (tim - st_time) <= (waiting*1000): pause = tim
            else: break
        if pause < 1000: return
        m = pause/1000/60
        s = int(pause/float(1000) - int(m)*60)
        self.cprint(u'9Релаксируем до ближайших рулеток^15_%d:%d ^1_начало в %s' % (m,s,time.strftime('%H:%M:%S', time.localtime(time.time()))))
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
        
    def create_map(self):
        if not hasattr(self, 'isle_map'):
            buildings = self._get_game_location().get_all_objects_by_type('building')
            max_ids = []
            
            for resource in buildings:
                if not hasattr(resource, 'item'): continue
                if resource.item == '@B_STONE_WELL':
                    max_ids.append(resource.id)
            start_id = max(max_ids)
            start_obj = self._get_game_location().get_object_by_id(start_id)

            self.path_map = (
                        self.patch + 
                        '\\map_' + 
                        str(start_obj.x) + 
                        '_' + 
                        str(start_obj.y) + 
                        str(start_id) + '.txt')
            if os.path.isfile(self.path_map):
                with open(self.path_map, 'r') as f:
                    self.isle_map = eval(f.read())  # читаем карту self.isle_map
            else:
                self.isle_map = {}

        new = False
        for object in self._get_game_location().get_game_objects():
            try:
                id = self.isle_map.pop(str(object.id))
            except KeyError:
                new = True
                self.isle_map[str(object.id)] = object.item
        if new:
            with open(self.path_map, 'w') as f:
                f.write(str(self.isle_map))


class ShipCheck(BaseActor):

    def perform_action(self):
        return
        if self.location_id() != 'main': return
        if not hasattr(self._get_game_state().get_state(),'pirate'): return

        curuser = self._get_game_state().get_curuser()
        par = self.mega().ship_check_options()
        ships = par.get('ships',[])
        if not ships: return

        file_seaman = par.get('file_seaman', '')
        if file_seaman:
            if os.path.isfile('statistics\\'+ curuser + '\\' + file_seaman):
                with open('statistics\\'+ curuser + '\\' + file_seaman, 'r') as f:
                    try:
                        legal_seaman = eval(f.read())
                    except:
                        self.cprint(u'12Не можем прочитать файл %s' % file_seaman)
                        return
            else:
                print u'Нет файла %s' % file
                self.cprint(u'12Нет файла %s' % file_seaman)
        else:
            legal_seaman = par.get('seaman', [])
        if not legal_seaman: return

        has_build = self.get_ship(ships)
        for ship in has_build:
            self.check_ship_seaman(ship, legal_seaman)

    def get_ship(self, ships):
        for object in self._get_game_state().get_state().gameObjects:
            if (object.item.lstrip('@') in ship) or (object.item in ship):
                build_reader = self._get_item_reader().get(object.item.lstrip('@'))
                if object.level == len(build_reader.upgrades) and len(object.team) > 0:
                    has_build.append(object)
        return has_build
        
    def check_ship_seaman(ship, legal_seaman):
        for seaman in ship.team:
            if str(seaman) not in legal_seaman:
                logger.info('Выкидываем матроса %s из команды корабля %d' % (str(seaman), ship.id))
                event = {"type":"pirateShip", "user":seaman, "action":"removeFromTeam", "objId":ship.id}
                self.send([event])
                ship.team.remove(seaman)
                self._get_game().handle_all_events()


class PirateTreeCutBroot(BaseActor):

    def perform_action(self):
        if not self.if_location_only_pirate(): return
        return
