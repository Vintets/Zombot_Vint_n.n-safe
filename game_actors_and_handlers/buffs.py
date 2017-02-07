# coding=utf-8
import logging
from game_state.game_event import dict2obj
from game_state.base import BaseActor


logger = logging.getLogger(__name__)


class GameBuffFixHarvest(BaseActor):

    def perform_action(self):
        # Предупреждает, что через "day_count" дней закончится супер-урожай на складе
        day_count = self.mega().buff_options()['day_count']
        # Активировать за "time_activation" секунд до окончания        
        time_activation = self.mega().buff_options()['time_activation'] 
        
        if self.if_location_pirate(): return
        day_1 = day_2 = day_3 = exp_time = 0
        for materials in self._get_game_state().get_state().storageItems:
            if hasattr(materials, 'item'):
                if "BUFF_FIX_HARVEST_1" in materials.item:
                    day_1 = materials.count
                if "BUFF_FIX_HARVEST_2" in materials.item:
                    day_2 = materials.count
                if "BUFF_FIX_HARVEST_3" in materials.item:
                    day_3 = materials.count
        day = day_1 + day_2*2 + day_3*3
        if int(str(day)[-1:]) == 0 or 9 < int(str(day)[-2:]) < 21 or 4 < int(str(day)[-1:]) < 10:
            days = u'дней'
        elif 1 < int(str(day)[-1:]) < 5:
            days = u'дня'
        else:
            days = u'день'
        if day < day_count:
            logger.info(u'Внимание!!! Супер-урожая на складе осталось на %d %s' % (day, days))

        buff_list = self._get_game_state().get_state().buffs.list
        max_time = 0
        for l in buff_list:
            if "BUFF_FIX_HARVEST" in l.item:
                exp_time = int((float(l.expire.endDate)-self._get_timer()._get_current_client_time())/1000)
                if exp_time < 0:
                    exp_time = 0
                if exp_time > max_time: max_time = exp_time
                # d = exp_time/86400
                # h = (exp_time - 86400*d)/3600
                # m = (exp_time - 86400*d - 3600*h)/60
                # s = exp_time - 86400*d  - 3600*h - 60*m
                # if d == 0:
                    # logger.info(u'Осталось 5-мин урожая: %d:%d:%d' % (h,m,s))
                # elif d == 1:
                    # logger.info(u'Осталось 5-мин урожая: 1 день %d:%d:%d' % (h,m,s))
                # elif d == 2:
                    # logger.info(u'Осталось 5-мин урожая: 2 дня %d:%d:%d' % (h,m,s))

        if max_time < time_activation:
            if day_3 > 0:
                event = {"x":20,"type":"item","y":7,"action":"useStorageItem","itemId":"BS_BUFF_FIX_HARVEST_3"}
                self._get_events_sender().send_game_events([event])
                self._get_game_state().remove_from_storage("@BS_BUFF_FIX_HARVEST_3", 1)
                buff_list.append(dict2obj({"item":"@BUFF_FIX_HARVEST_3", "expire": dict2obj({"type":"time", "endDate": str(int(self._get_timer()._get_current_client_time()) + 259200000)})}))
                logger.info(u'Активирован супер-урожай на 3 дня')
            elif day_2 > 0:
                event = {"x":20,"type":"item","y":7,"action":"useStorageItem","itemId":"BS_BUFF_FIX_HARVEST_2"}
                self._get_events_sender().send_game_events([event])
                self._get_game_state().remove_from_storage("@BS_BUFF_FIX_HARVEST_2", 1)
                buff_list.append(dict2obj({"item":"@BUFF_FIX_HARVEST_2", "expire": dict2obj({"type":"time", "endDate": str(int(self._get_timer()._get_current_client_time()) + 172800000)})}))
                logger.info(u'Активирован супер-урожай на 2 дня')
            elif day_1 > 0:
                event = {"x":20,"type":"item","y":7,"action":"useStorageItem","itemId":"BS_BUFF_FIX_HARVEST_1"}
                self._get_events_sender().send_game_events([event])
                self._get_game_state().remove_from_storage("@BS_BUFF_FIX_HARVEST_1", 1)
                buff_list.append(dict2obj({"item":"@BUFF_FIX_HARVEST_1", "expire": dict2obj({"type":"time", "endDate": str(int(self._get_timer()._get_current_client_time()) + 86400000)})}))
                logger.info(u'Активирован супер-урожай на 1 день')
            else:
                logger.info(u'На складе нет супер-урожая!!!')


