# -*- coding: utf-8 -*-
from game_state.connection import Connection
from game_state.settings import Settings
import re
import os.path
#sys.path.append('./API')
#import odnoklassniki.api
#import json
import vkontakte.api
import requests.api
import time
import simplejson
from hashlib import md5
from game_state.game_types import GameSTART, GameInfo
# from game_state.pymymailru import PyMyMailRu, ApiError
from _mega_options import MegaOptions
from game_actors_and_handlers.active_user import FinalReportUserMR
from game_state.game_event import dict2obj, obj2dict


class MR():
    def __init__(self, credentials):
        self._credentials = credentials

    def getAppParams(self, app_id, session_cookies=None):
        if session_cookies is None:
            session_cookies = self._getSessionCookies()
#        mr = Connection('http://my.mail.ru/apps/' + str(app_id))
#        UrlRedirect1 = mr.sendRequestNoRedirect(None, cookies=session_cookies)
#        print 'UrlRedirect 1 = ', UrlRedirect1
        mr = Connection('http://auth.mail.ru/sdc')
        data = {'from':'http://my.mail.ru/apps/609744'}
        UrlRedirect2 = mr.sendRequestNoRedirect(data, cookies=session_cookies)
#        print 'UrlRedirect 2 = ', UrlRedirect2
        mr = Connection('http://my.mail.ru/sdc')
#        data = {'token':UrlRedirect2[28:]}
        data = {'token':UrlRedirect2.split('=')[1]}
#        print 'data-token = ', data
#        self.__tokenMR = UrlRedirect2.split('=')[1] 
        session_cookies3 = mr.sendRequestNoRedirect(data, cookies=session_cookies, getCookies=True)               
#        print 'session_cookies3 = ', session_cookies3
        
        session_cookies_sdc = (session_cookies3.output(attrs=[],
                                                  header='', sep=';')) 
#        print 'session_cookies_sdc = ', session_cookies_sdc
        session_cookies += ('; ' + session_cookies_sdc)
        self.__session_cookies = session_cookies
