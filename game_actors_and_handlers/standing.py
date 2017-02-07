# coding=utf-8
import logging
import time
from game_state.base import BaseActor
from game_state.game_event import obj2dict

logger = logging.getLogger(__name__)

class Standing(BaseActor):
    def perform_action(self):
        self.set_wishlist()             # выставление хотелок
        self.logging_bufs()             # вывод оставшегося времени бафов
        # self.reload_LEMON()             # обновляем лимонные деревья

        return
        raw_input('-------------   END   ---------------')

    def set_wishlist(self):
        if hasattr(self, 'wish_state'): return
        self.wish_state = True
        print u'Наша существующая хотелка:'
        # print self._get_game_state().get_state().wishlist
        for item in self._get_game_state().get_state().wishlist:
            if item: name = self._get_item_reader().get(item.lstrip('@')).name
            else: name = u''
            print u' ' * 5 + str(item).ljust(20, ' ') + name

        set_wish = self.mega().wishlist_options()
        if type(set_wish).__name__ != 'list':
            print
            print u'Не меняем хотелку ботом'
            return
        
        for ind in range(4):
            if ind >= len(set_wish) or set_wish[ind] == None:
                gift = None
            else:
                gift = set_wish[ind].lstrip('@')
                gift = '@' + gift
            if gift == self._get_game_state().get_state().wishlist[ind]: continue
            if self._get_game_state().get_state().wishlist[ind]:
                self.wish_remove(ind)
            if gift:
                if gift in self._get_game_state().get_state().wishlist:
                    bad = self._get_game_state().get_state().wishlist.index(gift)
                    self.wish_remove(bad)
                event = {
                        "type":"wishlist",
                        "itemId":gift.lstrip('@'),
                        "index":ind,
                        "action":"add"}
                self.send([event])
                self._get_game_state().get_state().wishlist[ind] = gift
                name = self._get_item_reader().get(gift.lstrip('@')).name
                logger.info(u'Ставим в слот %d хотелку %s %s' % (ind, gift.ljust(20, ' '), name))

        # {"type":"wishlist","itemId":"CR_204","index":0,"action":"add"}
        # {"type":"wishlist","index":3,"action":"remove"}
        # {"type":"wishlist","itemId":"FREE_NY2016_BOX","index":3,"action":"add"}
        # [u'@CR_204', u'@CR_04', u'@CAKE', u'@FREE_NY2016_BOX']
        pass

    def wish_remove(self, ind):
        event_remove = {"type":"wishlist","index":ind,"action":"remove"}
        self.send([event_remove])
        self._get_game_state().get_state().wishlist[ind] = None
        logger.info(u'Очищаем хотелкин слот: %d' % (ind))

    def logging_bufs(self):
        if self.if_location_pirate(): return
        
        if not hasattr(self, 'old_min'):
            self.old_min = 1000
            return

        cur_time = self._get_timer()._get_current_client_time()
        min = int(cur_time/1000)/60
        if min == self.old_min: return
        self.old_min = min

        self.BuffFixHarvest()
        self.BuffDigger()
        self.BuffFixCook()
        self.TravelBuff()

    def BuffFixHarvest(self):
        is_there_travel_buff = False
        buff_list = self._get_game_state().get_state().buffs.list
        max_time = 0
        for buff in buff_list:
            if '@BUFF_FIX_HARVEST' in buff.item:
                time_exp = int(buff.expire.endDate)
                is_there_travel_buff = True
                if time_exp > max_time :
                    max_time = time_exp
        if not is_there_travel_buff: return
        if int((max_time - self._get_timer()._get_current_client_time())/1000) > 0:
            time_baff = int((max_time - self._get_timer()._get_current_client_time())/1000)
            if time_baff < 0: return
            d = time_baff/86400
            h = (time_baff - 86400*d)/3600
            m = (time_baff - 86400*d - 3600*h)/60
            s = time_baff - 86400*d  - 3600*h - 60*m
            if d == 0:
                self.cprint(u'1Осталось 5-мин урожая:^0_       %d:%d:%d' % (h,m,s))
            elif d == 1:
                self.cprint(u'1Осталось 5-мин урожая:^0_1 день %d:%d:%d' % (h,m,s))
            elif d == 2:
                self.cprint(u'1Осталось 5-мин урожая:^0_%d дня  %d:%d:%d' % (d,h,m,s))

    def BuffDigger(self):
        is_there_travel_buff = False
        buff_list = self._get_game_state().get_state().buffs.list
        max_time = 0
        for buff in buff_list:
            if '@BUFF_FIX_DIGGER' in buff.item:
                time_exp = int(buff.expire.endDate)
                is_there_travel_buff = True
                if time_exp > max_time :
                    max_time = time_exp
        if not is_there_travel_buff: return
        if int((max_time - self._get_timer()._get_current_client_time())/1000) > 0:
            time_baff = int((max_time - self._get_timer()._get_current_client_time())/1000)
            if time_baff < 0: return
            d = time_baff/86400
            h = (time_baff - 86400*d)/3600
            m = (time_baff - 86400*d - 3600*h)/60
            s = time_baff - 86400*d  - 3600*h - 60*m
            if d == 0:
                self.cprint(u'1Осталось супер-поиск: ^0_       %d:%d:%d' % (h,m,s))
            elif d == 1:
                self.cprint(u'1Осталось супер-поиск: ^0_1 день %d:%d:%d' % (h,m,s))
            elif d == 2:
                self.cprint(u'1Осталось супер-поиск: ^0_%d дня  %d:%d:%d' % (d,h,m,s))

    def BuffFixCook(self):
        is_there_travel_buff = False
        buff_list = self._get_game_state().get_state().buffs.list
        max_time = 0
        for buff in buff_list:
            if '@BUFF_FIX_COOK' in buff.item:
                time_exp = int(buff.expire.endDate)
                is_there_travel_buff = True
                if time_exp > max_time :
                    max_time = time_exp
        if not is_there_travel_buff: return
        if int((max_time - self._get_timer()._get_current_client_time())/1000) > 0:
            time_baff = int((max_time - self._get_timer()._get_current_client_time())/1000)
            if time_baff < 0: return
            d = time_baff/86400
            h = (time_baff - 86400*d)/3600
            m = (time_baff - 86400*d - 3600*h)/60
            s = time_baff - 86400*d  - 3600*h - 60*m
            if d == 0:
                self.cprint(u'1Осталось минутки:     ^0_       %d:%d:%d' % (h,m,s))
            elif d == 1:
                self.cprint(u'1Осталось минутки:     ^0_1 день %d:%d:%d' % (h,m,s))
            elif d == 2:
                self.cprint(u'1Осталось минутки:     ^0_%d дня  %d:%d:%d' % (d,h,m,s))

    def TravelBuff(self):
        is_there_travel_buff = False
        buff_list = self._get_game_state().get_state().buffs.list
        max_travel_time = 0
        for buff in buff_list:
            if '@BUFF_TRAVEL_TICKET_TIME' in buff.item:
                time_exp = int(buff.expire.endDate)
                is_there_travel_buff = True
                if time_exp > max_travel_time:
                    max_travel_time = time_exp
            elif buff.item == '@BUFF_TRAVEL_TICKET_COUNT' or buff.item == '@BUFF_TRAVEL_TICKET_COUNT2':
                logger.info(u'Есть жетоны для перехода на платные острова')
                return
        if not is_there_travel_buff: return
        if int((max_travel_time - self._get_timer()._get_current_client_time())/1000) > 0:
            time_travel = int((max_travel_time - self._get_timer()._get_current_client_time())/1000)
            if time_travel < 0: return
            d = time_travel/86400
            h = (time_travel - 86400*d)/3600
            m = (time_travel - 86400*d - 3600*h)/60
            s = time_travel - 86400*d  - 3600*h - 60*m
            
            if d == 0:
                self.cprint(u'1Осталось проездного:  ^0_       %d:%d:%d' % (h,m,s))
            elif d == 1:
                self.cprint(u'1Осталось проездного:  ^0_1 день %d:%d:%d' % (h,m,s))
            else:
                self.cprint(u'1Осталось проездного:  ^0_%d дня  %d:%d:%d' % (d,h,m,s))
                    
    # Обновляем лимон
    def reload_LEMON(self):
        loc = self._get_game_state().get_game_loc().get_location_id()
        events = []
        for object in self._get_game_location().get_game_objects():
            if object.item == '@FT_LEMON'and object.fruitingCount < 3:
                id = object.id
                x = object.x
                y = object.y
                print u'Обновляем лимонное дерево: ', '  id = ', id, '  x/y: ', x, '/', y, u'  кручено ', object.fruitingCount
                event_to = {"type":"item","action":"moveToStorage","objId":id}
                event_from = {"x":x, "y":y, "action":"placeFromStorage", "itemId":'FT_LEMON', "type":"item", "objId":id}
                events.append(event_to)
                events.append(event_from)
                object.fruitingCount = 25
        if len(events) > 0:
            self._get_events_sender().send_game_events(events)
                
        # self._get_events_sender().send_game_events([{"type":"item","action":"moveToStorage","objId":id}])
        # event = {"x":x, "y":y, "action":"placeFromStorage", "itemId":'FT_LEMON', "type":"item", "objId":id}
        # self._get_events_sender().send_game_events([event])

        #FIND:  @FT_LEMON   id =  42784
        #{u'rotate': 0L, u'fruitingCount': 24L, u'fertilized': False, u'item': u'@FT_LEMON', u'jobFinishTime': u'172689319', u'jobStartTime': u'-110681', u'y': 34L, u'x': 33L, u'type': u'fruitTree', u'id': 42784L}
