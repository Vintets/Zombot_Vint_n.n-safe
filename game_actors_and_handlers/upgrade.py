# coding=utf-8
import logging
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class Upgrader(BaseActor):
    def perform_action(self):
        options = self.mega().upgrader_options()

        if self.if_location_pirate(): return
        for object in self._get_game_state().get_state().gameObjects:
            if (u'Строим' in options.keys()) and options[u'Строим']:
                if not (object.item in options[u'Строим']): continue
            if (u'НЕ строим' in options.keys()) and (object.item in options[u'НЕ строим']): continue
            obj_reader = self._get_item_reader().get(object.item.lstrip('@'))
            if not hasattr(obj_reader,'upgrades'): continue
            upgrades = obj_reader.upgrades
            if object.level == len(upgrades): continue

            for lev_up in range(object.level, len(upgrades)):
                if not self.check_materials(upgrades[lev_up].materials,obj_reader.name): break
                event = {"type":"item","objId":object.id,"action":"upgrade"}
                self.send([event])
                object.level += 1
                logger.info(u'Поднимаем уровень %s, id %d до уровня %d'%(obj_reader.name,object.id,lev_up+1))
                #removing
                for mat in upgrades[lev_up].materials:
                    self.add_crafted_item(mat.item, -mat.count)
                #adding
                self.add_crafted_item('@XP', upgrades[lev_up].xp)

    def check_materials(self,materials,name):
        for mat in materials:
            if self.craft_item_count(mat.item) < mat.count:
                print u'Не хватает материалов для апгрейда %s'%(name)
                print u'Материала %s %d из %d'%(mat.item,self.craft_item_count(mat.item),mat.count)
                break
        else: return True
        return False


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
