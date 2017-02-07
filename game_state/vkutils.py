# -*- coding: utf-8 -*-
from game_state.connection import Connection
from game_state.settings import Settings
import re
import json
from game_state.game_types import GameSTART, GameInfo
import os.path
import sys
import vkontakte.api
import simplejson
import time
from _mega_options import MegaOptions
from game_actors_and_handlers.active_user import FinalReportUserVK



class VK():
    def __init__(self, credentials):
        self._credentials = credentials

    def getAppParams(self, app_id, session_cookies=None):
        if session_cookies is None:
            session_cookies = self._getSessionCookies()
        vk = Connection('https://vk.com/app' + str(app_id))
        html = vk.sendRequest(None, cookies=session_cookies)
        #open('html.tmp','w').write(html.encode('utf-8'))
        params = None
        if html:
            matcher = re.compile('.*var params = (.*);$')
            for line in html.split('\n'):
                match = matcher.match(line)
                if match is not None:
                    params = match.group(1)
                    break
            if params is not None:
                #print json.loads(params)
                #return json.loads(params)
                try:
                    return json.loads(params)
                except:
                    print 'Vk auth failed for app%s' % app_id
                    return None
        return params

    def get_game_params(self):
        params = self.getAppParams('612925')
        self.__game_api_user_id = params['viewer_id']
        game_auth_key = params['auth_key']
        self.__api_access_token = params['access_token']
        game_url = 'https://java.shadowlands.ru/zombievk/go'
        connection = Connection(game_url)
        self._save_key(game_auth_key)
        return (self.__game_api_user_id, game_auth_key, self.__api_access_token, connection)

    def get_time_key(self):
        return None

    def _save_key(self, game_auth_key):
        file = 'statistics\\auth_key.txt'
        curuser = str(self.__game_api_user_id)
        spisok = self.reading(file)
        for data in spisok:
            if data.split(' = ')[0] == curuser:
                return
        info = curuser + u' = auth_key: ' + game_auth_key + u', access_token: ' + self.__api_access_token
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

    def create_start_command(self,server_time, client_time, curuser):
        self.curuser = curuser
        command = GameSTART(lang=u'en', info=self._getUserInfo(),
                      ad=u'user_apps', serverTime=server_time,
                      clientTime=client_time)
        self.__mega = MegaOptions(self.curuser)
        friendsid = self._getFriendsId()
        par = self.__mega.actor_options()
        for ap1 in par:
            if issubclass(ap1, FinalReportUserVK):
                self._getFriendsAllVK(friendsid)
                break
        return command, friendsid

    def _getUserInfo(self):
        '''
        returns user info using vk api
        '''
        # get vk user info
        api = vkontakte.api.API(token=self.__api_access_token)
        info = api.getProfiles(
            uids=self.__game_api_user_id, format='json',
            fields='bdate,sex,first_name,last_name,city,country')
        info = info[0]
        if 'bdate' in info:
            bdate = info['bdate']
        else:
            bdate = None
        my_country = api.places.getCountryById(cids=int(info['country']))[0]
        info['country'] = my_country['name']
        #my_city = api.places.getCityById(cids=int(info['city']))[0]
        my_city = {'name':u'Bobruysk'}
        info['city'] = my_city['name']
        game_info = GameInfo(city=info['city'], first_name=info['first_name'],
                 last_name=info['last_name'],
                 uid=long(info['uid']), country=info['country'],
                 sex=long(info['sex']), bdate=bdate)
        return game_info

    def _getFriendsId(self):
        api = vkontakte.api.API(token=self.__api_access_token)
        info = api.friends.getAppUsers(format='json')
        print (u'Всего друзей в списке: %s'%str(len(info))).encode('cp866')
        return info
        
    def _getFriendsAllVK(self, friendsid):  # All VK
        friends_all_id = {}
        #return friends_all_id
        api = vkontakte.api.API(token=self.__api_access_token, fields='uid, first_name, last_name, nickname, sex, domain')
        #, fields=uid, first_name, last_name, nickname, sex, bdate (birthdate), city, country, timezone, photo, photo_medium, photo_big, domain, has_mobile, rate, contacts, education
        info = api.friends.get(format='json', timeout=8)
        #print info
        if len(info) == 5000:
            sd = 1 
            while True:
                api = vkontakte.api.API(token=self.__api_access_token, offset=5000*sd, fields='uid, first_name, last_name, nickname, sex, domain')
                info2 = api.friends.get(format='json', timeout=8)
                info.extend(info2)
                sd +=1
                if len(info2) < 5000:
                    break
                else:
                    time.sleep(0.34)
        print u'Frends all', len(info)
        print u'Frends ZF', len(friendsid)
        for us in info:
            nickname = ''
            ZF = ''
            uid = us["uid"]
            #link = 'http://vk.com/id' + us["uid"]
            link = 'https://vk.com/' + us["domain"]
            if hasattr(us,'nickname'): nickname = self._correct(us["nickname"])
            if friendsid.count(uid) > 0: ZF = 'ZF'

            new = {u"link":link, u"first_name":self._correct(us["first_name"]), u"last_name":self._correct(us["last_name"]), u"nick":nickname, u"app_installed":ZF}
            friends_all_id[uid] = new
        #print (u'Друзей в VK: %s'%str(len(friends_all_id))).encode('cp866')
        with open('statistics\\'+self.curuser+'\\friends_all_infoVK.txt', 'w') as f:
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

    def _validateSessionCookies(self, session_cookies):
        return False
        valid = False
        if session_cookies is not None:
            valid = self.getAppParams(1, session_cookies) is not None
        return valid

    def _getSessionCookies(self):
        session_cookies = '' # self._credentials.getSessionCookies()
        cookies_are_valid = self._validateSessionCookies(session_cookies)
        if not cookies_are_valid:
            print 'Session old. Autentification...'
            username = self._credentials.getUserEmail()
            password = self._credentials.getUserPassword()
            post = {'act': 'login',
                    'role': 'al_frame',
                    'expire': '',
                    'captcha_sid': '',
                    'captcha_key': '',
                    '_origin': 'https://vk.com',
                    'email': username,
                    'pass': password}
            vk = Connection('https://vk.com/')
            session_cookies, html = vk.sendRequest(data=None, getCookies=True, getContent=True)
            session_cookies = ('Cookie:' +
                               session_cookies.output(attrs=[],
                                                      header='', sep=';'))
            if html:
                # with open('html.txt', 'w') as f:
                    # f.write(html.encode('UTF-8'))
                matcher = re.compile(r'<input type="hidden" name="([^"]+)" value="([^"]*)" />')
                post.update(dict(matcher.findall(html)))
            # print 'post', post
            vk = Connection('https://login.vk.com/?act=login')
            session_cookies = vk.sendRequest(post, getCookies=True, cookies = session_cookies)  # , cookies = session_cookies
            session_cookies = ('Cookie:' +
                               session_cookies.output(attrs=[],
                                                      header='', sep=';'))
            # print session_cookies
            # self._credentials.setSessionCookies(session_cookies)
        return session_cookies

if __name__ == '__main__':
    credentials = Settings()
    vk = VK(credentials)
    print vk.getAppParams(612925)
