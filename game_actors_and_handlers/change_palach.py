# coding=utf-8
import logging
from math import ceil
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class ChangePalach(BaseActor):
    def perform_action(self):
        support_dublon = self.mega().change_palach_options()['support_dublon']  # поддерживать дублонов
        reserv_palach = self.mega().change_palach_options()['reserv_palach']    # резерв коллекций палача

        if self.if_location_pirate(): return
        dublon_needed = support_dublon - self._get_game_state().count_in_storage('@DUBLON')
        dublon_needed = int(ceil(float(dublon_needed) / 5)) * 5
        # print 'dublon', self._get_game_state().count_in_storage('@DUBLON'), 'dublon_needed', dublon_needed
        if dublon_needed < 1: return

        collectionItems = self._get_game_state().get_state().collectionItems
        pal = []
        for num in range(1,6):
            if hasattr(self._get_game_state().get_state().collectionItems, 'C_48_' + str(num)):
                pal.append(getattr(self._get_game_state().get_state().collectionItems, 'C_48_' + str(num)))
        if len(pal) < 5: return
        count_col = min(pal) - reserv_palach
        if count_col < 1: return

        count = (min(count_col * 5, dublon_needed)) / 5

        if count > 0:
            event = [{"type":"item","count":count,"itemId":'C_48',"action":"collect"}]
            self._get_events_sender().send_game_events(event)
            logger.info(u'Обменяли %d коллекций Палача получив %d дублонов'%(count,count*5))
            self._get_game_state().add_from_storage('@DUBLON', count*5)
            for num in range(1,6):
                self._get_game_state().remove_from_storage('@C_48_' + str(num), count)
                has = getattr(self._get_game_state().get_state().collectionItems, 'C_48_' + str(num))
                setattr(self._get_game_state().get_state().collectionItems, 'C_48_' + str(num), has-count)
