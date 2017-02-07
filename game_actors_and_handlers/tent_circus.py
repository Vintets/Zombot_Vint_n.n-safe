# coding=utf-8
import logging
from game_state.base import BaseActor
logger = logging.getLogger(__name__)


class BowReceiverBot(BaseActor):
    def perform_action(self):  # железные тыквы # бантики
        if self.if_location_pirate(): return
        bows = self._get_game_location().get_all_objects_by_type('halloweenTower')

        curuser = str(self._get_game_state().get_curuser())
        if not hasattr(self._get_game_state(), 'airplane_user'):
            try:
                with open('statistics\\'+curuser+'\\airplane_user.txt', 'r') as f:
                    self._get_game_state().airplane_user = eval(f.read())
            except:
                self._get_game_state().airplane_user = []

        self._event = []
        self.bow_count = 0
        for bow in bows:
            if bow.item == '@B_SAKURA': # '@B_MAUSOLEUM' '@B_TENT_CIRCUS'
                for i in bow.users:
                    if i.itemId != u'SAKURA_PACK_DEFAULT': continue # только бесплатные
                    self._get_game_state().airplane_user.append(i.id)
                    self._event.append({"extraId":i.id,"itemId":i.itemId,"action":"trick","type":"item","objId":bow.id})
                    name_user = self.addName(i.id)
                    sp_n = u' '*(14-len(name_user))
                    name = unicode(i.id).ljust(20, " ") + name_user + sp_n
                    # if i.itemId == u'BOW_PACK_DEFAULT':
                        # count = 1
                    # elif i.itemId == u'BOW_PACK_SMALL':
                        # count = 3
                    # elif i.itemId == u'BOW_PACK_MEDIUM':
                        # count = 10
                    # if i.itemId == u'METALL_PACK_DEFAULT':
                        # count = 1
                    # elif i.itemId == u'METALL_PACK_SMALL':
                        # count = 5
                    # elif i.itemId == u'METALL_PACK_MEDIUM':
                        # count = 15
                    # elif i.itemId == u'METALL_PACK_LARGE':
                        # count = 30
                    if i.itemId == u'SAKURA_PACK_DEFAULT':
                        count = 1
                    elif i.itemId == u'SAKURA_PACK_SMALL':
                        count = 5
                    elif i.itemId == u'SAKURA_PACK_MEDIUM':
                        count = 15
                    elif i.itemId == u'SAKURA_PACK_LARGE':
                        count = 30 
                    # sms = u'Пользователь ' + name + u' положил Вишневый цвет: ' + unicode(count)
                    # logger.info(u'Пользователь %s положил Вишневый цвет: %d' % (name, count))
                    sms = u'Пользователь ' + name + u' положил Вишневый цвет: ' + unicode(count)
                    logger.info(u'Пользователь %s положил Вишневый цвет: %d' % (name, count))
                    with open('statistics\\'+curuser+'\\action_frends.txt', 'a') as f:
                        sms += u'\n'
                        f.write(sms.encode("utf-8"))
                    self.bow_count += count
                    if len(self._event) > 499:
                        self.events_send(curuser)
                bow.users = []
                self.events_send(curuser)

    def events_send(self, curuser):
        if self._event != []:
            self._get_events_sender().send_game_events(self._event)
            # добавляем на склад
            # self._get_game_state().add_from_storage('@CR_153',self.bow_count)
            self._get_game_state().add_from_storage("@CR_198",self.bow_count)
            with open('statistics\\'+curuser+'\\airplane_user.txt', 'w') as f:
                f.write(str(self._get_game_state().airplane_user))
            print
            if str(len(self._event))[-1:] == '1' and len(self._event) !=11:
                if str(self.bow_count)[-1:] == '1' and self.bow_count !=11:
                    logger.info(u'Собрали %d Вишневый цвет   от %d друга' % (self.bow_count, len(self._event)))
                elif 1 < int(str(self.bow_count)[-1:]) < 5 and self.bow_count < 5 and self.bow_count > 20:
                    logger.info(u'Собрали %d Вишневых цвета от %d друга' % (self.bow_count, len(self._event)))
                else:
                    logger.info(u'Собрали %d Вишневых цвета от %d друга' % (self.bow_count, len(self._event)))
            else:
                if str(self.bow_count)[-1:] == '1' and self.bow_count !=11:
                    logger.info(u'Собрали %d Вишневый цвет   от %d друзей' % (self.bow_count, len(self._event)))
                elif 1 < int(str(self.bow_count)[-1:]) < 5 and self.bow_count < 5 and self.bow_count > 20:
                    logger.info(u'Собрали %d Вишневых цвета от %d друзей' % (self.bow_count, len(self._event)))
                else:
                    logger.info(u'Собрали %d Вишневых цвета от %d друзей' % (self.bow_count, len(self._event)))
            self._event = []
            self.bow_count = 0
            
    def addName(self, id):
        if hasattr(self._get_game_state(), 'friends_names') and self._get_game_state().friends_names.get(id) and self._get_game_state().friends_names.get(id) != u'Без имени':
            name = u" '" + self._get_game_state().friends_names.get(id) + u"'"
            name = name.replace(u'\u0456', u'i').encode("UTF-8", "ignore")
            name = unicode(name, "UTF-8")
            #print name.replace(u'\u0456', u'i').encode("cp866", "ignore")
        else: name = u''
        return name

