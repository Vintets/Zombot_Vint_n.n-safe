# coding=utf-8
import logging
import time
from game_state.game_types import GamePickItem, GamePickup, GameWoodTree, GameStone
from game_state.game_event import dict2obj
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class MagicWand(BaseActor):

    def perform_action(self):
        if self.if_location_pirate(): return
        if not self.check_clock_works(self.mega().magicwand_options()): return
        # print u'Палочек использовано', self._get_game_state().get_state().magic.used
        if self._get_game_state().get_state().magic.used < 500 :
            res = self.mega().magicwand_options()['element']
            types = self.mega().magicwand_options()['types']
            location_id = self.mega().magicwand_options()['location']
            if location_id and (not self._get_game_state().get_location_id() in location_id):
                return
            if res:
                resources = self._get_game_location().get_game_objects()
            elif types:
                resources = self._get_game_location().get_all_objects_by_types(types)
            else:
                return

            index = 0
            for resource in resources:
                if (res and resource.item in res) or types:
                    if index == 0:
                        if not resource.gainStarted:
                            res_item = self._get_item_reader().get(resource.item)
                            for _ in range(resource.materialCount):
                                if self._get_game_state().get_state().magic.used != 500:
                                    if self._get_game_state().count_in_storage('@MAGIC_WAND') > 0:
                                        gain_event = {"action":"magic","type":"item","objId":resource.id}
                                        logger.info(u"Добываем палочкой   " + res_item.name)
                                        self._get_events_sender().send_game_events( [gain_event] )
                                        resource.gainStarted = True
                                        self._get_game_state().get_state().magic.used += 1
                                        self._get_game_state().remove_from_storage('@MAGIC_WAND',1)
                                        resource.materialCount -= 1
                                        if resource.materialCount == 0:
                                            if hasattr(res_item, 'box'):
                                                box_item = self._get_item_reader().get(res_item.box)
                                                new_obj = dict2obj({'item': '@' + box_item.id,
                                                                    'type': GamePickup.type,
                                                                    'id': resource.id})
                                                self._get_game_location().remove_object_by_id(resource.id)
                                                self._get_game_location().append_object(new_obj)
                                                logger.info(u"'%s' превращён в '%s'" % (res_item.name, box_item.name))
                                            else:
                                                self._get_game_location().remove_object_by_id(resource.id)
                                    else:
                                        index = 2
                                        break
                                else:
                                    index = 1
                                    break
                        else: logger.info(u"Ресурс добывается")
                    elif index == 1:
                        print u'Исчерпан лимит палочек на сегодня'
                        break
                    else:
                        print u'Закончились палочки'
                        break
            # logger.info(u"Не осталось ресурсов для добычи")
            # self.BoxOpener()

    def BoxOpener(self):
        box_all = 0
        boxes = self._get_game_location().get_all_objects_by_type(
                                                    GamePickup.type)
        for box in boxes:
          name = self._get_item_reader().get_name(box)
          boxItem = self._get_item_reader().get(box.item)
          if not hasattr(boxItem, 'openingPrice'):
            logger.info(u'Вскрываем %s' % name)
            pick_event = GamePickItem(objId=box.id)
            self._get_events_sender().send_game_events([pick_event])
            self._get_game_location().remove_object_by_id(box.id)

    def getOpeningPriceMsg(self, boxItem):
        openingPrice = boxItem.openingPrice[0]
        count = openingPrice.count
        item_name = self._get_item_reader().get(openingPrice.item).name
        price_msg = u'%d %s' % (count, item_name)
        return price_msg
