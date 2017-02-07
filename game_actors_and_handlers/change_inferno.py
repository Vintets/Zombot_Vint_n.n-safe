# coding=utf-8
import logging
from math import ceil
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class ChangeInferno(BaseActor):
    def perform_action(self):
        support_wand = self.mega().change_inferno_options()['support_wand']  # поддерживать палочек
        reserv_inferno = self.mega().change_inferno_options()['reserv_inferno']    # резерв Адских коллекций

        if self.if_location_pirate(): return
        magic_needed = support_wand - self._get_game_state().count_in_storage('@MAGIC_WAND')
        magic_needed = int(ceil(float(magic_needed) / 15)) * 15
        # print 'magic wand', self._get_game_state().count_in_storage('@MAGIC_WAND'), 'magic_needed', magic_needed
        if magic_needed < 1: return

        collectionItems = self._get_game_state().get_state().collectionItems
        inferno = []
        for num in range(1,6):
            if hasattr(self._get_game_state().get_state().collectionItems, 'C_34_' + str(num)):
                inferno.append(getattr(self._get_game_state().get_state().collectionItems, 'C_34_' + str(num)))
        if len(inferno) < 5: return
        count_col = min(inferno) - reserv_inferno
        # print u'полных ада', min(inferno)
        # print u'можно обменять с учётом резерва', count_col
        if count_col < 1: return

        count = (min(count_col * 15, magic_needed)) / 15
        if count > 0:
            event = [{"type":"item","count":count,"itemId":'C_34',"action":"collect"}]
            self._get_events_sender().send_game_events(event)
            logger.info(u'Обменяли %d Адских коллекций получив %d палочек-выручалочек' % (count,count*15))
            logger.info(u'За обмен получили %d шоколада' % (count))
            self._get_game_state().add_from_storage('@MAGIC_WAND', count*15)
            self._get_game_state().add_from_storage('@CR_79', count)
            for num in range(1,6):
                self._get_game_state().remove_from_storage('@C_34_' + str(num), count)
                has = getattr(self._get_game_state().get_state().collectionItems, 'C_34_' + str(num))
                setattr(self._get_game_state().get_state().collectionItems, 'C_34_' + str(num), has-count)
