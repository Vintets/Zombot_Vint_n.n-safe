# coding=utf-8
import logging
from game_state.game_event import dict2obj, obj2dict
from game_state.base import BaseActor
from math import ceil

logger = logging.getLogger(__name__)


# покупаем что либо выставляемое
class BuyAny(BaseActor):
    def perform_action(self):
        data = self.mega().buy_any()
        for options in data:
            self.buy(options)


# покупаем каравеллы
class BuyCaravel(BaseActor):
    def perform_action(self):
        options = self.mega().buy_caravell()
        self.buy(options)


# покупаем золотые лопаты
class BuyShovel(BaseActor):
    def perform_action(self):
        par = self.mega().buy_shovel()
        min_money = par.get('min_money',0)                  # оставляем монет
        num = par.get('count', 300)                         # запросы по ... шт. лопаты х3
        max_result = par.get('max_result', 0)               # поддерживаем максимум лопат

        if self.if_location_pirate(): return
        if self._get_game_state().get_state().gameMoney > min_money + 5000:
            shovel_extra = self._get_game_state().count_in_storage('@SHOVEL_EXTRA')
            if max_result != 0 and shovel_extra >= max_result: return
            logger.info(u'У нас есть золотых лопат:  %s'% (shovel_extra))
            buy = {"itemId":"BOX_SHOVEL_EXTRA3","action":"buy","type":"item"}
            action = False
            shovel = 0
            event_full = []
            for n in range(num):
                event_full.append(buy)
            while self._get_game_state().get_state().gameMoney > min_money + num*5000:
                if max_result != 0 and\
                        self._get_game_state().count_in_storage('@SHOVEL_EXTRA') + num*3 > max_result:
                    break
                self._get_events_sender().send_game_events(event_full)
                shovel += num*3
                self._get_game_state().add_from_storage('@SHOVEL_EXTRA', num*3)
                self._get_game_state().get_state().gameMoney -= num*5000
                logger.info(u'Покупаем %d лопат на сумму %d'% (num*3, num*5000))
                action = True
            if self._get_game_state().get_state().gameMoney > min_money + 5000:
                event = []
                it1 = int((self._get_game_state().get_state().gameMoney - min_money)/5000)
                it2 = int(ceil((max_result - self._get_game_state().count_in_storage('@SHOVEL_EXTRA'))/3.0))
                if max_result == 0:
                    it = it1
                else:
                    it = min(it1, it2)
                if it > 0: 
                    for n in range(it):
                        event.append(buy)
                    self._get_events_sender().send_game_events(event)
                    shovel += it*3
                    self._get_game_state().add_from_storage('@SHOVEL_EXTRA', it*3)
                    self._get_game_state().get_state().gameMoney -= it*5000
                    logger.info(u'Покупаем %d лопат на сумму %d'% (it*3, it*5000))
                    action = True
            if action:
                logger.info(u'Куплено всего %d лопат на сумму %d'% (shovel, shovel/3*5000))


# покупаем зеленые удобрения
class BuyGreenFertilizer(BaseActor):
    def perform_action(self):
        par = self.mega().buy_green_fertilizer()
        min_money = par.get('min_money', 0)                 # оставляем монет
        num = par.get('count', 300)                         # запросы по ... шт. удобрений х50
        max_result = par.get('max_result', 0)               # поддерживаем максимум зел. удобр.

        if self.if_location_pirate(): return
        if self._get_game_state().get_state().gameMoney > min_money + 20000:
            stock_green_fertilizer = self._get_game_state().count_in_storage('@GREEN_FERTILIZER')
            if max_result != 0 and stock_green_fertilizer >= max_result: return
            logger.info(u'У нас есть удобрений: %s'% (stock_green_fertilizer))
            buy = {"itemId":"F_GREEN_BIG","action":"buy","type":"item"}
            action = False
            GREEN_FERTILIZER = 0
            event_full = []
            for n in range(num):
                event_full.append(buy)
            while self._get_game_state().get_state().gameMoney > min_money + num*20000:
                if max_result != 0 and\
                        self._get_game_state().count_in_storage('@GREEN_FERTILIZER') + num*50 > max_result:
                    break
                self._get_events_sender().send_game_events(event_full)
                GREEN_FERTILIZER += num*50
                self._get_game_state().add_from_storage('@GREEN_FERTILIZER', num*50)
                self._get_game_state().get_state().gameMoney -= num*20000
                logger.info(u'Покупаем %d удобрений на сумму %d'% (num*50, num*20000))
                action = True
            if self._get_game_state().get_state().gameMoney > min_money + 20000:
                event = []
                it1 = int((self._get_game_state().get_state().gameMoney - min_money)/20000)
                it2 = int(ceil((max_result - self._get_game_state().count_in_storage('@GREEN_FERTILIZER'))/50.0))
                if max_result == 0:
                    it = it1
                else:
                    it = min(it1, it2)
                if it > 0:
                    for n in range(it):
                        event.append(buy)
                    self._get_events_sender().send_game_events(event)
                    GREEN_FERTILIZER += it*50
                    self._get_game_state().add_from_storage('@GREEN_FERTILIZER', it*50)
                    self._get_game_state().get_state().gameMoney -= it*20000
                    logger.info(u'Покупаем %d удобрений на сумму %d'% (it*50, it*20000))
                    action = True
            if action:
                logger.info(u'Куплено всего %d удобрений на сумму %d'% (GREEN_FERTILIZER, GREEN_FERTILIZER/50*20000))




