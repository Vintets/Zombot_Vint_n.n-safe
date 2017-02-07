# encoding=utf-8
from game_state.connection import Connection
from game_state.settings import Settings
import pdb
import requests.api
import re
import json
import vkontakte.api
from game_state.game_types import GameSTART, GameInfo
from game_state.game_event import dict2obj, obj2dict
from hashlib import md5


class OK():
    def __init__(self, credentials):
#        print 'FLOW[okutils.py]:     OK():init()'
        self._credentials = credentials

    def str2dict(self, val):								# Convert "string" cookies to "dict"
        if type(val) is str:
            res = {}
            for tmp in val.replace(' ','').split(';'):
                k = tmp.split('=')[0]
                v = tmp.split('=')[1]
                res[k] = v
#                print k,v
            return res
        else:
            return val

    def getAppParams(self, session_cookies=None):					# Called from: local->
#        print 'FLOW[okutils.py]:     OK():getAppParams()'
        if session_cookies is None:
            session_cookies = self._getSessionCookies()					# OK cookies
											# Step 4 - get App Params
        # html = requests.get('http://www.ok.ru/games/zm', cookies=self.str2dict(session_cookies)).text
        html = requests.get('http://ok.ru/game/zm?st.cmd=appMain&st.appId=625920&gwt.requested=' + self.gwtHash +'&p_sId=0', cookies=self.str2dict(session_cookies)).text

        params = None

        if html:
            matcher = re.compile('.*zombiefarm.html\?(.*?)"')
            for line in html.split('\n'):
                match = matcher.match(line)
                if match is not None:
                    params = match.group(1)
                    break
            if params is not None:
                orig_params = params							# Save unparsed params
                pairs = params.split('&amp;')
                params = {}
                for pair in pairs:
                    key = pair.split('=')[0]
                    value = pair.split('=')[1]
                    params[key] = value
#                    print key, value
        return params									# Return Dict of params

    def get_game_params(self):								# Called from game_engine.py->__create_request_sender()
											# Returns api_user_id, game_auth_key, api_access_token, connection
        params = self.getAppParams()
        #print 'params ', params
#        print 'FLOW[okutils.py]:     OK():get_game_params()'
        ok_user_id = params['logged_user_id']
        ok_auth_key = params['auth_sig']
        ok_session_key = params['session_secret_key']
        game_url = 'http://jok.shadowlands.ru/zombieok/go'
        connection = Connection(game_url)
        self.__params = params
        self._ok_user_id = ok_user_id
        return (ok_user_id, ok_auth_key, ok_session_key, connection)

    def get_time_key(self):								# Called from game_engine.py->get_time()
#        print 'FLOW[okutils.py]:     OK():get_time_key()'
#        print self.__params
        del self.__params['sig']
#        return '&'.join([k + '=' + v for k, v in self.__params.iteritems()])
        return self.__params['session_key']

    def create_start_command(self,server_time, client_time, curuser):  # Called from: game_engine.py->start_game()
        self.curuser = curuser
#        print 'FLOW[okutils.py]:     MR():create_start_command()'
        command = GameSTART(lang=u'en', info=self._getUserInfo(),
                      ad=u'search', serverTime=server_time,
                      clientTime=client_time)
        self.friendsid = self._getFriendsList()
        return command, self.friendsid

    def _getUserInfo(self):								# returns user info from OK
											# Step 7 - get OK userInfo
#        print 'FLOW[okutils.py]:     OK():_getUserInfo()'
        post = {
            'uids': self.__params['logged_user_id'],
            'new_sig': 1,
            'session_key': self.__params['session_key'],
            'fields': u'uid,first_name,last_name,gender,birthday,locale,location',
            'application_key': self.__params['application_key'],
            'format': 'Json'
            }
        post_keys = sorted(post.keys())
        param_str = "".join(["%s=%s" % (str(key), vkontakte.api._encode(post[key])) for key in post_keys])
        param_str += self.__params['session_secret_key']
        sign = md5(param_str).hexdigest().lower()
        post.update({'sig': sign})
#        print '\tDEBUG[okutils.py]:_getUserInfo()->self._credentials.getSessionCookies() = ', self._credentials.getSessionCookies()
        info = requests.post('http://api.ok.ru/api/users/getInfo', data=post, cookies=self.str2dict(self._credentials.getSessionCookies())).json()[0]
