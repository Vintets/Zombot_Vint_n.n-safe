# coding=utf-8
import logging
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class TreePlant(BaseActor):

    def perform_action(self):
        if self.if_location_pirate(): return
        min_money = self.mega().tree_plant_options()['min_money']
        plant_tree = self.mega().tree_plant_options()['plant_tree']
        current_loc = self._get_game_state().get_location_id()
        if not current_loc in plant_tree: return 1
        need = plant_tree[current_loc]
        objects = self._get_game().get_free_spaces().newObject(need)
        need = self._get_item_reader().get(need)
        if len(objects) == 0: return
        list_obj = []
        for obj in objects:
            list_obj.append((obj,obj.y))
        list_obj.sort(key=lambda y: y[::-1], reverse=True)  # ресурсы отсортированные по Y
        objects = [obj[0] for obj in list_obj]
        buy = []
        for obj in objects:
            if self._get_game_state().get_state().gameMoney > need.buyCoins + min_money:
                buy_event = {"x":obj.x,"y":obj.y,"action":"buy","itemId":need.id,"type":"item","objId":obj.id}
                buy.append(buy_event)
                self._get_game_state().get_state().gameMoney -= need.buyCoins
                self._get_game_state().get_state().gameObjects.append(obj)
                self._get_game_location().get_game_objects().append(obj)
            else:
                logger.info(u'Не хватает монет')
                break
        if len(buy) > 0:
            self._get_events_sender().send_game_events(buy)
            logger.info(u'Посадили %d %s'%(len(buy),need.name))
