# coding=utf-8
import logging
import time
from game_state.game_types import GamePickPickup, GamePickItem, GamePickup
from game_state.base import BaseActor
from game_state.game_event import dict2obj
import _mega_options


logger = logging.getLogger(__name__)


class Pickuper(BaseActor):

    def perform_action(self):
        pickups = self._get_game_location().get_pickups()
        self.pick_pickups(pickups)

    def pick_pickups(self, pickups):
        if pickups:
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


class BoxPickuper(BaseActor):

    def getOpeningPriceMsg(self, boxItem):
        openingPrice = boxItem.openingPrice[0]
        count = openingPrice.count
        item_name = self._get_item_reader().get(openingPrice.item).name
        price_msg = u'%d %s' % (count, item_name)
        return price_msg

    def perform_action(self):
        _loc = self._get_game_state().get_game_loc().get_location_id()
        if _loc in ('un_07', 'un_06', 'isle_gnome'): return
        exclusion = self.mega().box_pickuper_options()
        boxes = self._get_game_location().get_all_objects_by_type(GamePickup.type)
        if boxes:
            enemies = self._get_game_location().get_all_objects_by_type('pirateEnemy')
            missionEnemy = self._get_game_location().get_all_objects_by_type(u'missionEnemy')
            enemies.extend(missionEnemy)
        for box in boxes:
            if box.item in exclusion: continue
            name = self._get_item_reader().get_name(box)
            boxItem = self._get_item_reader().get(box.item)
            if hasattr(boxItem, 'openingPrice'): continue
            enemy_here = 0
            if enemies and _loc != 'main':
                for enemy in enemies:
                    if(((enemy.x - box.x)**2+(enemy.y - box.y)**2)**0.5) < 16:
                        enemy_here = 1
                        break
                if(enemy_here == 1) and _loc != 'main':
                    logger.info('Сильвер мешает вскрыть ' + str(box.id))
                    continue
            logger.info(u'Вскрываем %s' % name)
            pick_event = GamePickItem(objId=box.id)
            self._get_events_sender().send_game_events([pick_event])
            if u'@PIRATE_BOX_FULL' in box.item:
                self._get_game_state().get_state().pirate.instruments = []
                self._get_game_state().get_state().pirate.storage = []
            self._get_game_location().remove_object_by_id(box.id)


class AddPickupHandler(object):
    def __init__(self, itemReader, game_location, game_state, setting_view):
        self.__game_loc = game_location
        self.__item_reader = itemReader
        self.__game_state_ = game_state
        self.__setting_view = setting_view

    def handle(self, event_to_handle):
        pirate_locs_id = ['exploration_isle1_random','exploration_isle2_random','exploration_isle3_random','exploration_snow1','exploration_isle1_1','exploration_isle4_random','exploration_independent_asteroid_random']
        _loc = self.__game_state_.get_location_id() # текущая локация
        if event_to_handle is None:
            logger.critical("OMG! No such object")
            return
        else:
            tmp = {}
            for pickup in event_to_handle.pickups:
                item_type_msg = {
                    'coins':
                        lambda pickup: u'денег',
                    'xp':
                        lambda pickup: u'опыта',
                    'collection':
                        lambda pickup: u'предмет(ов) коллекции ',
                    'storageItem':
                        lambda pickup: u'предмет(ов) ',
                    'shovel':
                        lambda pickup: u'лопат',
                    'scrapItem':
                        lambda pickup: u'шт. металлолома'
                }.get(pickup.type, lambda pickup: pickup.type)(pickup)
                if (pickup.type == 'collection') or (pickup.type == 'storageItem'):
                    item_type_msg = ('%s%s'%(item_type_msg,self.__item_reader.get(pickup.id).name))
                if item_type_msg in tmp.keys(): tmp[item_type_msg] += pickup.count
                else: tmp[item_type_msg] = pickup.count
                # Добавление в game_state
                if hasattr(pickup, 'id'):              
                    if (_loc in pirate_locs_id) and (pickup.id == 'CHOP_MACHETE' or\
                            pickup.id == 'CHOP_AXE' or pickup.id == 'CHOP_HAMMER'):
                        self.__game_state_.add_pirate_instruments('@'+pickup.id, pickup.count)
                    elif _loc in pirate_locs_id:
                        pass
                    else:
                        self.__game_state_.add_from_storage('@'+pickup.id, pickup.count)

                if not hasattr(self.__game_state_,'all_pickups'): self.__game_state_.all_pickups = []

                new = True
                for info in self.__game_state_.all_pickups:
                    if pickup.type == info.type:
                        if pickup.type in ['coins', 'xp'] or (hasattr(pickup, 'id') and pickup.id == info.id):
                            new = False
                            info.count += pickup.count
                            break
                if new:
                    if (hasattr(pickup, 'id')): id = pickup.id
                    else: id = ''
                    add_pickup = dict2obj({u'type': pickup.type, u'count': pickup.count, u'id': id})
                    self.__game_state_.all_pickups.append(add_pickup)

            if self.__setting_view['pickup']:
                if len(tmp.keys()) > 0:
                    #for i in tmp.keys():
                        #logger.info(u'Подобрали %d %s' % (tmp[i], i))
                    if not hasattr(self.__game_state_,'getcoins'):self.__game_state_.getcoins = 0
                    if not hasattr(self.__game_state_,'getxp'):self.__game_state_.getxp = 0
                    for i in tmp.keys():
                        self.write_log(u'\t\t\t\tдроп %d %s' % (tmp[i], i))
                        if i == u'денег': self.__game_state_.getcoins += tmp[i]
                        elif i == u'опыта': self.__game_state_.getxp += tmp[i]
                        else:
                            logger.info(u'Подобрали %d %s' % (tmp[i], i))

            self.__game_loc.add_pickups(event_to_handle.pickups)

    def write_log(self, text, pref=''):
        curuser = self.__game_state_.get_curuser()
        if not _mega_options.MegaOptions(curuser).err_log(): return
        __date = time.strftime('%Y.%m.%d %H:%M:%S  ', time.localtime(time.time()))
        data = pref + __date + text + u'\n'
        with open('statistics\\log_' + curuser + '.txt', 'a') as f:
            f.write(data.encode('utf-8'))

