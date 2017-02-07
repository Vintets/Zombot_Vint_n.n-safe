# coding=utf-8
import logging
from game_state.base import BaseActor
from game_state.game_event import obj2dict

logger = logging.getLogger(__name__)


class TradeBot(BaseActor):

    def get_worker_types(self):
        return [GameTraderGrave.type, GameTraderGraveWithBrains.type]

    def perform_action(self):
        if self.if_location_pirate(): return
        #loc_obj = self._get_game_location().get_all_objects_by_types(self.get_worker_types())
        loc_obj = self._get_game_location().get_game_objects()
        for _obj in loc_obj:
            if 'SC_TRADER_GRAVE' in _obj.item:
                if _obj.started == False:
                    trader_event = {"objId":_obj.id,
                                "type":"item",
                                "action":"start"}
                    self._get_events_sender().send_game_events([trader_event])
                    print u'Выгоняем на работу торгаша № ',_obj.id
                    _obj.started = True

                if _obj.countCompleted == 1:
                    trader_event = {"objId":_obj.id,
                                "type":"item",
                                "action":"pick"}
                    self._get_events_sender().send_game_events([trader_event])
                    print u'Забираем коробку у торгаша № ',_obj.id
                    _obj.countCompleted = 0

                if _obj.countExchange == 0 and _obj.countCompleted == 0:
                    give_list = obj2dict(_obj.give)
                    # print '_obj.give', give_list
                    give_t = {}
                    for giv in give_list:
                        give_t[giv['item']] = giv['count']

                    check_give, problem_item = self.check_give(give_t)
                    if not check_give:
                        name = self._get_item_reader().get(problem_item).name
                        self.cprint(u"4Для выставления обмена торговцу не хватает '" + name + "'")
                        continue
                    trader_event = {"objId":_obj.id,
                                    "type":"trader",
                                    "want":_obj.want,
                                    "give":_obj.give,
                                    "action":"change",
                                    "countExchange":1}
                    self._get_events_sender().send_game_events([trader_event])
                    print u'Ставим торг у торгаша № ',_obj.id
                    _obj.countExchange = 1
                    self.remove_tovar(give_t)

    def remove_tovar(self, give_t):
        for item in give_t.keys():
            count = give_t[item]
            if not item.startswith('@'):
                item = '@' + item
            if item.startswith('@C_') and item[-2] == '_':
                item_lstrip = item.lstrip('@')
                collectionItems = self._get_game_state().get_state().collectionItems
                has = 0 if not hasattr(collectionItems, item_lstrip) else getattr(collectionItems, item_lstrip)
                setattr(collectionItems, item_lstrip, has - count)
            elif item.startswith('@C_'):
                item_lstrip = item.lstrip('@')
                collectionItems = self._get_game_state().get_state().collectionItems
                for num in range(1, 6):
                    item_ = item_lstrip + '_' + str(num)
                    has = 0 if not hasattr(collectionItems, item_) else getattr(collectionItems, item_)
                    setattr(collectionItems, item_, has - count)
            else:
                self._get_game_state().remove_from_storage(item, count)

    def check_give(self, give_t):
        for item in give_t.keys():
            count_required = give_t[item]
            if not item.startswith('@'):
                item = '@' + item
            if item.startswith('@C_') and len(item) > 5:
                item_lstrip = item.lstrip('@')
                collectionItems = self._get_game_state().get_state().collectionItems
                has = 0 if not hasattr(collectionItems, item_lstrip) else getattr(collectionItems, item_lstrip)
            elif item.startswith('@C_'):
                item_lstrip = item.lstrip('@')
                collectionItems = self._get_game_state().get_state().collectionItems
                coll = []
                for num in range(1, 6):
                    if hasattr(collectionItems, item_lstrip + '_' + str(num)):
                        coll.append(getattr(collectionItems, item_lstrip + '_' + str(num)))
                if len(coll) < 5: return False, item
                has = min(coll)
            else:
                has = self._get_game_state().count_in_storage(item)
            if has < count_required: return False, item
        return True, None


