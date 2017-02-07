# coding=utf-8
import logging
from game_state.base import BaseActor
from game_state.game_types import GameApplyGiftEvent, GameGift, GameSendGift
from game_state.game_event import dict2obj, obj2dict
import random  as  random_number
import os.path
import os
import time
import datetime
logger = logging.getLogger(__name__)


class GiftReceiverBot(BaseActor):
    def perform_action(self):
        if self.if_location_pirate(): return
        self.receive_all_gifts()

    def receive_all_gifts(self):
        gifts = list(set(self._get_game_state().get_state().gifts))
        # print dir(gifts[0])
        #[ u'count', u'free', u'id', u'item', u'msg', u'type', u'user']
        if len(gifts) > 0:
            logger.info(u'Доступно подарков: %s' % len(gifts))
        for gift in list(gifts):
            self.receive_gift(gift)

    def receive_gift(self, gift):
        item = self._get_item_reader().get(gift.item)
        gift_name = u'П ' + str(gift.count) + ' ' + item.name # подарок
        with_message = hasattr(gift, 'msg') and gift.msg != ''
        moved = hasattr(item, 'moved') and item.moved == True
        free = hasattr(gift, 'free') and gift.free
        admin_id = u'139890285' # zfadmin
        receive_options = self.mega().receive_options()
        admin_gift = ((gift.user == admin_id) or (gift.user == 'zfadmin'))
        _log_message = receive_options.get('logging_message',False)
        _log_words = receive_options.get('words',[])
        if not _log_words: _log_message = False

        if with_message:
            SMS = u' SMS: ' + gift.msg + u''
            #if u'Перрон' in gift.msg or u'перрон' in gift.msg or u'перон' in gift.msg:
            #    sms_perron = u'id '+gift.user+u'  SMS: '+gift.msg+"\n".encode("utf-8")
            #    open('perron_log.txt', 'a').write(sms_perron.encode("utf-8"))
        else:
            SMS = u''
        if moved:
           gift_name = u'В' + gift_name # выставляемый
           logger.info(u"П"+gift_name[1:]+ u"' нужно поместить")
        if free and not moved:
            gift_name = u'Б' + gift_name # бесплатный
        gift_name = gift_name.ljust(22, ' ')
        gift_name += u" от " + gift.user
        gift_name = gift_name.ljust(47, ' ')
        if hasattr(self._get_game_state(), 'friends_names') and\
                self._get_game_state().friends_names.get(gift.user) and\
                self._get_game_state().friends_names.get(gift.user) != u'Без имени' and\
                self._get_game_state().friends_names.get(gift.user) != u'':
            friends_names = self._get_game_state().friends_names.get(gift.user)
            gift_name += u"'" + friends_names + u"'"
        else:
            friends_names = ''
        print gift_name.replace(u'\u0456', u'i').encode("cp866", "ignore")
        if SMS:
            print SMS.replace(u'\u0456', u'i').encode("cp866", "ignore")
        #logger.info(u'' + gift_name) # Доступен 

        CollIt = (hasattr(self._get_game_state().get_state().collectionItems, gift.item[1:]))
        if with_message and gift.msg == u'мутабор':
            pass
        elif moved:
            self.remove_gift_from_game_state(gift)
            return
        elif (gift.user == 'ACTIVE_NPC_LOVE'):
            if not receive_options['active_npc_love']:
                self.remove_gift_from_game_state(gift)
                return
        elif admin_gift:
            if not receive_options['admins']:
                self.remove_gift_from_game_state(gift)
                return
        elif CollIt:
            if (not receive_options['coll']) or\
                    (with_message and not receive_options['with_messages']):
                self.remove_gift_from_game_state(gift)
                return
        elif not free:
            if not receive_options['non_free'] or\
                    (with_message and not receive_options['with_messages']):
                self.remove_gift_from_game_state(gift)
                return
        elif with_message and not receive_options['with_messages']:
            self.remove_gift_from_game_state(gift)
            return

        if _log_message and with_message:
            _message = gift.msg.lower()
            _date = time.strftime('%Y.%m.%d %H:%M:%S ', time.localtime(time.time()))
            self.curuser = self._get_game_state().get_curuser()
            for w in _log_words:
                if w.lower() in _message:
                     # (время) (айди) (сообщение к подарку) (что за подарок)
                    name = u" '" + friends_names + u"'"
                    _text = _date +\
                            ' ' + unicode(gift.user).ljust(20, ' ') +\
                            ' ' + name.ljust(16, ' ') +\
                            u' SMS: ' + gift.msg +\
                            u' Подарок:' + item.name +' '+ str(gift.count) + u'\n'
                    with open('statistics\\messages_' + self.curuser + '.txt', 'a') as f: 
                        f.write(_text.encode('utf-8'))
                    break
        
        #logger.info(u"Принимаю " + gift_name)
        apply_gift_event = GameApplyGiftEvent(GameGift(gift.id))
        self._get_events_sender().send_game_events([apply_gift_event])
        self._get_game_state().add_from_storage(gift.item,gift.count)
        if gift.item.startswith('@C_'):
            if CollIt:
                has = getattr(self._get_game_state().get_state().collectionItems, gift.item[1:])
                setattr(self._get_game_state().get_state().collectionItems, gift.item[1:], has+gift.count)
            else:
                setattr(self._get_game_state().get_state().collectionItems, gift.item[1:], gift.count)

        self.remove_gift_from_game_state(gift)

    def remove_gift_from_game_state(self, gift):
        for current_gift in list(self._get_game_state().get_state().gifts):
            if gift.id == current_gift.id:
                self._get_game_state().get_state().gifts.remove(current_gift)
                break


