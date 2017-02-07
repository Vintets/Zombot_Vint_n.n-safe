# coding=utf-8
import logging
import time
from game_state.base import BaseActor
from game_state.game_event import obj2dict
import collections

logger = logging.getLogger(__name__)


class ChangeLocationBot(BaseActor):
    '''
    Changes location

    @param options: Available receive options:

    selected_location: location to change to
    '''

    def perform_action(self):
        if self.if_location_pirate(): return
        self.interval()
        loc_setting = self._get_options()
        current_loc_id = self._get_game_state().get_location_id()
        curuser = str(self._get_game_state().get_curuser())
        
        self.read_timer(curuser)
        self.__init_visit_queue(loc_setting,current_loc_id)
        # print 'self._visit_queue', self._visit_queue
        next_loc_id = self.__get_next_loc_id(loc_setting)
        timer_elapsed = self.timer_test(next_loc_id, curuser)
        while not timer_elapsed:
            next_loc_id = self.__get_next_loc_id(loc_setting)
            timer_elapsed = self.timer_test(next_loc_id, curuser)
        if next_loc_id != current_loc_id or len(self._visit_queue) == 1:
            self.saved_timer(current_loc_id, curuser)
            self.__change_location(next_loc_id)
        else:
            self._get_game().handle_all_events()
            while self._get_game().ping:
                self._get_game().handle_all_events()
            if self.mega().interval() < 10:
                time.sleep(10)

    def read_timer(self, curuser):
        if not hasattr(self, 'file_timer'):
            try:
                with open('statistics\\'+curuser+'\\isle_time.txt', 'r') as f:
                    self.file_timer = eval(f.read())
            except:
                self.file_timer = {}

    def timer_test(self, next_loc_id, curuser):
        time_isles = self.mega().time_isle()
        if next_loc_id not in time_isles.keys(): return True
        time_isle = time_isles[next_loc_id] * 60
        if next_loc_id in self.file_timer.keys():
            if time.time() - self.file_timer[next_loc_id] < time_isle:
                return False
        return True

    def saved_timer(self, current_loc_id, curuser):
        self.file_timer[current_loc_id] = time.time()
        with open('statistics\\'+curuser+'\\isle_time.txt', 'w') as f:
            f.write(str(self.file_timer))

    def __init_visit_queue(self, loc_setting, current_loc_id):
        # {
        # 'locations_only':'[u"isle_polar"]',
        # 'locations_nfree = [u"isle_01", u"isle_small", u"isle_star", u"isle_large", u"isle_moon", u"isle_giant", u"isle_xxl", u"isle_desert"]',
        # 'locations_nwalk':'[u"un_0"+str(x+1) for x in range(9)]',
        # 'locations_nother':'[]'
        # }

        if not hasattr(self, '_visit_queue'):
            pirate_locs_id = ['exploration_isle1_random','exploration_isle2_random','exploration_isle3_random','exploration_snow1','exploration_isle1_1','exploration_isle4_random','exploration_independent_asteroid_random']
            self._visit_queue = collections.deque()
            locations_only = eval(loc_setting['locations_only'])
            ban_isle = eval(loc_setting['locations_nfree'])         # Запрет платных островов
            ban_isle.extend(eval(loc_setting['locations_nwalk']))   # Запрет пещер
            ban_isle.extend(eval(loc_setting['locations_nother']))  # Прочие запреты

            self.loc_nfree = []
            open_locations = []
            reader = self._get_item_reader().get(current_loc_id)
            if not (reader.disableGlobus or (current_loc_id in pirate_locs_id)):
                open_locations.append(current_loc_id)
            for location in self._get_game_state().get_state().locationInfos:
                reader = self._get_item_reader().get(location.locationId)
                if reader.disableGlobus or (location.locationId in pirate_locs_id): continue
                open_locations.append(location.locationId)
                if reader.paid:
                    self.loc_nfree.append(location.locationId)

            if locations_only == []:
                for location in open_locations:
                    if location not in ban_isle:
                        self._visit_queue.appendleft(location)
            else:
                for location in locations_only:
                    if location in open_locations:
                        self._visit_queue.append(location)
            if current_loc_id in self._visit_queue:
                self.__rotation_current(current_loc_id)

    def add_location(self, location):
        self._visit_queue.append(location)

    def __rotation_current(self, current):
        while self._visit_queue[0] != current:
            self._visit_queue.rotate(1)

    def __rotation_until_free(self):
        while self._visit_queue[-1] in self.loc_nfree:
            self._visit_queue.rotate(1)
        return self._visit_queue.pop()

    def __get_next_loc_id(self, loc_setting):
        locations_only = eval(loc_setting['locations_only'])
        next_loc_id = self._visit_queue.pop()
        if next_loc_id in self.loc_nfree:
            buff_list = self._get_game_state().get_state().buffs.list
            buff = False
            for buffs in buff_list:
                if '@BUFF_TRAVEL_TICKET_TIME' in buffs.item:
                    time_exp = buffs.expire.endDate
                    if not self._get_timer().has_elapsed(time_exp):
                        buff = True
            if not buff:
                self._visit_queue.appendleft(next_loc_id)
                next_loc_id = self.__rotation_until_free()
        self._visit_queue.appendleft(next_loc_id)
        return next_loc_id

    def __change_location(self, location_id):
        print ' '
        name = self._get_item_reader().get(location_id).name
        logger.info(u'Переходим на ' + name)
        change_location_event = {
                                "user": None,
                                "locationId" : location_id,
                                "type":"gameState",
                                "action":"gameState",
                                "objId": None
                                }
        self._get_events_sender().send_game_events([change_location_event])

    def __get_next_loc_id_old2(self, loc_setting, current_loc_id):
        locations_only=eval(loc_setting['locations_only'])
        if (locations_only == []):
            # Запрет платных островов
            locations_nfree = eval(loc_setting['locations_nfree'])
            # Запрет пещер
            locations_nwalk = eval(loc_setting['locations_nwalk'])
            # Прочие запреты
            locations_nother = eval(loc_setting['locations_nother'])
            if (current_loc_id not in locations_nfree) and (current_loc_id not in locations_nwalk) and (current_loc_id not in locations_nother):
                self._visit_queue.appendleft(current_loc_id)
            next_loc_id = self._visit_queue.pop()
        else:
            if current_loc_id in locations_only:  
                next_loc_id = locations_only[(locations_only.index(current_loc_id)) - 1]
                loc_nfree = [u"isle_01",u"isle_small",u"isle_star",u"isle_large",u"isle_moon",u"isle_giant",u"isle_xxl",u"isle_desert"]
                if next_loc_id in loc_nfree:
                    buff_list = self._get_game_state().get_state().buffs.list
                    buff = False
                    for buffs in buff_list:
                        if "BUFF_TRAVEL_TICKET_TIME" in buffs.item:
                            time_exp = buffs.expire.endDate
                            if not self._get_timer().has_elapsed(time_exp):
                                buff = True
                    if not buff:
                        next_loc_id = locations_only[-1]
            else: 
                next_loc_id = locations_only[-1]
        return next_loc_id

    def interval(self):
        interval = self.mega().interval()
        if interval > 20:
            self._get_game().handle_all_events()
        while interval > 22:
            interval -= 22
            time.sleep(interval)
            self._get_game().handle_all_events()
            while self._get_game().ping:
                self._get_game().handle_all_events()
        time.sleep(interval)


class GameStateEventHandler(object):
    def __init__(self, game_state, timer,setting_view):
        self.__game_state = game_state
        self.__timer = timer
        self.__setting_view = setting_view

    def handle(self, event_to_handle):
        if event_to_handle is None:
            logger.critical("OMG! No such object")
            return
        else:
            if self.__setting_view['location_send']:
                if (hasattr(event_to_handle, "locationId") is True ): 
                    logger.info(u'Перешли на ' + event_to_handle.locationId)
            if 0: 
                info_guest = event_to_handle.location.guestInfos
                logger.info(u'Гости:')
                for guest in info_guest:
                    jet = self.__timer - guest.visitingTime
                    s = (jet/1000)-(((jet/1000)/60)*60)
                    m = ((jet/1000)/60)-((((jet/1000)/60)/60)*60)
                    h = ((jet/1000)/60)/60
                    logger.info(u'%s\tбыл в %d:%d:%d\tник "%s"'%(guest.userId,h,m,s,guest.playerSettings.userName))
            self.__game_state.set_game_loc(event_to_handle)