#        print(info)

        game_info = GameInfo(city=info['location']['city'], first_name=info['first_name'],
                 last_name=info['last_name'], uid=long(info['uid']), country=info['location']['country'],
                  bdate=info['birthday'])
        return game_info
        #gender=info['gender'],
    def _get_friend_info(self, friend):
        post = {
            'uids': friend,
            'new_sig': 1,
            'session_key': self.__params['session_key'],
            'fields': u'uid,first_name,last_name,gender,birthday,locale,location',
            'application_key': self.__params['application_key'],
            'format': 'Json'
            }
        post_keys = sorted(post.keys())
        param_str = "".join(["%s=%s" % (str(key), vkontakte.api._encode(post[key])) for key in post_keys])
        param_str += self.__params['session_secret_key']
        sign = md5(param_str).hexdigest().lower()
        post.update({'sig': sign})
#        print '\tDEBUG[okutils.py]:_getUserInfo()->self._credentials.getSessionCookies() = ', self._credentials.getSessionCookies()
        info = requests.post('http://api.ok.ru/api/users/getInfo', data=post, cookies=self.str2dict(self._credentials.getSessionCookies())).json()[0]
        print(info)

    def _getFriendsList(self):
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
        info = requests.post('http://api.ok.ru/api/friends/getAppUsers', data=post, cookies=self.str2dict(self._credentials.getSessionCookies())).json()['uids']
#        print(info)
        return info



    def _validateSessionCookies(self, session_cookies):					# Check if cookies are still valid
#        print 'FLOW[okutils.py]:     OK():_validateSessionCookies()'
        valid = False
        if session_cookies is not None:							# If cookies are not empty
            valid = self.getAppParams(session_cookies) is not None			# 
        return valid


    def _getSessionCookies(self):							# Get OK session cookies (Steps 1-2-3)
#        print 'FLOW[okutils.py]:     OK():_getSessionCookies()'
        session_cookies = self._credentials.getSessionCookies()				# If cookies exist in settings.ini
        print 'session_cookies 1'
        print session_cookies
        if session_cookies:
            with open('ok.txt', 'a') as f:
                f.write('session_cookies 1')
                f.write(session_cookies)
        cookies_are_valid = self._validateSessionCookies(session_cookies)
        print 'cookies_are_valid', cookies_are_valid
        if not cookies_are_valid:
            username = self._credentials.getUserEmail()					# settings.py
            password = self._credentials.getUserPassword()				# settings.py
											# Step 2 - get encrypted URL
            post = {
                'st.posted':'set',
                'st.redirect': '%2Fgames%2Fzm',
                'st.originalaction': u'http://www.ok.ru/dk?cmd=AnonymLogin&st.cmd=anonymLogin',
                'st.fJS': 'on',
                'st.email': username,
                'st.password': password,
                'st.remember': 'on',
                'st.iscode': 'false',
                'button_go': 'Sign in'}

            sslurl = requests.post('https://www.ok.ru/https', data=post, allow_redirects=False, verify=True).headers['location']

											# Step 3 - call encrypted URL to get cookies
            session_cookies = requests.get(sslurl, allow_redirects=False).cookies
            self.__ok_cookies = session_cookies
											# Convert cookies to String format
            session_cookies_str = 'AUTHCODE=' + session_cookies['AUTHCODE'] + ';' + \
                              'JSESSIONID=' + session_cookies['JSESSIONID'] + ';' + \
                              'bci=' + session_cookies['bci'] + ';' + \
                              'LASTSRV=www.ok.ru; BANNER_LANG=ru'
                              # 'bd_login_cookie=' + session_cookies['bd_login_cookie'] + ';' + \
											# Save cookies to settings.ini
            self._credentials.setSessionCookies(session_cookies_str)
        ok_cookies = self.str2dict(session_cookies)

        html = requests.get('http://ok.ru', cookies=self.str2dict(session_cookies)).text
        self.gwtHash = str(re.findall(r'gwtHash:"(.*?)"', html)[0])
        # print 'session_cookies_2'
        # print session_cookies
        # print 'gwtHash:', self.gwtHash
        # with open('ok_html_1.txt', 'w') as f:
            # f.write(html.encode('UTF-8'))
        # raw_input()

        return session_cookies	# Return cookies in Dict format

    def getFriends(self):
        return self.friendsid

    def getMyId(self):
        return self.__params['logged_user_id']
        
