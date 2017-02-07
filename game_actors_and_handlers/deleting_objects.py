#coding=utf-8
import logging
from game_state.base import BaseActor
from game_state.game_event import dict2obj, obj2dict
logger = logging.getLogger(__name__)

class DeletingObjects(BaseActor):
    def perform_action(self):
        par = self.mega().deleting_options()
        obj_del = par.get('object',[])
        type_del = par.get('type','')
        # На каком острове
        loc_del = par.get('isle',[])
        
        if self.if_location_pirate(): return
        current_loc = self._get_game_state().get_location_id()
        if not current_loc in loc_del: return 1
        count_del = 0
        for object in self._get_game_location().get_game_objects():
            if object.type == type_del:
                self._get_events_sender().send_game_events([{"type":"item","objId":object.id,"action":"sell"}])
                #self._get_game_location().remove_object_by_id(object.id)
                count_del += 1
            if object.item in obj_del:
                self._get_events_sender().send_game_events([{"type":"item","objId":object.id,"action":"sell"}])
                #self._get_game_location().remove_object_by_id(object.id)
                count_del += 1
        if count_del > 0:
            logger.info(u'Удалили %d объекта(ов)' % count_del)
