# coding=utf-8
import logging
from game_state.game_types import GameBuilding, GamePlayGame, DailyBonus
from game_state.base import BaseActor
from game_state.game_event import dict2obj, obj2dict
import time

logger = logging.getLogger(__name__)


class RouletteRoller(BaseActor):
    def playCostGame(self,game,building_item):
        rulettes = self.mega().roulettes_options()
        game_id = game.id
        play_cost = game.playCost
        need_item = play_cost.item
        storageCount = self._get_game_state().count_in_storage(need_item)
        need_count = int(play_cost.count)
        # print
        # print 'building_item', building_item, 'game_id', game_id
        # print 'play_cost', play_cost
        # print 'storageCount', storageCount
        # print 'need_count', need_count
        if rulettes.has_key(building_item) and game_id != 'B_SOLDIER_ROULETTE':
            needGame = rulettes[building_item]
            if not needGame.has_key(game_id): return (False, 0)
            if storageCount <= needGame[game_id]: return (False, 0)
            if storageCount < play_cost.count: return (False, 0)
            mogem = int((storageCount-needGame[game_id])/need_count)
            # print u'Можем крутить', building_item, ' : ', game_id, str(mogem), u' раз'
            if mogem > 300: mogem = 300
            self._get_game_state().remove_from_storage(play_cost.item, need_count*mogem)

            return (True, mogem)
        else:
            if storageCount <= need_count: return (False, 0)
            self._get_game_state().remove_from_storage(need_item,need_count)
            return (True, 1)

    def unconditionalPlayCost(self,game,next_play):
        pirateBox = ['@PIRATE_BOX','@PIRATE_BOX_2']
        play_cost = game.unconditionalPlayCost
        if game.id == "B_TAVERNA_ROULETTE_1":
            state = self._get_game_state().get_state().pirate.state
            # print
            # print u'ТАВЕРНА!  state =', state, u'dublon =', self._get_game_state().count_in_storage(play_cost.item)
            if state == 'PIRATE' or state == 'AWAY': return False
            for box in pirateBox:
                if self._get_game_state().count_in_storageObjects(box) > 0: return False
            dublon = self._get_game_state().count_in_storage(play_cost.item)
            if dublon < play_cost.count: return False
            if self._get_timer().has_elapsed(next_play): return True
            # else:
                # self._get_game_state().remove_from_storage(play_cost.item,play_cost.count)
                # return True
        return False

    def enemyStatus(self,building,enemies):
        loc = self._get_game_state().get_game_loc().get_location_id()
        if not enemies or loc == u'main': return False
        for enemy in enemies:
            if (((enemy.x - building.x)**2 + (enemy.y - building.y)**2)**0.5) <= 15:
                return True
        return False

    def fillToLimit(self,game):
        storageCount = self._get_game_state().count_in_storage(game.item)
        if storageCount < game.limit: return True
        else:return False

    def perform_action(self):
        buildings = self._get_game_location().get_all_objects_by_type('building')
        enemies = self._get_game_location().get_all_objects_by_type('pirateEnemy')
        current_loc = self._get_game_state().get_location_id()
        # Ежедневный бонус
        dailyBonus = self._get_game_state().get_state().dailyBonus
        if self._get_timer().has_elapsed(dailyBonus.playFrom):
            daily = DailyBonus()
            self._get_events_sender().send_game_events([daily])
            dailyBonus.playFrom = 10800000
        # Крутим рулетку в волшебнике и т.д
        if hasattr(self._get_game_state().get_state().npcs,'list'):
            wizards = self._get_game_state().get_state().npcs.list
        else:wizards = []
        if wizards:
            for wizard in wizards:
                if wizard.type != 'wizard': continue
                if hasattr(wizard,'prize'): continue
                events = {"type":"npc","id":None,"npcId":wizard.id,"action":"play"}
                self._get_events_sender().send_game_events([events])
        eventRoll = []
        for building in buildings:
            building_item = self._get_item_reader().get(building.item)
            if not building_item.games: continue
            for game in building_item.games:
                need_count = 1
                if building.level < game.level: continue
                game_id = game.id
                if game_id == "B_MAST_ROULETTE" and (current_loc == u'main' or current_loc == u'isle_omega'): continue
                roller = True
                next_play_times = building.nextPlayTimes.__dict__
                if not next_play_times.has_key(game_id):
                    next_play_times[game_id] = -90000
                next_play = int(next_play_times[game_id])
                if not self._get_timer().has_elapsed(next_play): continue
                if hasattr(game,'unconditionalPlayCost'):
                    roller = self.unconditionalPlayCost(game,next_play)
                elif game.type == 'fillToLimit':
                    roller = self.fillToLimit(game)
                elif hasattr(game, 'playCost'):
                    roller, need_count = self.playCostGame(game,building_item.id)
                #if not self._get_timer().has_elapsed(next_play): continue
                if hasattr(game, 'playsCount'):
                    playsCounts = building.playsCounts.__dict__
                    if playsCounts.has_key(game_id):
                        play_Count = int(playsCounts[game_id])
                    else:
                        playsCounts[game_id] = 0
                        play_Count = playsCounts[game_id]
                    if play_Count >= game.playsCount: continue
                    playsCounts[game_id] += 1
                    building.playsCounts = dict2obj(playsCounts)
                #if not enemies: enemy_here = False
                #else: enemy_here = self.enemyStatus(building,enemies)
                enemy_here = self.enemyStatus(building,enemies)
                if enemy_here:
                    logger.info(u"Сильвер мешает крутить '%s'"%building_item.name)
                    self._get_game_location().remove_object_by_id(building.id)
                    roller = False
                if not roller: continue
                roll = GamePlayGame(building.id, game_id)
                for iter in range(need_count):
                    eventRoll.append(roll)
                next_play_times[game_id] = 10000
                if len(eventRoll) >= 100: break
        if eventRoll: self._get_events_sender().send_game_events(eventRoll)