"""
print (u'Собрали %(+4)d бантиков у %(+4)d друзей') % (20, 7)
u'remoteTrickTreating': [
{u'count': 0L, u'date': u'-14202657', u'user': u'17823741170892930057', u'item': u'@CR_153'}, 
{u'count': 0L, u'date': u'-14087056', u'user': u'11628291596603049922', u'item': u'@CR_153'},

           
{"type":"bellBox","id":"BOW_PACK_DEFAULT","name":"Бабочка","level":1,"buyCoins":0,"buyCash":0,"openCash":0,"gift":false,"xp":1,"shopImage":"crops/m_bow_tie.png","count":1,"item":"@CR_153","expire":43200,"disabled":false},
{"type":"bellBox","id":"BOW_PACK_SMALL","name":"3 Бабочки","level":1,"buyCoins":0,"buyCash":1,"openCash":0,"gift":true,"xp":1,"shopImage":"crops/m_bow_tie_3.png","count":3,"item":"@CR_153","disabled":false},
{"type":"bellBox","id":"BOW_PACK_MEDIUM","name":"10 Бабочек","level":1,"buyCoins":0,"buyCash":4,"openCash":0,"gift":true,"xp":1,"shopImage":"crops/m_bow_tie_5.png","count":10,"item":"@CR_153","disabled":false}

принять
{"extraId":"864730088123287177","itemId":"BOW_PACK_DEFAULT","action":"trick","type":"item","objId":24578}

FIND:  @B_TENT_CIRCUS   id =  24578
u'level': 0L, u'item': u'@B_TENT_CIRCUS', u'y': 70L, u'x': 14L, u'type': u'halloweenTower', u'id': 24578L, u'rotate': 0L, u'users':
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'38559575', u'id': u'6064366433377019163'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire':u'38637626', u'id': u'7121282654775318802'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'38832674', u'id': u'15818464092022489540'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'38901416', u'id': u'14055452232076276468'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'38977137', u'id': u'15014405591850557706'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39026125', u'id': u'4291172554993809160'}, 
{u'itemId': u'BOW_PACK_SMALL', u'id': u'4291172554993809160'}, 
{u'itemId': u'BOW_PACK_SMALL', u'id': u'4291172554993809160'}, 
{u'itemId': u'BOW_PACK_SMALL', u'id': u'4291172554993809160'}, 
{u'itemId': u'BOW_PACK_SMALL', u'id': u'4291172554993809160'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39129754', u'id':u'6964404519889477693'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39199436', u'id': u'3204314554139751192'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39318932', u'id': u'13457249625356096495'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39326238', u'id': u'5324694677519624602'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39328425', u'id': u'1861431567869250035'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39390312', u'id': u'7539667698249407867'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39464098', u'id': u'14943752851513071980'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39538459', u'id': u'4319975567792665443'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39684203', u'id': u'8983536472031539027'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39821616', u'id': u'13198999224975962564'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39869465', u'id': u'5612401879551889720'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'39931771', u'id': u'10302456478223098439'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40018473', u'id': u'11163803197376197496'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40026916', u'id': u'14812428810802350725'}, 
{u'itemId':u'BOW_PACK_SMALL', u'id': u'14812428810802350725'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40036679', u'id': u'3715048854790423074'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40068555', u'id': u'7936889122688061229'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40114102', u'id': u'4205058517012598771'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40159272', u'id': u'6539340140833976659'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40185017', u'id': u'17933220020014584008'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40200956', u'id': u'16468904229467526011'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40220400', u'id': u'14828874244573620095'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40373372', u'id': u'6581770191535967959'}, 
{u'itemId': u'BOW_PACK_DEFAULT',u'expire': u'40388933', u'id': u'9537326544119913665'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40509894', u'id': u'16201705050218677895'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40557860', u'id': u'3001198562846513236'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40639704', u'id': u'15532422456862347017'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40786780', u'id': u'8282628093369873249'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40847098', u'id': u'17463542978383975773'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'40889369', u'id': u'9141526217034386562'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41073972', u'id': u'1724896099377098400'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41130189', u'id': u'8227292692505829961'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41180773', u'id': u'7788823235118273698'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41231935', u'id': u'6888885388629123262'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41432916', u'id': u'10332266811119081784'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41490138', u'id': u'7445785979369703000'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41516948', u'id': u'6006182739190644564'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41532777', u'id': u'14080429193704954208'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41612957', u'id': u'12127301101092720687'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41722300', u'id': u'8151186094947845259'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41757892', u'id': u'15638996418232445734'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41836353', u'id': u'12669874990874077327'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41865795', u'id': u'13182473161417640576'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41866621', u'id': u'2758536737599680996'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'41938877', u'id': u'8620166768058098492'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'42156396', u'id': u'11221137759313638187'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'42190034', u'id': u'9011158480167868632'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'42233067', u'id': u'13713850230407340748'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'42250708', u'id': u'4652042415941722970'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'42265169', u'id': u'14506167444300188190'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'42267934', u'id': u'11641298102031355593'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'42273152', u'id': u'2841381438208214941'},
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'42277623', u'id': u'117913924970578491'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'42401735', u'id': u'17405731893743100309'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'43048472', u'id': u'332544315730299892'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'43050417', u'id': u'7363935275831159180'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire':u'43119395', u'id': u'11204450342418518713'}, 
{u'itemId': u'BOW_PACK_DEFAULT', u'expire': u'43137318', u'id': u'6296368708255388417'}
""" 