class AddGiftEventHandler(object):
    def __init__(self, game_state):
        self.__game_state = game_state

    def handle(self, event, log_print):
        gift = event.gift
        self.append_gift_to_game_state(gift, log_print)

    def append_gift_to_game_state(self, gift, log_print):
        if log_print:
            logger.info(u'Получен подарок.')
        self.__game_state.gifts.append(gift)


class FreeGifts(BaseActor):
    def perform_action(self):  # Дарение бесплатки
        if self.if_location_pirate(): return
        if not hasattr (self._get_game_state() , 'playersInfo'): return 1

        par = self.mega().free_gifts_options()
        if not self.check_clock_works(par): return
        SMS = par.get('SMS','')   #  u'Monster'  # по медведю
        other = par.get('other','@CR_16')

        # создаём список уже осчастливленных
        GU_go = [str(i.user) for i in self._get_game_state().get_state().freeGiftUsers if long(i.blockedUntil) > 0]
        if len(GU_go) == len(self._get_game_state().playersInfo): return

        # сообщение по медведю
        if SMS == u'Monster':
            if self._get_game_state().get_location_id() != u'main': return
            SMS = self.sms_monster()
            
        logger.info(u'Уже подарено бесплаток: %d' % (len(GU_go)))

        # создаём список с бесплатками
        freeGifts, limits = self.free_gifts()
        wishes = {n:[] for n in freeGifts}

        for playerInfo in self._get_game_state().playersInfo:
            if str(playerInfo.id) in GU_go: continue

            # список ID бесплатных хотелок соседа
            wish = [w for w in playerInfo.liteGameState.wishlist if w and (w in freeGifts)]
            if not wish:
                wish.append(other)

            for lim in limits.keys():
                if lim in wish:
                    count = 0
                    for i in self._get_game_state().get_state().freeGiftUsers:
                        if i.item == lim: count += 1
                    if count < limits[lim]:
                        wish = lim
                        break
            else:
                wish = [w for w in wish if not w in limits.keys()]
                if not wish:
                    wish.append(other)
                wish = random_number.choice(wish)

            wishes[wish].append(str(playerInfo.id))
            self._get_game_state().get_state().freeGiftUsers.append(
                    dict2obj({u'blockedUntil': u'86400000', u'user': playerInfo.id, u'item':wish})
                    )

        for elem in wishes.keys():
            while len(wishes[elem]) > 0:
                if len(wishes[elem]) >= 500:
                    self.events_send(elem, wishes[elem][:499], SMS)
                    wishes[elem] = wishes[elem][500:]
                else:
                    self.events_send(elem, wishes[elem], SMS)
                    wishes[elem] = []

    def events_send(self, elem, players, SMS):
        event = {
                "userIds":players,
                "msg":SMS,
                "type":"gifts",
                "action":"sendFreeGifts",
                "itemId":elem.lstrip('@')
                }
        self.send([event])
        name = self._get_item_reader().get(elem).name
        if str(len(players))[-1:] == '1' and len(players) != 11:
            logger.info(u'Отослали бесплатку %s %d другу' % (name.ljust(10), len(players)))
        else:
            logger.info(u'Отослали бесплатку %s %d друзьям' % (name.ljust(10), len(players)))
        if len(SMS) > 0:
            print u'C сообщением:', SMS
        time.sleep(0.3)
        self._get_game().handle_all_events()
    
    def sms_monster(self, SMS=u''):  # сообщение по медведю
            monster = self._get_game_location().get_all_objects_by_type('monsterPit')
            if monster and len(monster) > 0 and monster[0].state == 'DIGGING':
                monster_deep = len(monster[0].users)
                if monster_deep > 499:
                    SMS = u'Мишка ' + str(monster_deep) + u' м.!  Очень глубоко. Налетай! (Для продвинутых)'
                elif monster_deep > 99:
                    SMS = u'Мишка ' + str(monster_deep) + u' м.!  Перешёл в платный режим :) Для гурманов.'
                # elif monster_deep > 59:
                    # SMS = u'Мишка ' + str(monster_deep) + u' м.!  Нулевой медведь мало кому интересен.'
            else:
                monster_deep = 0
            print u'Медведь закопан на %d м.' % (monster_deep)
            # print 'monster[0].state =', monster[0].state
            # print 'SMS ', SMS
            return SMS

    def free_gifts(self):  # создаём список с бесплатками
        freeGifts = []
        limits = {}
        for i in self._get_item_reader().get('FREE_GIFTS').freeGifts:
            if hasattr (i, u'startDate') and int(i.startDate) > long(time.time())*1000: continue
            if hasattr (i, u'endDate') and int(i.endDate) < long(time.time())*1000: continue
            if hasattr (i, u'limit'): limits[i.item] = i.limit
            freeGifts.append(i.item)
        #print 'freeGifts', freeGifts
        return freeGifts, limits


