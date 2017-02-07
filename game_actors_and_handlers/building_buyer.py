# coding=utf-8
import logging
from game_state.game_types import GameWoodGrave, GameWoodGraveDouble,\
    GamePickItem, GameWoodTree, GameGainItem, GamePickup
from game_state.game_event import dict2obj
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class BuildingBuyer(BaseActor):

    def perform_action(self):
        location_id = self.mega().change_rocket_options()['location']   # на каком острове
        min_money = self.mega().change_rocket_options()['min_money']    # оставляем монет
        num = self.mega().change_rocket_options()['count']              # партиями по ... шт.
        building_id = 'B_ROCKET'

        if self.if_location_pirate(): return
        current_loc = self._get_game_state().get_location_id()
        if current_loc == location_id:
            if self._get_game_state().get_state().gameMoney < min_money: return
            build_cost = self._get_item_reader().get(building_id).buyCoins
            build_sell = self._get_item_reader().get(building_id).sellCoins
            xp = self._get_item_reader().get(building_id).xp

            next_id = self.new_id()
            objects = self._get_game().get_free_spaces().newObject(building_id)
            need = self._get_item_reader().get(building_id)
            if len(objects) == 0: 
                logger.info(u"Нет пустого места для ракеты")
                return
            for obj in objects:
                break

            logger.info(u'Свободное место для объекта: x=%d, y=%d'% (obj.x,obj.y))
            buy_rocket = {"x":obj.x,"action":"buy","y":obj.y,"itemId":building_id,"type":"item","objId":next_id}
            sell_rocket = {"action":"sell","type":"item","objId":next_id}
            self._event = []
            self.expa  = 0
            level_start = self._get_game_state().get_state().level
            while self._get_game_state().get_state().gameMoney-(build_cost-build_sell) > min_money:
                self._event.append(buy_rocket)
                self._event.append(sell_rocket)
                self._get_game_state().get_state().gameMoney -= (build_cost-build_sell)
                if len(self._event)/2 > num-1:
                    self.events_send()
            self.events_send()

            if self.expa:
                logger.info(u'Обменяли всего %d ракет! Опыта: %d '% (self.expa,xp*self.expa))
                if level_start > 67:
                    logger.info(u'Уровней прибавилось  %f'% (round(float(xp*self.expa)/610000, 2)))

    def events_send(self):
        if self._event != []:
            num2 = len(self._event)/2
            self.expa  += num2
            self._get_events_sender().send_game_events(self._event)
            logger.info(u'Обменяли %d ракет.' % (num2))
            self._event = []
