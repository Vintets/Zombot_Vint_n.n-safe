# coding=utf-8
import logging
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class PremiumGifts(BaseActor):

    def perform_action(self):
        par = self.mega().premium_gifts()
        location_id = par.get('location',['main'])
        gift_list = par.get('gift',[])
        num = par.get('num',300)

        if self.if_location_pirate(): return
        if location_id and (self._get_game_state().get_location_id() not in location_id): return
        s = 0
        events = []
        for gift in list(set(self._get_game_state().get_state().gifts)):
            if s >= num: break
            reader = self._get_item_reader().get(gift.item)
            if not hasattr(reader, 'moved'): continue
            co = s
            if (gift_list and (gift.item.lstrip('@') in gift_list)) or not gift_list:
                item = gift.item.lstrip('@')
                objects = self._get_game().get_free_spaces().newObject(item)
                for obj in objects:
                    if s >= num: break
                    if gift.count < 1:
                        self._get_game_state().get_state().gifts.remove(gift)
                        break
                    s += 1
                    gift.count -= 1
                    events.append({
                            "action":"applyCompGift",
                            "type":"item",
                            "x":obj.x,
                            "y":obj.y,
                            "extraId":gift.id,
                            "itemId":item,
                            "objId":obj.id})
                    obj.type = self._get_item_reader().get(item).type
                    self._get_game_state().get_state().gameObjects.append(obj)
                    self._get_game_location().get_game_objects().append(obj)
                if s - co:
                    name = reader.name
                    logger.info(u'Выставляем подарок %s  %d шт.'% (name, (s-co)))                
        if s:
            self.send(events)