class SendColl(BaseActor):
    def perform_action(self):
        if self.if_location_pirate(): return
        par = self.mega().send_coll_options()
        saveCollection = par.get('saveCollection',[])
        send_user = self._get_options()
        if send_user <> None:
            CollIt = obj2dict(self._get_game_state().get_state().collectionItems)
            saveCollection.extend(['C_42','C_29'])
            for item_id in CollIt.keys():
                send = False
                for save in saveCollection:
                    if save in item_id:send = True
                if send: continue
                #print item_id + '\t-\t' + str(CollIt[item_id])
                #{"gift":{"msg":"","item":"C_4_1","count":1,"user":"NNNNN"},"action":"sendGift","type":"gift"}
                if CollIt[item_id] > 0:
                    send_gift = {
                            "item":'@'+item_id,
                            "msg":"",
                            "count":CollIt[item_id],
                            "user":send_user
                            }
                    event = GameSendGift(gift=send_gift)
                    self._get_events_sender().send_game_events([event])
                    #print 'Otpravleno\t'+str(CollIt[item_id])+'\t'+item_id
                    logger.info(u"Отправили %d '%s' пользователю %d"%(CollIt[item_id],self._get_item_reader().get(item_id).name,int(send_user)))
                    self._get_game_state().remove_from_storage('@'+item_id, CollIt[item_id])
                    CollIt[item_id] = 0
            self._get_game_state().get_state().collectionItems = dict2obj(CollIt)