class GameResultHandler(object):
    def __init__(self, item_reader, game_location,game_state):
        self.__item_reader = item_reader
        self.__game_location = game_location
        self.__game_state_ = game_state
        self.__collection = game_state.get_state().collectionItems.__dict__
    def handle(self, event_to_handle):
        pirate_locs_id = ['exploration_isle1_random','exploration_isle2_random','exploration_isle3_random','exploration_snow1','exploration_isle1_1','exploration_isle4_random','exploration_independent_asteroid_random']
        _loc = self.__game_state_.get_location_id()
        #self.cprint = self.__game_state_.cprint
        _loc = self.__game_state_.get_location_id()
        readerloc = self.__item_reader.get(_loc)
        if hasattr (event_to_handle,'dailyBonus'):
            daily = self.__game_state_.get_state().dailyBonus
            prize_pos = event_to_handle.pos
            game_prize = daily.prizes[prize_pos]
            prize = self.__item_reader.get(game_prize.item)
            logger.info(u"Крутанул: Ежедневный бонус Приз: %d %s "%(game_prize.count,prize.name.upper()))
        elif event_to_handle.type == 'wizardNpcPlay':
            npcsAll = self.__game_state_.get_state().npcs.list
            for npcs in npcsAll:
                if npcs.id != event_to_handle.npcId: continue
                npcsRead = self.__item_reader.get(npcs.item)
                prize = npcsRead.prizes[event_to_handle.pos]
                prizeRead = self.__item_reader.get(prize.item)
                prizeSTR = u'Выиграл %s %s шт.'%(prizeRead.name.upper(),str(prize.count))
                logger.info(u"Крутанул '%s' %s"%(npcsRead.name,prizeSTR))
                setattr(npcs,'prize',dict2obj({u'count': prize.count, u'item': prize.item}))
            self.__game_state_.get_state().npcs.list = dict2obj(npcsAll)
        elif event_to_handle.action == u'play':
            gameObject = self.__game_location.get_object_by_id(event_to_handle.objId)
            if gameObject is None: return
            #print str(obj2dict(event_to_handle))

            extraId = event_to_handle.extraId
            if hasattr(event_to_handle,'nextPlayDate'):
                nextPlayDate = event_to_handle.nextPlayDate
                gameObject.nextPlayTimes.__setattr__(extraId,nextPlayDate)
            building = self.__item_reader.get(gameObject.item)
            #print
            #print 'building', building.name
            #print str(obj2dict(building))
            for game in building.games:
                if game.id != extraId: continue
                game_prize = False
                if extraId == 'FILL_TRIDENT':
                    fill = game.limit-self.__game_state_.count_in_storage(game.item)
                    game_prize = dict2obj({"count":fill,"item":game.item})
                elif hasattr(event_to_handle.result, 'pos'):
                    prize_pos = event_to_handle.result.pos
                    game_prize = game.prizes[prize_pos]
                elif hasattr(event_to_handle.result, 'won'):
                    prize_pos = event_to_handle.result.won
                    if prize_pos is not None:game_prize = game.combinations[prize_pos].prize
                if not game_prize:
                    prizeSTR = u'Ничего не выиграл.'
                    logger.info(u"Крутанул '%s' %s"%(building.name,prizeSTR))
                    return
                prize = self.__item_reader.get(game_prize.item)
                if readerloc.type == 'explorationLocation' and prize.type == 'chopInstrument':
                    if not readerloc.disableUseTicketFromGlobus:
                        self.__game_state_.add_pirate_instruments(game_prize.item, game_prize.count)
                    else: self.__game_state_.add_from_storage(game_prize.item, game_prize.count)
                elif prize.type == 'collectionItem':
                    if self.__collection.has_key(prize.id):
                        self.__collection[prize.id] += game_prize.count
                    else:self.__collection[prize.id] = game_prize.count
                    self.__game_state_.get_state().collectionItems = dict2obj(self.__collection)
                elif hasattr(prize,'moved') and prize.moved:
                    self.__game_state_.add_from_storageObjects(game_prize.item, game_prize.count)
                else: self.__game_state_.add_from_storage(game_prize.item, game_prize.count)
                prizeSTR = u'приз: %s %s шт.'%(prize.name.upper(),str(game_prize.count))
                if game_prize.item in ['@PIRATE_BOX','@PIRATE_BOX_2']:
                    self.__game_state_.get_state().pirate.state = 'CITIZEN'

                buildings = self.__game_location.get_all_objects_by_type('building')
                for building2 in buildings:
                    if building2.id == event_to_handle.objId:
                        break

                # проверка на лимит рулетки
                playsCount = 0
                if hasattr(game, 'playsCount'):
                    #print
                    #print 'building2'
                    #print str(obj2dict(building2))
                    #print 'playsCounts', building2.playsCounts
                    plays = building2.playsCounts.__dict__
                    if extraId in plays:
                        playsCount = plays[extraId]
                    #print 'playsCount', playsCount

                if playsCount > 0:
                    logger.info(u"Крутанул '%s' %s кручено %d/%d"%(building.name,prizeSTR,playsCount,game.playsCount))
                else:
                    if (_loc in pirate_locs_id):
                        logger.info(u"Крутанул '%s' %s  id %d" % (building.name,prizeSTR,event_to_handle.objId))
                    else:
                        logger.info(u"Крутанул '%s' %s" % (building.name,prizeSTR))


