# coding=utf-8
import logging
from game_state.base import BaseActor
from game_state.game_types import GameApplyGiftEvent, GameGift
logger = logging.getLogger(__name__)


class CakesReceiverBot(BaseActor):

    def perform_action(self): # Пряники
        if self.if_location_pirate(): return
        curuser = str(self._get_game_state().get_curuser())
        if not hasattr(self._get_game_state(), 'conifer_user'):
            try:
                with open('statistics\\'+curuser+'\conifer_user.txt', 'r') as f:
                    self._get_game_state().conifer_user = eval(f.read())
            except:
                self._get_game_state().conifer_user = []

        trees = self._get_game_location().get_all_objects_by_type('newYearTree')
        cakes_count = 0
        for tree in trees:
            for i in tree.users:
                cakes_count += 1
                self._get_game_state().conifer_user.append(i.id)
                apply_tree_event = {"type": "newYearTree",
                                    "action": "applyNewYearGift",
                                    "objId": tree.id,
                                    "index": 0}
                self._get_events_sender().send_game_events([apply_tree_event])
                self._get_game_state().add_from_storage('@CAKE',1)
            tree.users = []
        if cakes_count > 0:
            logger.info(u'Собрали %d пряников' % cakes_count)
            with open('statistics\\'+curuser+'\conifer_user.txt', 'w') as f:
                f.write(str(self._get_game_state().conifer_user))
