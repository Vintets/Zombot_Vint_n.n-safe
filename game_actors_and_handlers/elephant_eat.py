# coding=utf-8   
import logging
from game_state.base import BaseActor

logger = logging.getLogger(__name__)

class ElephantEat(BaseActor):

    def perform_action(self):
        
        if self.if_location_pirate(): return
        elefants = []
        if not hasattr(self._get_game_state(), 'count_treasure'): self._get_game_state().count_treasure = 0
        current_loc = self._get_game_state().get_location_id()
        if not hasattr(self._get_game_state(), 'playersInfo'): return # friend = '' 
        else: 
            friends = self._get_game_state().playersInfo
            friend = friends[0].id
        for building in self._get_game_location().get_all_objects_by_type('elephantBase'):
            if not hasattr(building, 'dishes'): 
                elefants.append(building.id)
                continue
            materials = {}
            for dishes in building.dishes:
                if self._get_game_state().count_in_storage(dishes.item) < dishes.count:
                    logger.info(u'Не хватает %d "%s" для слоника'%(
                        dishes.count-self._get_game_state().count_in_storage(dishes.item),
                        self._get_item_reader().get(dishes.item).name))
                    break
                materials[dishes.item] = dishes.count    
            else:     
                for material in materials: self._get_game_state().remove_from_storage(material, materials[material])
                self._get_events_sender().send_game_events([{"type":"elephantBase","elephantBaseId":building.id,"action":"eat"}])
                elefants.append(building.id)
        if not elefants: return
        self._get_events_sender().send_game_events([{"locationId":"main","type":"gameState","travelId":0,"user":friend,"objId":None,"action":"gameState"}])
        logger.info(u'Идём к другу в гости')
        for elefant in elefants:
            self._get_events_sender().send_game_events([{"type":"elephantBase","elephantBaseId":elefant,"action":"find"}])
            self._get_game_state().count_treasure += 1
            logger.info(u'Слоник нашёл клад: %d',self._get_game_state().count_treasure)
        self._get_events_sender().send_game_events([{"locationId":current_loc,"type":"gameState","travelId":0,"user":None,"objId":None,"action":"gameState"}])
        logger.info(u'Возвращаемся домой')