class GameBuffDigger(BaseActor):

    def perform_action(self):
        # Предупреждает, что через "day_count" дней закончится супер-поиск на складе 
        day_count = self.mega().buff_options()['day_count']
        # Активировать за "time_activation" секунд до окончания
        time_activation = self.mega().buff_options()['time_activation'] 

        if self.if_location_pirate(): return
        day_1 = day_2 = day_3 = exp_time = 0
        for materials in self._get_game_state().get_state().storageItems:
            if hasattr(materials, 'item'): 
                if "BUFF_FIX_DIGGER1" in materials.item:
                    day_1 = materials.count
                    pass
                if "BUFF_FIX_DIGGER2" in materials.item:
                    day_2 = materials.count
                    pass
                if "BUFF_FIX_DIGGER3" in materials.item:
                    day_3 = materials.count
                    pass
        day = day_1 + day_2*2 + day_3*3
        if int(str(day)[-1:]) == 0 or 9 < int(str(day)[-2:]) < 21 or 4 < int(str(day)[-1:]) < 10:
            days = u'дней'
        elif 1 < int(str(day)[-1:]) < 5:
            days = u'дня'
        else:
            days = u'день'
        if day < day_count:
            logger.info(u'Внимание!!! Супер-поиск на складе осталось на %d %s' % (day, days))

        buff_list = self._get_game_state().get_state().buffs.list
        max_time = 0
        for l in buff_list:
            if "BUFF_FIX_DIGGER" in l.item:
                exp_time = int((float(l.expire.endDate)-self._get_timer()._get_current_client_time())/1000)
                if exp_time < 0:
                    exp_time = 0
                if exp_time > max_time: max_time = exp_time
                # d = exp_time/86400
                # h = (exp_time - 86400*d)/3600
                # m = (exp_time - 86400*d - 3600*h)/60
                # s = exp_time - 86400*d  - 3600*h - 60*m
                # if d == 0:
                    # logger.info(u'Осталось супер-поиск: %d:%d:%d' % (h,m,s))
                # elif d == 1:
                    # logger.info(u'Осталось супер-поиск: 1 день %d:%d:%d' % (h,m,s))
                # elif d == 2:
                    # logger.info(u'Осталось супер-поиск: 2 дня %d:%d:%d' % (h,m,s))

        if max_time < time_activation:
            if day_3 > 0:
                event = {"x":20,"type":"item","y":7,"action":"useStorageItem","itemId":"BS_BUFF_FIX_DIGGER3"}
                self._get_events_sender().send_game_events([event])
                self._get_game_state().remove_from_storage("@BS_BUFF_FIX_DIGGER3", 1)
                buff_list.append(dict2obj({"item":"@BUFF_FIX_DIGGER3", "expire": dict2obj({"type":"time", "endDate": str(int(self._get_timer()._get_current_client_time()) + 259200000)})}))
                logger.info(u'Активирован супер-поиск на 3 дня')
            elif day_2 > 0:
                event = {"x":20,"type":"item","y":7,"action":"useStorageItem","itemId":"BS_BUFF_FIX_DIGGER2"}
                self._get_events_sender().send_game_events([event])
                self._get_game_state().remove_from_storage("@BS_BUFF_FIX_DIGGER2", 1)
                buff_list.append(dict2obj({"item":"@BUFF_FIX_DIGGER2", "expire": dict2obj({"type":"time", "endDate": str(int(self._get_timer()._get_current_client_time()) + 172800000)})}))
                logger.info(u'Активирован супер-поиск на 2 дня')
            elif day_1 > 0:
                event = {"x":20,"type":"item","y":7,"action":"useStorageItem","itemId":"BS_BUFF_FIX_DIGGER1"}
                self._get_events_sender().send_game_events([event])
                self._get_game_state().remove_from_storage("@BS_BUFF_FIX_DIGGER1", 1)
                buff_list.append(dict2obj({"item":"@BUFF_FIX_DIGGER1", "expire": dict2obj({"type":"time", "endDate": str(int(self._get_timer()._get_current_client_time()) + 86400000)})}))
                logger.info(u'Активирован супер-поиск на 1 день')
            else:
                logger.info(u'На складе нет супер-поиск!!!')


