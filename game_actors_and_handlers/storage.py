# coding=utf-8
import logging
from game_state.game_types import GameSellItem
from game_state.base import BaseActor
from game_state.game_types import GamePickPickup, GamePickItem, GamePickup

logger = logging.getLogger(__name__)

class SellBot(BaseActor):
    def perform_action(self): # Продажа
        if self.if_location_pirate(): return
        sell_items = self._get_options()
        if sell_items <> None:
            par = self.mega().sell_options()
            min_money = par.get('min_money',1900000000)
            max_money = par.get('max_money',1950000000)
            for item_id in sell_items.keys():
                item_save_count = sell_items[item_id]
                itm_count = self._get_game_state().count_in_storage('@'+item_id)
                item_count = itm_count - item_save_count
                sellCoins = self._get_item_reader().get(item_id).sellCoins
                if item_count > 0 and \
                        self.money() < min_money and \
                        self.money() + sellCoins < max_money:
                    count_max_m = int((max_money - self.money()) / sellCoins)
                    item_count = min(item_count, count_max_m)
                    print 'item_count', item_count
                    sell_event = GameSellItem(count=long(item_count), itemId = unicode(item_id))
                    self._get_events_sender().send_game_events([sell_event])
                    self._get_game_state().remove_from_storage('@'+item_id,item_count)
                    self._get_game_state().get_state().gameMoney += item_count*sellCoins
                    itm_count = self._get_game_state().count_in_storage('@'+item_id)
                    logger.info(u"Продали %d '%s' осталось %d" % (item_count,self._get_item_reader().get(item_id).name,itm_count))

class PutStorage(BaseActor):
    def perform_action(self): # Выставление со склада
        if self.if_location_pirate(): return
        par = self.mega().put_storage_options()
        locations = par.get('location',[])
        objects = par.get('objects',{})

        if not objects: return
        if locations and (not self.location_id() in locations): return
        # проверяем локацию на возможность выставления
        loc = self._get_item_reader().get(self.location_id())
        if loc.disableGlobus:
            # print u'остров временный'
            return
        if loc.invisibleInList:
            # print u'на острове нельзя ставить'
            return
        
        for object in objects.keys():
            item_count = self._get_game_state().count_in_storageObjects(object)
            reserv = objects[object]
            can_put_count = item_count - reserv
            if can_put_count < 1: continue
            name = self._get_item_reader().get(object).name
            
            objects_space = self._get_game().get_free_spaces().newObject(object)
            if not len(objects_space):
                # print u'Нет пустого места для выставления', name
                continue
            # print u'Нужно выставить', name, object, u' ', can_put_count, u'шт. из', item_count, u'мест:', len(objects_space)
            count_put = action_count = min(can_put_count, len(objects_space))
            for obj in objects_space:
                if count_put <= 0: break
                count_put -= 1
                
                event = {
                    "x":obj.x,
                    "y":obj.y,
                    "action":"placeFromStorage",
                    "itemId":object,
                    "type":"item",
                    "objId":obj.id}
                # logger.info(u'Ставим ' + name + u'  ' + object + u' на '+str(obj.x)+u'/'+str(obj.y))                
                self.send([event])

                #adding
                self._get_game_state().get_state().gameObjects.append(obj)
                # self._get_game_location().get_game_objects().append(obj) # НЕТ! в _get_game_state
                #removing
                self._get_game_state().remove_from_storageObjects(object, 1)
            logger.info(u'Поставили ' + name + u'  ' + object + u'  ' + str(action_count) + u' шт.')

            # print
            # print '_get_game_state'
            # for ob in self._get_game_state().get_state().gameObjects:
                # if ob.type == 'pickup':
                    # print ob.item, ob.id
            
            