# coding=utf-8
import logging
from game_state.game_types import GameWoodGrave, GameWoodGraveDouble,\
    GamePickItem, GameWoodTree, GameStone, GameGainItem, GamePickup
from game_state.game_event import dict2obj
from game_state.base import BaseActor
logger = logging.getLogger(__name__)


class TiketReceiverBot(BaseActor):
    def perform_action(self):
        # билеты на хоккей
        if self.if_location_pirate(): return
        tikets = self._get_game_location().\
                    get_all_objects_by_type('thanksgivingTable')
        tiket_count = 0
        if not hasattr(self._get_game_state(), 'airplane_user'):
            try:
                with open('airplane_user.txt', 'r') as f:
                    self._get_game_state().airplane_user = eval(f.read())
            except:
                self._get_game_state().airplane_user = []

        # if not hasattr(self._get_game_state(), 'airplaneReload'):
            # self._get_game_state().airplaneReload = True
        for tiket in tikets:
            if tiket.item == "@B_BASKETS_EASTER_2015":
                for i in tiket.users:
                    tiket_count += 1
                    self._get_game_state().airplane_user.append(i.id)
                    apply_tiket_event = {"objId":tiket.id,"type":"thanksgivingTable","index":0,"action":"applyThanksgivingGift"}
                    self._get_events_sender().send_game_events([apply_tiket_event])
                    self._get_game_state().add_from_storage("@CANDY_BOX1",1)
                tiket.users = []

                if tiket.item == "@B_BASKETS_EASTER_2015" and not tiket.users: # and self._get_game_state().airplaneReload == True:
                    if tiket.usedPlatesCount == 8:
                        self._get_events_sender().send_game_events([{"objId":tiket.id,"type":"item","action":"reload"}])
                        logger.info(u'Обновляю КОРЗИНОЧКУ!!!')
                    #self._get_game_state().airplaneReload = False
        if tiket_count > 0:
            #tiket_count = count
            logger.info(u'Собрали конфеты: '+str(tiket_count))
            with open('airplane_user.txt', 'w') as f:
                f.write(str(self._get_game_state().airplane_user))


class TiketReceiverBot_Airplane(BaseActor):
    def perform_action(self):
        # билеты на хоккей
        if self.if_location_pirate(): return
        tikets = self._get_game_location().\
                    get_all_objects_by_type('thanksgivingTable')
        tiket_count = 0
        if not hasattr(self._get_game_state(), 'airplane_user'):
            try:
                with open('airplane_user.txt', 'r') as f:
                    self._get_game_state().airplane_user = eval(f.read())
            except:
                self._get_game_state().airplane_user = []

        # if not hasattr(self._get_game_state(), 'airplaneReload'):
            # self._get_game_state().airplaneReload = True
        for tiket in tikets:
            if tiket.item == "@B_HOCKEY_AIRPLANE":
                for i in tiket.users:
                    tiket_count += 1
                    self._get_game_state().airplane_user.append(i.id)
                    apply_tiket_event = {"objId":tiket.id,"type":"thanksgivingTable","index":0,"action":"applyThanksgivingGift"}
                    self._get_events_sender().send_game_events([apply_tiket_event])
                    self._get_game_state().add_from_storage("@CR_TICKET",1)
                tiket.users = []

                if tiket.item == "@B_HOCKEY_AIRPLANE" and not tiket.users: # and self._get_game_state().airplaneReload == True:
                    if tiket.usedPlatesCount == 5:
                        self._get_events_sender().send_game_events([{"objId":tiket.id,"type":"item","action":"reload"}])
                        logger.info(u'Обновляю САМОЛЕТ!!!')
                    #self._get_game_state().airplaneReload = False
        if tiket_count > 0:
            logger.info(u'Собрали билетов: ',tiket_count)
            with open('airplane_user.txt', 'w') as f:
                f.write(str(self._get_game_state().airplane_user))