class GameBuffFixCook(BaseActor):
    
    def perform_action(self):
        # Предупреждает, что через "day_count" дней закончится минутка на складе
        day_count = self.mega().buff_options()['day_count']
        # Активировать за "time_activation" секунд до окончания
        time_activation = self.mega().buff_options()['time_activation'] 

        if self.if_location_pirate(): return
        day_1 = day_2 = day_3 = exp_time = 0
        for materials in self._get_game_state().get_state().storageItems:
            if hasattr(materials, 'item'):
                if "BUFF_FIX_COOK_1" in materials.item:
                    day_1 = materials.count
                if "BUFF_FIX_COOK_2" in materials.item:
                    day_2 = materials.count
                if "BUFF_FIX_COOK_3" in materials.item:
                    day_3 = materials.count
        day = day_1 + day_2*2 + day_3*3
        if int(str(day)[-1:]) == 0 or 9 < int(str(day)[-2:]) < 21 or 4 < int(str(day)[-1:]) < 10:
            days = u'дней'
        elif 1 < int(str(day)[-1:]) < 5:
            days = u'дня'
        else:
            days = u'день'
        if day < day_count:
            logger.info(u'Внимание!!! Минутки на складе осталось на %d %s' % (day, days))

        buff_list = self._get_game_state().get_state().buffs.list
        max_time = 0
        for l in buff_list:
            if "BUFF_FIX_COOK" in l.item:
                exp_time = int((float(l.expire.endDate)-self._get_timer()._get_current_client_time())/1000)
                if exp_time < 0:
                    exp_time = 0
                if exp_time > max_time: max_time = exp_time
                # d = exp_time/86400
                # h = (exp_time - 86400*d)/3600
                # m = (exp_time - 86400*d - 3600*h)/60
                # s = exp_time - 86400*d  - 3600*h - 60*m
                # if d == 0:
                    # logger.info(u'Осталось минутки: %d:%d:%d' % (h,m,s))
                # elif d == 1:
                    # logger.info(u'Осталось минутки: 1 день %d:%d:%d' % (h,m,s))
                # elif d == 2:
                    # logger.info(u'Осталось минутки: 2 дня %d:%d:%d' % (h,m,s))

        if max_time < time_activation:
            if day_3 > 0:
                event = {"x":20,"type":"item","y":7,"action":"useStorageItem","itemId":"BS_BUFF_FIX_COOK_3"}
                self._get_events_sender().send_game_events([event])
                self._get_game_state().remove_from_storage("@BS_BUFF_FIX_COOK_3", 1)
                buff_list.append(dict2obj({"item":"@BUFF_FIX_COOK_3", "expire": dict2obj({"type":"time", "endDate": str(int(self._get_timer()._get_current_client_time()) + 259200000)})}))
                logger.info(u'Активирована минутка на 3 дня')
            elif day_2 > 0:
                event = {"x":20,"type":"item","y":7,"action":"useStorageItem","itemId":"BS_BUFF_FIX_COOK_2"}
                self._get_events_sender().send_game_events([event])
                self._get_game_state().remove_from_storage("@BS_BUFF_FIX_COOK_2", 1)
                buff_list.append(dict2obj({"item":"@BUFF_FIX_COOK_2", "expire": dict2obj({"type":"time", "endDate": str(int(self._get_timer()._get_current_client_time()) + 172800000)})}))
                logger.info(u'Активирована минутка на 2 дня')
            elif day_1 > 0:
                event = {"x":20,"type":"item","y":7,"action":"useStorageItem","itemId":"BS_BUFF_FIX_COOK_1"}
                self._get_events_sender().send_game_events([event])
                self._get_game_state().remove_from_storage("@BS_BUFF_FIX_COOK_1", 1)
                buff_list.append(dict2obj({"item":"@BUFF_FIX_COOK_1", "expire": dict2obj({"type":"time", "endDate": str(int(self._get_timer()._get_current_client_time()) + 86400000)})}))
                logger.info(u'Активирована минутка на 1 день')
            else:
                logger.info(u'На складе нет минутки!!!')