class TradeSet(BaseActor):

    def opt(self, id=None, user='null', set=False):
        want = self.mega().trade_options()['want']
        give = self.mega().trade_options()['give']
        id = self.mega().trade_options()['id']
        user = self.mega().trade_options()['user']
        set = self.mega().trade_options()['set']
        return (want, give, id, user, set)

    def perform_action(self):
        if self.if_location_pirate(): return
        want_t, give_t, id, user, set = self.opt()
        if not (want_t and give_t): return
        if not id:
            for _obj in self._get_game_location().get_game_objects():
                if ("SC_TRADER_GRAVE" in _obj.item) and _obj.countCompleted == 0:
                    id = _obj.id
                    break
            if not id: return
        else:
            _obj = self._get_game_location().get_object_by_id(id)
            if not (id == _obj.id and ("SC_TRADER_GRAVE" in _obj.item) and _obj.countCompleted == 0):
                return

        if (not set) and _obj.countExchange == 1 : return
        want = []
        for w in want_t.keys():
            want.append({"count":want_t[w],"item":w})

        check_give, problem_item = self.check_give(give_t)
        if not check_give:
            name = self._get_item_reader().get(problem_item).name
            self.cprint(u"4Для выставления обмена торговцу не хватает '" + name + "'")
            return
        give = []
        for w in give_t.keys():
            if not w.startswith('@'):
                w = '@' + w
            give.append({"count":give_t[w],"item":w})

        event = {"want":want,"give":give,"type":"trader","countExchange":1,"action":"change","objId":id}
        if user != 'null':
            event["user"] = user

        self._get_events_sender().send_game_events([event])
        _obj.countExchange = 1
        print u'Ставим спец.торг у торгаша № ',_obj.id
        self.remove_tovar(give_t)

    def remove_tovar(self, give_t):
        for item in give_t.keys():
            count = give_t[item]
            if not item.startswith('@'):
                item = '@' + item
            if item.startswith('@C_') and item[-2] == '_':
                item_lstrip = item.lstrip('@')
                collectionItems = self._get_game_state().get_state().collectionItems
                has = 0 if not hasattr(collectionItems, item_lstrip) else getattr(collectionItems, item_lstrip)
                setattr(collectionItems, item_lstrip, has - count)
            elif item.startswith('@C_'):
                item_lstrip = item.lstrip('@')
                collectionItems = self._get_game_state().get_state().collectionItems
                for num in range(1, 6):
                    item_ = item_lstrip + '_' + str(num)
                    has = 0 if not hasattr(collectionItems, item_) else getattr(collectionItems, item_)
                    setattr(collectionItems, item_, has - count)
            else:
                self._get_game_state().remove_from_storage(item, count)

    def check_give(self, give_t):
        for item in give_t.keys():
            count_required = give_t[item]
            if not item.startswith('@'):
                item = '@' + item
            if item.startswith('@C_') and len(item) > 5:
                item_lstrip = item.lstrip('@')
                collectionItems = self._get_game_state().get_state().collectionItems
                has = 0 if not hasattr(collectionItems,item_lstrip) else getattr(collectionItems,item_lstrip)
            elif item.startswith('@C_'):
                item_lstrip = item.lstrip('@')
                collectionItems = self._get_game_state().get_state().collectionItems
                coll = []
                for num in range(1,6):
                    if hasattr(collectionItems, item_lstrip + '_' + str(num)):
                        coll.append(getattr(collectionItems, item_lstrip + '_' + str(num)))
                if len(coll) < 5: return False, item
                has = min(coll)
            else:
                has = self._get_game_state().count_in_storage(item)
            if has < count_required: return False, item
        return True, None

        #{"action":"change","user":null,"type":"trader","countExchange":1,"objId":20200,"give":[{"count":100,"item":"@C_42"}],"want":[{"count":800000,"item":"@CHOP_HAMMER"}]}
        #{"want":[{"count":10,"item":"@C_43"}],"user":null,"type":"trader","give":[{"count":50,"item":"@C_4"},{"count":10,"item":"@C_2"}],"countExchange":1,"action":"change","objId":20200}
        
        # обмен у друга
        #{"want":[{"item":"@CR_36","count":7}],"action":"remoteExchange","objId":20200,"give":[{"item":"@CR_129","count":3}],"id":24,"type":"trader"}