class SendCollections(BaseActor):
    def perform_action(self):
        if self.if_location_pirate(): return
        curuser = str(self._get_game_state().get_curuser())

        par = self.mega().send_collections()
        SMS = par.get('SMS','')
        file = par.get('file','')
        delay = par.get('delay',0)
        only_frends = par.get('only_frends',False)
        users = par.get('users',[])
        friends = self.get_friendsid()

        if file != '':
            try:
                with open(file, 'r') as f:
                    users = eval(f.read())
            except:
                print u'файл рассылки не найден или пустой'
                return
        
        print
        print
        print u'-------------------- Рассылка коллекций --------------------'
        print
        print u'задано:'
        for gifts in users:
            if not gifts[0].isdigit() : continue
            name_coll = self._get_item_reader().get('@' + gifts[1]).name
            print u'%s  %s  %d    - %s' % (gifts[0],gifts[1],gifts[2],name_coll)      
        self.add_log_podarok_ini2(users) 

        saveCollection = ['C_42','C_29']
        text = u''
        for gifts in users:
            if not gifts[0].isdigit() : continue
            user = gifts[0]
            if only_frends and (not ((str(user) in friends) or (long(user) in friends))):
                continue
            gift_id = gifts[1]
            nado = gifts[2]
            name_coll = self._get_item_reader().get('@' + gift_id).name
            
            if gift_id in saveCollection:
                print u'Эту коллекцию нельзя отправить'
                text = u'Эту коллекцию нельзя отправить' + u'\n'
                continue
            
            coll = []
            if 'EGG_' in gift_id:
                coll.append(gift_id)
                min = self._get_game_state().count_in_storage('@' + gift_id)
            elif 'C_' in gift_id:
                for postfix in range(1, 6):
                    coll.append(gift_id + '_' + str(postfix))
                min = nado
                for elem in coll:
                    count_st = self.coll_count_in_storage(elem)
                    #print elem, count_st
                    if count_st < min: min = count_st
            else: continue
            
            if min < nado:
                print u'Не хватает элементов %s для пересылки пользователю %s!!!' % (gift_id,user)
                print u'Необходимо %d, в наличии %d. Не хватает %d шт.' % (nado,min,nado-min)
                text = u'Не хватает элементов ' + gift_id + u' для пересылки пользователю ' + user + u'\n'
                text += u'Необходимо ' + str(nado) + u', в наличии ' + str(min) + u'. Не хватает ' + str(nado-min) + u' шт.' + u'\n'
                continue

            event_first = []
            event_second = []
            for elem in coll:
                send = {
                    "action":"sendGift",
                    "type":"gift",
                    "gift":{
                        "item":'@'+elem,
                        "msg":SMS,
                        "count":nado,
                        "user":user
                        }
                    }
                if event_first == []:
                    event_first.append(send)
                else:
                    event_second.append(send)
        
            otch = u'Отправляем пользователю '
            otch += str(user).ljust(21, ' ')
            otch += self.addName(user).ljust(10, ' ') + u'\n'
            otch += str(nado).rjust(7, ' ')
            otch += u' коллекций '
            otch += gift_id + u' ' + name_coll

            print otch.encode("cp866", "ignore")
            text += otch + u'\n'

            if event_first != []:
                #print event_first
                self._get_events_sender().send_game_events(event_first)
                time.sleep(delay/1000.0)
            if event_second != []:
                #print event_second
                self._get_events_sender().send_game_events(event_second)
                time.sleep(delay/1000.0)

            self.remove_coll_from_storage(coll, nado)
            print

        self.add_log_podarok(text)
        time.sleep(5)
        raw_input('-------------   END   ---------------')
        exit(0)

    def coll_count_in_storage(self, item_id):
        CollIt = obj2dict(self._get_game_state().get_state().collectionItems)
        for itemid in CollIt.keys():
            if itemid == item_id:
                return CollIt[itemid]
        return 0

    def remove_coll_from_storage(self, coll, count):
        CollIt = obj2dict(self._get_game_state().get_state().collectionItems)
        for itemid in CollIt.keys():
            if itemid in coll:
                #print u'удаляем %d шт. %s' % (count, itemid)
                CollIt[itemid] -= count
        self._get_game_state().get_state().collectionItems = dict2obj(CollIt)

    def addName(self, user):
        id = user
        if hasattr(self._get_game_state(), 'friends_names') and self._get_game_state().friends_names.get(id) and self._get_game_state().friends_names.get(id) != u'':
            name = u" '" + self._get_game_state().friends_names.get(id) + u"'"
            name = name.replace(u'\u0456', u'i').encode("UTF-8", "ignore")
            name = unicode(name, "UTF-8")
            #print name.replace(u'\u0456', u'i').encode("cp866", "ignore")
        else: name = u''
        return name

    def add_log_podarok_ini2(self, users):
        with open('statistics\\podarok.txt', 'a') as f:
            _time = datetime.datetime.today().strftime("%Y.%m.%d %H:%M:%S")
            t = u'\n' + u'\n' + _time + u'\n'
            t += u'задано:' + u'\n'
            for gifts in users:
                if not gifts[0].isdigit() : continue
                name_coll = self._get_item_reader().get('@' + gifts[1]).name
                t += gifts[0] + u'  ' + gifts[1] + u'  ' + str(gifts[2]) + u'    - ' + name_coll + u'\n'
            f.write(t.encode("utf-8"))

    def add_log_podarok(self, text):
        with open('statistics\\podarok.txt', 'a') as f:
            f.write(text.encode("UTF-8", "ignore"))

    """    
    def perform_action_v0(self):
        gift_id = "C_16"                 # id коллекции
        SMS = u'подарочек...'            # сообщение
        users = {
                '3689309721258147904':3,
                '3689309721258148238':5,
                '3689309721258149862':10
                }                       # id друга : количество


        #=====================================================================
        print
        print
        print u'-------------------- Рассылка коллекций --------------------'
        print
        name_coll = self._get_item_reader().get('@' + gift_id).name
        print u'выбранная коллекция для отправки:'
        print gift_id, name_coll
        print
        self.add_log_podarok_ini(gift_id,name_coll)
        text = u''

        while(True):
            saveCollection = ['C_42','C_29']
            if gift_id in saveCollection:
                print u'Эту коллекцию нельзя отправить'
                text = u'Эту коллекцию нельзя отправить' + u'\n'
                break

            coll = []
            for postfix in range(1, 6):
                coll.append(gift_id + '_' + str(postfix))

            nado = 0
            for i in users.values():
                nado += i
            #print 'nado', nado

            min = nado
            for elem in coll:
                count_st = self.coll_count_in_storage(elem)
                #print elem, count_st
                if count_st < min: min = count_st
            
            if min < nado:
                print u'Не хватает коллекций для пересылки!!!'
                print u'Необходимо %d, в наличии %d. Не хватает %d шт.' % (nado,min,nado-min)
                text = u'Не хватает коллекций для пересылки!!!' + u'\n'
                text += u'Необходимо ' + str(nado) + u', в наличии ' + str(min) + u'. Не хватает ' + str(nado-min) + u' шт.' + u'\n'
                break

            event_first = []
            event_second = []
            for user in users.keys():
                count = users[user]
                for elem in coll:
                    send = {
                        "action":"sendGift",
                        "type":"gift",
                        "gift":{
                            "item":'@'+elem,
                            "msg":SMS,
                            "count":users[user],
                            "user":user
                            }
                        }
                    if event_first == []:
                        event_first.append(send)
                    else:
                        event_second.append(send)

                otch = u'Отправляем '
                otch += str(users[user]).rjust(7, ' ')
                otch += u' коллекций пользователю '
                otch += str(user).ljust(21, ' ')
                otch += self.addName(user)
                print otch
                text += otch + u'\n'

            if event_first != []:
                pass
                #print event_first
                self._get_events_sender().send_game_events(event_first)
            if event_second != []:
                pass
                #print event_second
                self._get_events_sender().send_game_events(event_second)

            self.remove_coll_from_storage(coll, nado)
            break

        print
        self.add_log_podarok(text)
        time.sleep(5)
        raw_input('-------------   END   ---------------')
        exit(0)


    def add_log_podarok_ini(self, gift_id, name_coll):
        with open('podarok.txt', 'a') as f:
            _time = datetime.datetime.today().strftime("%Y.%m.%d %H:%M:%S")
            t = u'\n' + u'\n' + _time + u'\n'
            t += u'выбранная коллекция для отправки:' + u'\n'
            t += gift_id + u' ' + name_coll + u'\n'
            f.write(t.encode("utf-8"))
    """