class GameTravelBuff(BaseActor):

    def perform_action(self):
        if self.if_location_pirate(): return
        is_there_travel_buff = False
        buff_list = self._get_game_state().get_state().buffs.list
        o_id = False
        max_travel_time = 0
        for buff in buff_list:
            if '@BUFF_TRAVEL_TICKET_TIME' in buff.item:
                time_exp = int(buff.expire.endDate)
                # print 'time_exp', time_exp
                is_there_travel_buff = True
                if max_travel_time < time_exp :
                    max_travel_time = time_exp
            elif buff.item == '@BUFF_TRAVEL_TICKET_COUNT' or buff.item == '@BUFF_TRAVEL_TICKET_COUNT2':
                #time_exp = buff.expire.count
                time_exp = self._get_timer()._get_current_client_time() + 86400000
                is_there_travel_buff = True

        # if max_travel_time > 0:
            # time_travel = (max_travel_time-self._get_timer()._get_current_client_time())/1000.0
            # time_travel = int(time_travel)
            # if time_travel < 0: time_travel = 0
            # d = int(time_travel/86400)
            # h = (time_travel - 86400*d)/3600
            # m = (time_travel - 86400*d - 3600*h)/60
            # s = time_travel - 86400*d  - 3600*h - 60*m
            
            # if time_travel <> 0:
                # if d == 0:
                    # logger.info(u'Осталось времени проездного: %d:%d:%d' % (h,m,s))
                # elif d == 1:
                    # logger.info(u'Осталось времени проездного: 1 день %d:%d:%d' % (h,m,s))
                # else:
                    # logger.info(u'Осталось времени проездного: %d дня %d:%d:%d' % (d,h,m,s))

        if is_there_travel_buff == False or self._get_timer().has_elapsed(time_exp):
            result, name_result = self.craft({},'B_VAN_ICE_CREAM','1',1)
            # print result, name_result
            if not result:
                result, name_result = self.craft({},'B_VAN_ICE_CREAM_CASH','1',1)
            if result:
                logger.info(self._get_item_reader().get("@BUFF_TRAVEL_TICKET_TIME").name)
                buff_list.append(dict2obj({"item":"@BUFF_TRAVEL_TICKET_TIME", "expire": dict2obj({"type":"time", "endDate": str(int(        self._get_timer()._get_current_client_time()) + 86400000*5)})}))
                logger.info(u'Активирован %s' % (self._get_item_reader().get("@BUFF_TRAVEL_TICKET_TIME").name))


"""
from game_actors_and_handlers.buffs import GameBuffFixHarvest, GameBuffDigger, GameBuffFixCook, GameTravelBuff
    actor_classes = [
        GameBuffFixHarvest,         # Активировать супер-урожай
        GameBuffDigger,             # Активировать супер-поиск
        GameBuffFixCook,            # Активировать повара-минутки
        GameTravelBuff,             # Активировать проездной
        ]
"""