class RouletteTavernaDub(BaseActor):

    def perform_action(self):
        if not hasattr(self._get_game_state().get_state(), 'pirate'): return
        if hasattr(self._get_game_state().get_state().pirate, 'state'):
            state = self._get_game_state().get_state().pirate.state
        else:
            setattr(self._get_game_state().get_state().pirate, 'RETURNED')
        # print u'ТАВЕРНА!  state =', state, u'dublon =', self._get_game_state().count_in_storage('@DUBLON')
        if state == 'PIRATE' or state == 'AWAY': return
        pirateBox = ['@PIRATE_BOX','@PIRATE_BOX_2']
        for box in pirateBox:
            if self._get_game_state().count_in_storageObjects(box) > 0: return

        buildings = self._get_game_location().get_all_objects_by_type(GameBuilding.type)
        for building in list(buildings):
            building_item = self._get_item_reader().get(building.item)
            for game in building_item.games:
                if game.id == 'B_TAVERNA_ROULETTE_1' and game.level > 2:
                    #print obj2dict(building_item)
                    print u'Заскочили в платную таверну'
                    dublon = self._get_game_state().count_in_storage('@DUBLON')
                    print u'Дублонов:', dublon

                    # logger.info(u"П Крутим рулетку в '" + building_item.name + "' " +str(building.id) + u" коорд.(" + str(building.x) + u"," + str(building.y) + u")")
                    roll_count = 0
                    _box = False
                    while not _box and dublon > 5:
                        roll_count += 1
                        dublon -= 5
                        self._get_game_state().remove_from_storage('@DUBLON',5)
                        roll = GamePlayGame(building.id, game.id)
                        self._get_events_sender().send_game_events([roll])
                        self._get_game().game_result = []
                        self._get_game().handle_all_events()
                        while not self._get_game().game_result:
                            print u'\b.',
                            self._get_events_sender().send_game_events([])
                            self._get_game().handle_all_events()
                            time.sleep(0.1)
                        print ''
                        for box in pirateBox:
                            if self._get_game_state().count_in_storageObjects(box) > 0:
                                self._get_game_state().get_state().pirate.state = 'CITIZEN'
                                _box = True
                                logger.info(u'Выигран пиратский сундук!')
                                break
                        time.sleep(0.1)
                    logger.info(u'Кручено за дублоны %d раз' % (roll_count))
                    with open('statistics\\taverna.txt', 'a') as f:
                        f.write(str(roll_count) + '\n')