class StandartGifts(BaseActor):
    def perform_action(self):
        if self.if_location_pirate(): return
        self.gift_id = '@METAL_SCRAP'    # подарок
        self.count = 1                   # количество
        SMS = u''                        # сообщение
        users = self.get_friendsid()      # все друзья
        #users = ['111','222','333']     # друзья по списку
        users = users[80:]

        if not users: return
        if self.gift_id == '@METAL_SCRAP': self.count = 10 # для металла, количество 10

        storage = self._get_game_state().get_state().storageItems
        for object in storage:
            if object.item == '@' + self.gift_id:
                self.mat_count = object.count
                print self.gift_id, object.count
                break

        self.event = []
        for user in users:
            #"id":users.index(user)+1
            self.event.append({"action":"sendGift","type":"gift","gift":{"count":self.count,"user":user,"item":self.gift_id,"msg":SMS}})
            if user == users[0]:
                logger.info(u'Отправляем подарок '+str(self.gift_id)+' '+str(len(self.event))+u' раз '+str(len(self.event)*self.count)+u' штук')
                self._get_events_sender().send_game_events(self.event)
                object.count -= len(self.event)*self.count
                self.event = []
            if len(self.event) > 19:
                self.events_send(users[0])
                object.count -= len(self.event)*self.count
        self.events_send(users[0])
        print
        raw_input('-------------   END   ---------------')

    def events_send(self, conrol):
        if self.event != []:
            self._get_game_state().resp = False
            logger.info(u'Отправляем подарок '+str(self.gift_id)+' '+str(len(self.event)-1)+u' раз '+str(len(self.event)*self.count)+u' штук')
            #self.event.append({"type":"players","action":"getInfo","players":[conrol]})
            self._get_events_sender().send_game_events(self.event)
            event_control = {"type":"players","action":"getInfo","players":[conrol]}
            self._get_events_sender().send_game_events([event_control])
            self.response_wait()
            self.event = []

    def response_wait(self):
        #self._get_game().handle_all_events()
        print 'resp', self._get_game_state().resp
        while not self._get_game_state().resp:
            #print u'\b.',
            if 'SERVER_TOO_MANY_GIFTS_LIMIT' in self._get_game().alerts:
                print u'Лимит...'
                self._get_game_state().resp = True
                time.sleep(1)
                self.limit = True
            else:
                print u'\b.',
                #self._get_events_sender().send_game_events([])
                self._get_game().handle_all_events()
                time.sleep(0.2)
        print 'resp', self._get_game_state().resp
        time.sleep(1)

    # {"gift":{"msg":"","user":"8997900496038913535","count":1,"item":"@CR_16"},"id":14,"type":"gift","action":"sendGift"},
    # {"gift":{"msg":"","user":"8036052199871747874","count":1,"item":"@CR_16"},"id":15,"type":"gift","action":"sendGift"},
    # {"gift":{"msg":"","user":"17845066894669387658","count":1,"item":"@CR_16"},"id":16,"type":"gift","action":"sendGift"
    pass

