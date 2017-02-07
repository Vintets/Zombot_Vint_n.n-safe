# coding=utf-8
from game_state.connection import Connection
import requests
import vkontakte
from hashlib import md5
from game_state.game_types import GameSTART, GameInfo

class FB():
    def __init__(self, credentials):
        self._credentials = credentials

    def str2dict(self, val):
        if type(val) is str:
            res = {}
            for tmp in val.replace(' ','').split(';'):
                k = tmp.split('=')[0]
                v = tmp.split('=')[1]
                res[k] = v
            return res
        else:return val

    def getAppParams(self, app_id, session_cookies=None):
        if session_cookies is None:
            session_cookies = self._getSessionCookies()
        html = requests.get('https://apps.facebook.com/' + str(app_id) + '/?fb_source=appcenter&fb_appcenter=1', cookies=self.str2dict(session_cookies)).text
        self.__session_cookies = session_cookies
        findUser=str(session_cookies)
        e=findUser.find('c_user=')
        if e>0:e=e+7
        y=findUser.find(' for')
        userID=findUser[e:y]
        params = {'uid': '', 'key':'', 'auth':'' }
        if html:
            findes='name="signed_request" value="'
            f = html.find(findes)
            if f>0:f = f + len(findes)
            t = html.find('"', f)
            if (f>0) and (t>0):params['key']=html[f:t]
            if userID:params['uid']=userID
        return params

    def getAppParams2(self, params):
        post = {
			'signed_request': params['key'],
			'fb_locale':'ru_RU',
            }
        mr = Connection('https://zombie-fb.shadowlands.ru/zombiefb/?fb_source=appcenter&fb_appcenter=1')
        html = mr.sendRequest(post, None)
        if html:
            myFile = open('_html_ap2.html', 'wb')
            myFile.write(html.encode("utf-8"))
            myFile.close()
        v = html.find('flashvars')
        f = html.find("key:'", v)
        if f>0:f=f+5
        t = html.find("'", f)
        if f>0 and t>0:params['key']=html[f:t]
        f = html.find("auth:'", v)
        if f>0:f=f+6
        t = html.find("'", f)
        if f>0 and t>0:params['auth']=html[f:t]
        return params

    def get_game_params(self):
        params=self.getAppParams('zombieisland')
        params=self.getAppParams2(params)
        self.__game_api_user_id = params['uid']
        game_auth_key = params['auth']
        self.__api_access_token = params['auth']
        game_url = 'https://zombie-fb.shadowlands.ru/zombiefb/go'
        connection = Connection(game_url)
        self.__params = params
        return (self.__game_api_user_id, game_auth_key, params, connection)

    def get_time_key(self):
        return self.__params['key']

    def create_start_command(self,server_time, client_time, curuser):
        self.curuser = curuser
        command = GameSTART(lang=u'en', info=self._getUserInfo(),
                      ad=u'search', serverTime=server_time,
                      clientTime=client_time)
        uid = self.__game_api_user_id
        return command, [], uid
        #return command, []

    def _getUserInfo(self):
        return GameInfo()

    def _validateSessionCookies(self, session_cookies):
        valid = False
        if session_cookies is not None:
            valid = self.getAppParams('zombieisland',session_cookies) is not None
        return valid
        
    def _getFriendsListMR2_old_do_500(self):
        friendsid = []
        offset = 0
        ex_fr = 0
        while ex_fr == 0:     
            post = {
                'method': 'friends.getAppUsers',
                'app_id': 'zombieisland',
                'offset' : str(offset),
                'session_key': self.__api_access_token
                }
            post_keys = sorted(post.keys())
            param_str = "".join(["%s=%s" % (str(key), vkontakte.api._encode(post[key])) for key in post_keys])
            param_str = self.__game_api_user_id + param_str + 'session_key'
            sign = md5(param_str).hexdigest().lower()
            post.update({'sig': sign})
            BASE_URL = Connection('http://api.facebook.com/1.0/')
            add = eval(BASE_URL.sendRequest(post, cookies=self.__session_cookies))
            if len(add) == 0:
                ex_fr = 1
            else:
                offset +=1000
                friendsid.extend(add)
        return friendsid

    def _getFriendsListMR2(self):
        friendsid = []
        offset = 0
        while True:
            post = {
                'method': 'friends.getAppUsers',
                'app_id': 'zombieisland',
                'offset' : str(offset),
                'session_key': self.__api_access_token
                }
            post_keys = sorted(post.keys())
            param_str = "".join(["%s=%s" % (str(key), vkontakte.api._encode(post[key])) for key in post_keys])
            param_str = self.__game_api_user_id + param_str + 'session_key'
            sign = md5(param_str).hexdigest().lower()
            post.update({'sig': sign})
            BASE_URL = Connection('http://api.facebook.com/1.0/')
            add = eval(BASE_URL.sendRequest(post, cookies=self.__session_cookies))
            friendsid.extend(add)
            print 'load ', len(add)
            offset += 500
            if len(add) < 500: break
        return friendsid

    def _getSessionCookies(self):
        session_cookies = self._credentials.getSessionCookies()
        cookies_are_valid=False
        #cookies_are_valid = self._validateSessionCookies(session_cookies)
        if not cookies_are_valid:
            username = self._credentials.getUserEmail()
            password = self._credentials.getUserPassword()
            post = {

                'lsd':'AVr5db7w',
                'display':'page',
                'enable_profile_selector':'',
                'legacy_return':'1',
                'profile_selector_ids':'',
                'skip_api_login' :'1',
                'trynum':'1',
                'timezone':'',
                'lgnrnd':'115053_Dgev',
                'lgnjs': 'n',
                'email': username,
                'pass': password,
                'persistent':'1',
                'default_persistent': '0',
                'login':'&#x412;&#x43e;&#x439;&#x442;&#x438;',
                #'_fb_noscript':'true'
            }
            res = requests.post('https://m.facebook.com/login.php?refsrc=https%3A%2F%2Fm.facebook.com%2Flogin.php&refid=9', data=post, allow_redirects=False, verify=True)
            session_cookies = res.cookies
            self._credentials.setSessionCookies(session_cookies)
        return session_cookies