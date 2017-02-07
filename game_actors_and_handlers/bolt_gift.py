# coding=utf-8
import logging
import time
from game_state.base import BaseActor
#from game_state.game_types import GameSendGift

logger = logging.getLogger(__name__)

class BoltGift(BaseActor):

    def perform_action(self):
        send_user = self.mega().bolt_gift()['user']     # ID игрока, кому шлем
        item_id = self.mega().bolt_gift()['item_id']    # что слать '@CR_53'болт, '@CR_148'кнопка Z, '@CR_66'лампочка
        msg = self.mega().bolt_gift()['msg']            # сообщение
        count = self.mega().bolt_gift()['count']        # Сколько посылок слать
        nut_count = self.mega().bolt_gift()['nut_count']# по сколько штук

        if self.if_location_pirate(): return
        event = []
        for k in range(count):
            send_gift = {"type":"gift",
                        "action":"sendGift",
                        "gift":{
                            "item":item_id,
                            "msg":msg,
                            "count":nut_count,
                            "user":send_user
                            },
                        "id":k + 1
                        }
            self._get_events_sender().send_game_events([send_gift])
        logger.info( u'Отослал пользователю %s предметов %d' % (send_user, count*nut_count))
        raw_input('-------------   END   ---------------')
        time.sleep(20)
        exit(0)