# {u'rotate': 0L, u'level': 0L, u'nextPlayTimes': {}, u'playsCounts': {}, u'item': u'@B_FLAG_ENGLAND', u'y': 30L, u'x': 11L, u'type': u'building', u'id': 49373L}

# флаг
# u'features': [], 
# u'originalBuyReal': 0L, 
# u'moved': True, 
# u'buyCash': 0L, 
# u'upgrades': [{u'xp': 50L, u'materials': [{u'count':70L, u'item': u'@CR_14', u'notBeUsed': False}, {u'count': 10L, u'item': u'@R_27', u'notBeUsed': False}, {u'count': 20L, u'item': u'@CR_51', u'notBeUsed': False}]}, {u'xp': 200L, u'materials': [{u'count': 15L, u'item': u'@CR_09', u'notBeUsed': False}, {u'count': 50L, u'item': u'@CAKE', u'notBeUsed': False}, {u'count': 5L, u'item': u'@CR_53', u'notBeUsed': False}]}], 
# u'objType': 7L, 
# u'xp': 500L, 
# u'id': u'B_FLAG_ENGLAND', 
# u'sellCoins': 50000L, 
# u'type': u'building', 
# u'multiPlace': False, 
# u'buyCoins': 500000L, 
# u'npcAnchorings': [], 
# u'important': False, 
# u'saleBuyCoins': 250000L, 
# u'name': u'\u0424\u043b\u0430\u0433 \u0412\u0435\u043b\u0438\u043a\u043e\u0431\u0440\u0438\u0442\u0430\u043d\u0438\u0438', 
# u'gift': False, 
# u'level': 63L, 
# u'games': [{u'delayTime': 86400L,u'type': u'roulette', u'id': u'B_ENGLAND_ROULETTE', u'prizes': [{u'count': 10L,u'item': u'@CR_01'}, {u'count': 2500L, u'item': u'@COINS'}, {u'count': 1L, u'item': u'@CR_122'}, {u'count': 250L, u'item': u'@XP'}, {u'count': 15L, u'item': u'@R_27'}, {u'count': 10L, u'item': u'@CR_16'}, {u'count': 7500L, u'item': u'@COINS'}, {u'count': 10L, u'item': u'@CR_55'}, {u'count': 750L, u'item': u'@XP'}, {u'count': 10L, u'item': u'@CR_11'}, {u'count': 500L, u'item': u'@COINS'}, {u'count': 100L, u'item': u'@XP'}], u'level': 2L}],
 # u'crafts': [], 
 # u'openCash': 63L
 

# каравелла
# u'features': [], 
# u'originalBuyReal': 0L, 
# u'moved': True, 
# u'buyCash': 0L, 
# u'buyItem': {u'count': 250L, u'item': u'@DUBLON'},
# u'upgrades': [
# {u'xp': 200L, u'materials': [
    # {u'count': 40L, u'item': u'@CR_41', u'notBeUsed': False}, 
    # {u'count': 10L, u'item': u'@CR_47', u'notBeUsed': False}, 
    # {u'count': 5L, u'item': u'@CR_33', u'notBeUsed': False}]}, 
# {u'xp': 250L, u'materials': [
    # {u'count': 30L, u'item': u'@CR_11', u'notBeUsed': False}, 
    # {u'count': 5L,u'item': u'@CR_68', u'notBeUsed': False}, 
    # {u'count': 5L, u'item': u'@CR_53', u'notBeUsed': False}]}
# ], 
# u'objType': 7L, 
# u'captureTime': 0L, 
# u'id': u'B_PIRATE_CARAVEL_2', 
# u'capacity': 1000L, 
# u'sellCoins': 0L, 
# u'type': u'pirateShip', 
# u'multiPlace': False, 
# u'buyCoins': 0L, 
# u'npcAnchorings': [], 
# u'important': False, 
# u'sailLocation': u'@exploration_isle3_random', 
# u'name': u'\u041a\u0430\u0440\u0430\u0432\u0435\u043b\u043b\u0430', 
# u'gift': False, 
# u'level': 1L, 
# u'xp': 150L, 
# u'placesCount': 7L, 
# u'games': [], 
# u'crafts': [], 
# u'openCash': 1