# бесплатки ruslanische
class GiftSenderBot(BaseActor):
    def __init__(self, *args):
        super(GiftSenderBot, self).__init__(*args)
        # список из ID бесплатных подарков
        self.free_gifts_ids = [record['item'] for record in self.stateProcessor.get_item_by_id(u'FREE_GIFTS').get(u'freeGifts', [])]
        # список из бесплатных подарков
        self.free_gifts = [self.stateProcessor.get_item_by_id(gift) for gift in self.free_gifts_ids]

    def perform_action(self):
        if self.if_location_pirate(): return
        self.send_free_gifts()

    def friend_without_gifts(self):
        freeGiftUsers = self.game_state['state']['freeGiftUsers']
        for user in list(freeGiftUsers):
            if self.gameTimer.has_elapsed(user['blockedUntil']):
                freeGiftUsers.remove(user)
        blocked_users = [user['user'] for user in freeGiftUsers]
        # список соседей, которым сегодня не дарили бесплатного подарка
        friends_without_gift = filter(lambda(x): x[u'id'] not in blocked_users, self.friends)
        return friends_without_gift

    def friend_free_gift_wishes(self, friend):
        # список хотелок соседа
        friend_wishlist = friend.get(u'liteGameState', {}).get(u'wishlist', [])
        # список ID бесплатных хотелок соседа
        friend_free_wishlist_ids = [wish.lstrip('@') for wish in friend_wishlist if wish in self.free_gifts_ids]
        # список бесплатных хотелок соседа
        friend_free_wishlist_items = [wish_item for wish_item in self.free_gifts if wish_item['id'] in friend_free_wishlist_ids]
        return friend_free_wishlist_items

    def friends_who_wants_free_gift(self, gift):
        return [friend for friend in self.friend_without_gifts if gift in self.friend_free_gift_wishes(friend)]

    def send_free_gifts(self):
        sended_gifts = 0
        # дарим бесплатные подарки соседям по фильтру
        for free_gift in self.free_gifts:
            friends = self.friends_who_wants_free_gift(free_gift)
            if friends:
                sended_gifts += len(friends)
                friends_ids = [friend[u'id'] for friend in friends]
                # помечаем соседей, что подарки им подарены в этот день
                for friend_id in friends_ids:
                    self.game_state['state']['freeGiftUsers'].append({u'user': friend_id, u'blockedUntil': self.gameTimer.client_time_next_day()})
                send_event = {
                    u'type': u'gifts',
                    u'msg': self.settings.message_for_gifts,
                    u'userIds': friends_ids,
                    u'action': u'sendFreeGifts',
                    u'itemId': free_gift['id']
                }
                self.send_event(send_event)
        # дарим случайные подарки остальным соседям
        friends = self.friend_without_gifts
        if friends:
            sended_gifts += len(friends)
            wish_item = random.choice(self.free_gifts)
            friends_ids = [friend[u'id'] for friend in friends]
            # помечаем соседей, что подарки им подарены в этот день
            for friend_id in friends_ids:
                self.game_state['state']['freeGiftUsers'].append({u'user': friend_id, u'blockedUntil': self.gameTimer.client_time_next_day()})
            send_event = {
                u'type': u'gifts',
                u'msg': self.settings.message_for_gifts,
                u'userIds': friends_ids,
                u'action': u'sendFreeGifts',
                u'itemId': wish_item['id']
            }
            self.send_event(send_event)
        if sended_gifts > 0:
            logger.info(u"Подарено %s бесплатных подарков" % sended_gifts)


