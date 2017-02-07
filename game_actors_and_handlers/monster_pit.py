# coding=utf-8
import logging
from game_state.game_types import GamePickPickup, GamePickItem, GamePickup
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class MonsterPit(BaseActor):

    def perform_action(self):
        if self.if_location_pirate(): return
        monster = self._get_game_location().get_all_objects_by_type('monsterPit')
        if (len(monster) > 0):
            if (monster[0].state == 'HAVE_PICKUP_BOX'):
                monster_event = {
                    'objId': str(monster[0].id),
                    'type': 'item',
                    'action': 'pick'
                    }

                logger.info(u'Забираем сундук монстра...')
                self._get_events_sender().send_game_events([monster_event])

            if (monster[0].state == 'READY_FOR_DIG'):
                monster_event = {
                    'objId': str(monster[0].id),
                    'type': 'item',
                    'action': 'startDig'
                    }
                logger.info(u'Закапываем монстра...')
                self._get_events_sender().send_game_events([monster_event])