#{u'rotate': 0L, u'level': 3L, u'nextPlayTimes': {u'B_TAVERNA_ROULETTE_1': u'-9509028155'}, u'playsCounts': {}, u'item': u'@B_TAVERNA', u'y': 37L, u'x': 26L, u'type': u'building', u'id': -5024L}


# u'id': u'B_TAVERNA', 
# u'type': u'building', 
# u'name': u'\u0422\u0430\u0432\u0435\u0440\u043d\u0430', 
# u'games':[{
# u'requirements': [{u'requirements': [{u'item': u'@PS_PRISONER', u'type': u'playerStatusItemRequirement'}], u'type': u'not'}, {u'requirements': [{u'type': u'hasStorageComposition', u'composition': u'@PIRATE_BOX'}], u'type': u'not'}, {u'requirements': [{u'type': u'hasStorageComposition', u'composition': u'@PIRATE_BOX_2'}], u'type': u'not'}, {u'requirements': [{u'type': u'pirateStateRequirement'},{u'state': u'CITIZEN', u'type': u'pirateStateRequirement'}, {u'state': u'RETURNED', u'type': u'pirateStateRequirement'}, {u'state': u'DEAD', u'type': u'pirateStateRequirement'}], u'type': u'or'}], 
# u'unconditionalPlayCost': {u'count': 5L, u'item': u'@DUBLON'}, 
# u'delayTime': 86400L, 
# u'prizes': [{u'count': 1L, u'item': u'@DUBLON'}, {u'count': 5L, u'item': u'@CHOP_MACHETE'}, {u'count': 1L, u'item': u'@PIRATE_BOX'}, {u'count': 5L, u'item': u'@CHOP_AXE'}, {u'count': 10L, u'item': u'@CHOP_HAMMER'}, {u'count': 1L, u'item': u'@DUBLON'}, {u'count': 5L, u'item': u'@CHOP_MACHETE'}, {u'count': 5L, u'item': u'@CHOP_HAMMER'}, {u'count': 5L, u'item': u'@CHOP_AXE'}], 
# u'level': 3L, 
# u'type': u'roulette', 
# u'id': u'B_TAVERNA_ROULETTE_1', 
# u'bonusPrize': {u'count': 1L, u'item': u'@PIRATE_STATE_CITIZEN'}
# }]
