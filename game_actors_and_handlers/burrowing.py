# coding=utf-8
import logging
from game_state.base import BaseActor
from game_state.game_event import obj2dict
import sys
from ctypes import windll
import time
logger = logging.getLogger(__name__)

stdout_handle = windll.kernel32.GetStdHandle(-11)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute

class DigBot(BaseActor):

    def perform_action(self):
        if self.if_location_pirate(): return
        friends = self._get_options()
        myid = self._get_game_state().get_my_id()

        #обратный счетчик раскопки
        if hasattr(self._get_game_state(), 'digOut'):
            if self._get_game_state().digOut > time.time():
                return
            else:
                del self._get_game_state().digOut

        #если закопаны, раскапываемся
        try: Buried = self._get_game_state().get_state().buriedBy
        except: Buried = None
        if Buried:
            SetConsoleTextAttribute(stdout_handle, 0x0005 | 0x0078)
            print (u'!!!! Раскапываемся !!!!').encode('cp866')
            SetConsoleTextAttribute(stdout_handle, 0x0001 | 0x0078)
            sys.stdout.flush()
            self._get_events_sender().send_game_events([{"user":str(myid),"slot":-1,"type":"bury","action":"digOut"}])
            self._get_game_state().digOut = time.time() + 32
            Buried = None
            del self._get_game_state().get_state().buriedBy
            return

        if friends == [] or friends == None:
            return

        i = 0
        freeslots = []
        #open('burySlots.txt', 'w').write(str(obj2dict(self._get_game_state().get_state().burySlots)))
        for burySlot in self._get_game_state().get_state().burySlots:
            if not hasattr(burySlot, 'user'):
                #print str(i) + " " + 'Free'
                freeslots.append(i)
            i += 1
                #else:
                    #print str(i) + " " + burySlot.user

        if freeslots == []: return #если все слоты заняты выходим из функции

        friendsslot = []
        for slot in freeslots:
            print u'Слот свободен: ' + str(slot + 1)
            friendsslot.append(friends[slot])

        if hasattr(self._get_game_state(), 'playersInfo'):
            players_info = self._get_game_state().playersInfo
            print 'playersInfo:', len(players_info)
        else:
            self._get_events_sender().send_game_events([{"type":"players","action":"getInfo","players":friendsslot}])
            print u'Запрашиваем инфу о друзьях'
            return

        for slot in freeslots:
            #print u'обрабатываем слот', slot+1
            #self._get_events_sender().send_game_events([{"type":"players","action":"getInfo","players":friends[slot]}])
            #print u'Запрашиваем/обновляем инфу о друге'
            load = False
            for info in players_info:
                if str(friends[slot]) == str(info.id):
                    load = True
                    break

            if load:
                if hasattr(info, 'buried'):
                    print u'Раскапываем: ', str(info.id)
                    cook_event = {"user":str(info.id),"type":"bury","action":"digOut"}
                    self._get_events_sender().send_game_events([cook_event])
                    del info.buried
                    self._get_game_state().digOut = time.time() + 5

                text = u'Закапываем: '+str(info.id)
                if hasattr(info, 'name') and info.name:
                    text += u' ' + info.name
                text += u' в слот '+str(slot+1)
                print text
                cook_event = {"action":"bury","type":"bury","user":str(info.id),"slot":slot}
                self._get_events_sender().send_game_events([cook_event])
                self._get_game_state().get_state().burySlots[slot].user = friends[slot]

"""
# Старый вариант
i=0
for slot in freeslots:
    print (u'Закапываем: ' + friends[slot]).encode('cp866')
    cook_event = {"action":"bury","type":"bury","user":friends[slot],"slot":slot}
    self._get_events_sender().send_game_events([cook_event])
    i+=1
return
"""

"""
{u'buriedUntil': u'12604808', u'enabled': True, u'user': u'4203048485042405822'},
{u'buriedUntil': u'12613200', u'enabled': True, u'user': u'3964456987234298509'}, 
{u'buriedUntil': u'12620265', u'enabled': True, u'user': u'14918235694863302451'}, 
{u'buriedUntil': u'12630176', u'enabled': True, u'user': u'7993204982920828146'}

Alert! SERVER_DIG_OUT_BEGIN
Alert! SERVER_HUMAN_CAN_NOT_BE_BURRIED
""" 