#        self._credentials.setSessionCookies(session_cookies)
        
        mr = Connection('http://my.mail.ru/apps/' + str(app_id))
        html = mr.sendRequest(None, cookies=session_cookies)         
        params = None
        if html:
            #open('html.txt', 'a').write(html.encode('utf-8'))
            matcher = re.compile('.*zombiefarm.html\?(.*?)"')
            for line in html.split('\n'):
                match = matcher.match(line)
                if match is not None:
                    params = match.group(1)
                    break
            if params is not None:
                pairs = params.split('&')
                params = {}
                for pair in pairs:
                    key = pair.split('=')[0]
                    value = pair.split('=')[1]
                    params[key] = value
                    #print key, value
        return params

    def get_game_params(self):
        params = self.getAppParams('609744')
        #print 'params1 = ', params
        params['ext_perm']=params['ext_perm'].replace('%2C',',')
        self.__game_api_user_id = params['oid']
        self.__game_auth_key = params['sig']
        self.__auth_key = params['authentication_key']
        self.__api_access_token = params['session_key']
        self.__window_id = params['window_id']
        game_url = 'https://jmr.shadowlands.ru/zombiemr/go'
        connection = Connection(game_url)
        self.__params = params
        #print 'params = ', params
        self._save_key()
        return (self.__game_api_user_id, self.__game_auth_key, self.__api_access_token, connection)

    def _save_key(self):
        file = 'statistics\\auth_key.txt'
        curuser = str(self.__game_api_user_id)
        spisok = self.reading(file)
        for data in spisok:
            if data.split(' = ')[0] == curuser:
                return
        info = curuser + u' = auth_key: ' + self.__game_auth_key +\
                u', session_key: ' + self.__api_access_token +\
                u', authentication_key: ' + self.__auth_key
        spisok.append(info)
        text = '\n'.join(spisok)
        with open(file, 'w') as f:
           f.write(text.encode('utf-8'))

    def reading(self, file):
        if not os.path.isdir('statistics'): os.makedirs('statistics')
        if os.path.isfile(file):
            with open(file, 'r') as f:
                data = f.read()
            spisok = data.split('\n')
            if spisok.count('') > 0:
                spisok.remove('')
        else:
            spisok = []
        return spisok

    def get_time_key(self):
        #print self.__params
        del self.__params['sig']
        return '&'.join([k + '=' + v for k, v in self.__params.iteritems()])

    def create_start_command(self,server_time, client_time, curuser):
        self.curuser = curuser
        command = GameSTART(lang=u'en', info=self._getUserInfo(),
                      ad=u'search', serverTime=server_time,
                      clientTime=client_time)
        self.__mega = MegaOptions(self.curuser)
        
        # получаем список друзей общий
        #self._getFriendsAllMR0()
        
        # получаем список друзей общий ПОЛНАя инфа
        par = self.__mega.actor_options()
        for ap1 in par:
            if issubclass(ap1, FinalReportUserMR):
                self._getFriendsAllMR1()
                break
        
        # получаем список друзей с ЗФ
        self.friendsid = self._getFriendsListMR2()
        return command, self.friendsid

    def _getUserInfo(self):
        '''
        TODO returns user info using mailru api
        '''
        return GameInfo()

    def _getFriendsListMR(self):  # MR
        """
        friendsid = []
        xfile = open('ID Frends.txt', 'r')
        for line in xfile.readlines():
            if line != '':
                if line[-1] == '\n':
                    friendsid.append(line[:-1])
                else: friendsid.append(line)
        xfile.close()
        """
        friendsid = eval(open('ID Frends.txt').read())
        return friendsid
        
    def _getFriendsListMR2(self):  # MR
        friendsid = []
        #return friendsid
        print u'Загружаем список друзей...'
        offset = 0
        while True:
            post = {
                'method': 'friends.getAppUsers',
                'app_id': '609744',
                'offset' : str(offset),
                'session_key': self.__api_access_token
                }
            post_keys = sorted(post.keys())
            param_str = "".join(["%s=%s" % (str(key), vkontakte.api._encode(post[key])) for key in post_keys])
            param_str = self.__game_api_user_id + param_str + u'5cbd867117243d62af914948498eb3de'
            sign = md5(param_str).hexdigest().lower()
            post.update({'sig': sign})
            BASE_URL = Connection('http://www.appsmail.ru/platform/api')

            resp_fr = BASE_URL.sendRequest(post, cookies=self.__session_cookies)
            while resp_fr == None:
                print u'Друзья заедают... попробуем ещё раз'
                time.sleep(0.5)
                resp_fr = BASE_URL.sendRequest(post, cookies=self.__session_cookies)
            add = eval(resp_fr) 
            #add = eval(BASE_URL.sendRequest(post, cookies=self.__session_cookies))
            print 'load ', len(add)
            friendsid.extend(add)
            offset += 1000
            if len(add) < 1000:
                break
            else:
                time.sleep(0.34)

        friendsid = list(set(friendsid))
        print (u'Всего друзей в списке: %s'%str(len(friendsid))).encode('cp866')
        return friendsid
        
    def _getFriendsAllMR0(self):  # All MR
        friends_all_id = []
        #return friends_all_id
        offset = 0
        while True:
            post = {
                'method': 'friends.get',
                'app_id': '609744',
                'offset' : str(offset),
                'session_key': self.__api_access_token
                }
            post_keys = sorted(post.keys())
            param_str = "".join(["%s=%s" % (str(key), vkontakte.api._encode(post[key])) for key in post_keys])
            param_str = self.__game_api_user_id + param_str + u'5cbd867117243d62af914948498eb3de'
            sign = md5(param_str).hexdigest().lower()
            post.update({'sig': sign})
            BASE_URL = Connection('http://www.appsmail.ru/platform/api')
                
            resp_fr = BASE_URL.sendRequest(post, cookies=self.__session_cookies)
            while resp_fr == None:
                print u'Друзья заедают... попробуем ещё раз'
                time.sleep(0.5)
                resp_fr = BASE_URL.sendRequest(post, cookies=self.__session_cookies)
            add = eval(resp_fr) 
            print 'load MR', len(add)
            friends_all_id.extend(add)
            offset += 1000
            if len(add) < 1000:
                break
            else:
                time.sleep(0.34)
                
        print (u'Друзей в Моём Мире: %s'%str(len(friends_all_id))).encode('cp866')
        with open('statistics\\'+self.curuser+'friends_all.txt', 'w') as f:
            f.write(friends_all_id.encode("UTF-8", "ignore"))
        return friends_all_id
        
    def _getFriendsAllMR1(self):  # All MR
        friends_all_id = {}
        #return friends_all_id
        null = '0'
        offset = 0
        ex_fr = 0
        while ex_fr == 0:
            post = {
                'ext':'1',
                'method': 'friends.get',
                'app_id': '609744',
                'offset' : str(offset),
                'session_key': self.__api_access_token
                }
            post_keys = sorted(post.keys())
            param_str = "".join(["%s=%s" % (str(key), vkontakte.api._encode(post[key])) for key in post_keys])
            param_str = self.__game_api_user_id + param_str + u'5cbd867117243d62af914948498eb3de'
            sign = md5(param_str).hexdigest().lower()
            post.update({'sig': sign})
            BASE_URL = Connection('http://www.appsmail.ru/platform/api')
                
            resp_fr = BASE_URL.sendRequest(post, cookies=self.__session_cookies)
            while resp_fr == None:
                print u'Друзья заедают... попробуем ещё раз'
                time.sleep(0.5)
                resp_fr = BASE_URL.sendRequest(post, cookies=self.__session_cookies)
            # with open('response.txt', 'w') as f:
                # f.write(resp_fr.encode("UTF-8", "ignore"))
            add = eval(resp_fr)
            print 'load MR', len(add)
            if len(add) == 0:
                ex_fr = 1
            else:
                time.sleep(0.34)
                offset += 1000
                #friends_all_id.extend(add)
                for us in add:  
                    new = {u"link":us["link"], u"first_name":self._correct(us["first_name"]), u"last_name":self._correct(us["last_name"]), u"nick":self._correct(us["nick"]), u"app_installed":us["app_installed"], u"last_visit":us["last_visit"]}
                    friends_all_id[us["uid"]] = new
        print (u'Друзей в Моём Мире: %s'%str(len(friends_all_id))).encode('cp866')
        with open('statistics\\'+self.curuser+'\\friends_all_info.txt', 'w') as f:
            #f.write(unicode(friends_all_id))
            text = simplejson.dumps(friends_all_id, ensure_ascii=False)
            f.write(text.encode("UTF-8", "ignore"))
        return friends_all_id

    def _correct(self, name_):
        # print 'type name_', type(name_)
        # print 'name_',  name_
        while '{' in name_ or '}' in name_ or '[' in name_ or ']' in name_ or '^' in name_:
            for l in '{}[]^':
                name_ = name_.replace(l, '')
        if '\u0456' in name_:
            name_ = name_.replace('\u0456', u'i')
        return name_        
        
    def _getFriendsId(self): # VK
        api = vkontakte.api.API(token=self.__api_access_token)
        info = api.friends.getAppUsers(format='json')
        return info    
        
    def _getFriendsListOK(self): # OK
        post = {
            'new_sig': 1,
            'session_key': self.__params['session_key'],
            'application_key': self.__params['application_key'],
            'format': 'Json'
            }
        post_keys = sorted(post.keys())
        param_str = "".join(["%s=%s" % (str(key), vkontakte.api._encode(post[key])) for key in post_keys])
        param_str += self.__params['session_secret_key']
        sign = md5(param_str).hexdigest().lower()
        post.update({'sig': sign})
        info = requests.post('http://api.odnoklassniki.ru/api/friends/getAppUsers', data=post, cookies=self.str2dict(self._credentials.getSessionCookies())).json()['uids']
        #print(info)
        return info

    def _validateSessionCookies0000(self, session_cookies):
        valid = False
        if session_cookies is not None:
            valid = self.getAppParams(609744,session_cookies) is not None
        return valid
        
    def _validateSessionCookies(self, session_cookies):
        valid = False
        if session_cookies is not None:
            mr = Connection('http://my.mail.ru/apps/609744')
            html = mr.sendRequest(None, cookies=session_cookies)         
            params = None
            if html:
                #open('html.txt', 'a').write(html.encode('utf-8'))
                matcher = re.compile('.*zombiefarm.html\?(.*?)"')
                for line in html.split('\n'):
                    match = matcher.match(line)
                    if match is not None:
                        params = match.group(1)
                        break
                if params is not None:
                    pairs = params.split('&')
                    params = {}
                    for pair in pairs:
                        key = pair.split('=')[0]
                        value = pair.split('=')[1]
                        params[key] = value
                        #print key, value
            valid = params is not None
        return valid

    def _getSessionCookies(self):
        session_cookies = self._credentials.getSessionCookies()
        cookies_are_valid = self._validateSessionCookies(session_cookies)
        # print 'cookies_are_valid = ', cookies_are_valid
        if not cookies_are_valid:
            username = self._credentials.getUserEmail()
            password = self._credentials.getUserPassword()
            # print 'New login!'
            post = {
                    'post':'',
                    'Login': username.split('@')[0],
                    'Domain': username.split('@')[1],
                    'Password': password,
                    'level':'0'}
            # print 'post =', post
            # get = 'https://auth.mail.ru/cgi-bin/auth?post=&' +\
                    # 'Login=' + username.split('@')[0] +\
                    # '&Domain=' + username.split('@')[1] +\
                    # '&Password=' + password
            # print 'get =', get
            
            # реквест POST
            # session_cookies = requests.post('https://auth.mail.ru/cgi-bin/auth', data=post, allow_redirects=False).cookies

            # реквест GET
            # session_cookies = requests.get(get, allow_redirects=False).cookies
            # print 'session_cookies1 = ', session_cookies
            # print
            # print session_cookies.get_dict('.mail.ru')
            # print session_cookies.get_dict('.auth.mail.ru')

            
            # GET
            # mr = Connection(get)
            # session_cookies = mr.sendRequestNoRedirect(getCookies=True)
            
            
            mr = Connection('https://auth.mail.ru/cgi-bin/auth')
            session_cookies = mr.sendRequestNoRedirect(post, getCookies=True)
            # session_cookies = mr.sendRequest(post, getCookies=True)
            # print 'session_cookies1 = ', session_cookies
            # open('remont_log.txt', 'a').write('session_cookies1 = '+str(session_cookies)+"\n"+"\n")
            session_cookies = (
                               session_cookies.output(attrs=[],
                                                      header='', sep=';'))
            self._credentials.setSessionCookies(session_cookies)
        return session_cookies