class GiftsToFake(BaseActor):
    def perform_action(self):
        if self.if_location_pirate(): return
        if self.check_midnight(): return

        par = self.mega().send_gifts2fake()
        if not self.check_clock_works(par): return
        SMS = par.get('SMS','')
        delay = par.get('delay',0)
        only_frends = par.get('only_frends',False)
        data = par.get('data',[{'id':[],'gifts':{}}])

        #=====================================================================

        friends = self.get_friendsid()
        curuser = str(self._get_game_state().get_curuser())
        self.read_gifts2fake_time(curuser)
        self.dat = datetime.date.today().strftime("%Y.%m.%d")
        action = False

        for spis in data:
            if (not spis['id']) or (not spis['gifts']): continue
            ids = self.check_time(spis['id'])
            gifts = spis['gifts']
            msg = spis.get('SMS',SMS)
            for user in ids:
                if only_frends and (not ((str(user) in friends) or (long(user) in friends))):
                    continue
                for g_item in gifts.keys():
                    has = self.has_in(g_item,gifts[g_item])
                    if has == 0:
                        gifts.pop(g_item)
                        continue
                    if has < gifts[g_item]:
                        gifts[g_item] = has

                    event = []
                    if g_item.startswith('C_') and len(g_item) < 5:
                        for num in range(1,6):
                            event.append({"action":"sendGift","type":"gift","gift":{"count":has,"user":str(user),"item":'@'+g_item+'_'+str(num),"msg":msg}})
                    else:
                        event.append({"action":"sendGift","type":"gift","gift":{"count":has,"user":str(user),"item":'@'+g_item,"msg":msg}})
                    self.send(event)
                    action = True
                    self._get_game_state().gifts2fake_time[str(user)] = self.dat
                    name = self._get_item_reader().get(g_item).name
                    logger.info(u'Отправляем подарок ' + name + '  ' + str(has) + u' шт. другу ' + str(user))
                    time.sleep(delay/1000.0)

        if action:
            with open('statistics\\'+curuser+'\gifts2fake_time.txt', 'w') as f:
                f.write(str(self._get_game_state().gifts2fake_time))

    def check_midnight(self, rand_min=random_number.randint(6,59)):
        h = int(datetime.datetime.today().strftime("%H"))
        m = int(datetime.datetime.today().strftime("%M"))
        if (h == 23 and m > 54) or (h == 0 and (m < 6 or m < rand_min)):
            return True
        return False


    def has_in(self,item,count):
        if item.startswith('C_'):
            collectionItems = self._get_game_state().get_state().collectionItems
            print 'item', item
            if len(item) < 5:  # коллекция в сборе
                # print u'коллекция в сборе'
                coll = []
                for num in range(1,6):
                    if hasattr(self._get_game_state().get_state().collectionItems, item + '_' + str(num)):
                        coll.append(getattr(self._get_game_state().get_state().collectionItems, item + '_' + str(num)))
                if len(coll) < 5: return 0
                has = min(min(coll), count)
                if has:
                    for num in range(1,6):
                        self._get_game_state().remove_from_storage(item + '_' + str(num), has)
                        est = getattr(self._get_game_state().get_state().collectionItems, item + '_' + str(num))
                        setattr(self._get_game_state().get_state().collectionItems, item + '_' + str(num), est-has)
            else:  # отдельный элемент
                # print u'отдельный элемент'
                has = 0 if not hasattr(collectionItems,item) else getattr(collectionItems,item)
                has = min(has, count)
                if has:
                    self._get_game_state().remove_from_storage(item, has)
                    est = getattr(self._get_game_state().get_state().collectionItems, item)
                    setattr(self._get_game_state().get_state().collectionItems, item, est-has)
        else:
            # print u'предмет'
            has = min(self._get_game_state().count_in_storage(item), count)
            self._get_game_state().remove_from_storage(item, has)
        return has

    def read_gifts2fake_time(self,curuser):
        if not hasattr(self._get_game_state(), 'gifts2fake_time'):
            try:
                with open('statistics\\'+curuser+'\gifts2fake_time.txt', 'r') as f:
                    self._get_game_state().gifts2fake_time = eval(f.read())
            except:
                self._get_game_state().gifts2fake_time = {}

    def check_time(self,ids):
        times = self._get_game_state().gifts2fake_time
        out_id = []
        for id in ids:
            if (id in times.keys()) and times[id] == self.dat: continue
            out_id.append(id)
        return out_id
