# coding=utf8

import game_state.hashsum
import json
import collections

import random
import logging
import os.path
import os
import subprocess
from game_state.read_swf import swf2functions
import urllib2

logger = logging.getLogger(__name__)


def __saltFunction(string):
    result = ""
    # from classWithGo
    result += str(len(string)) + (game_state.hashsum)._md5hash(string + "stufff...")
    #salt13 = str(len(string) * 13)  # from main.initialize
    salt13 = str(len(string) * 17 + 13)  # from main.initialize
    #salt2 = hashsum._md5hash(salt13 + str(len(salt13)) + str(len(string)))
    salt2 = (game_state.hashsum)._md5hash(salt13 + str(len(string))+ str(len(salt13)))
    result += salt2
    characterSum = 0  # calc sum of byte codes in a string
    for i in range(0, len(string)):
        #characterSum += (ord(string[i]) & 255)
        characterSum += (ord(string[i]) & 250)
    result += str(characterSum)
    return result


def calcCRC(string):
    return (game_state.hashsum)._md5hash(string + __saltFunction(string))


# def calcSig(sessionKey, requestId, authKey):
    # sig = sessionKey + str(requestId) + authKey
    # sig += __saltFunction(sig)
    # sig = hashsum._md5hash(sig)
    # return sig    

def calcAuth(requestId, authKey):
    auth = str(requestId) + authKey
    auth += __saltFunction(auth)
    sig = (game_state.hashsum)._md5hash(auth)
    return sig


class Session():
    '''
    This class represents session data needed
    to authenticate and sign messages
    '''
    def __init__(self, user_id, auth_key, client_version=1370414015,
                 session_key=None):
        self.__user_id = user_id          # vk user id
        self.__session_key = session_key  # session key from TIME request
        self.__auth_session_key = None    # key from TIME response
        self.__auth_key = auth_key        # auth key from vk.com flashvars
        self.CLIENT_VERSION = client_version

    def getUserId(self):
        return self.__user_id

    def getSessionKey(self):
        return self.__session_key

    def setSessionKey(self, session_key):
        self.__session_key = session_key

    def getAuthKey(self):
        return self.__auth_key

    def set_auth_key(self, auth_key):
        self.__auth_key = auth_key

    def getAuthSessionKey(self):
        return self.__auth_session_key


class Factory():
    '''
    This class will be used to generate signed messages
    '''
    def __init__(self, session, selected_site, base_request_id=None):
        if base_request_id is None:
            base_request_id = _getInitialId()
        self.__session = session
        assert isinstance(self.__session, Session)
        self.BASE_REQUEST_ID = base_request_id  # "magick" initial value
        self.__request_id = self.BASE_REQUEST_ID
        self.__selected_site = selected_site

    def createRequest(self, data, data_keys_order=None):
        request_data = {}
        request_data['data'] = self.__createDataValue(data, data_keys_order)
        request_data['crc'] = calcCRC(request_data['data'])
        return Request(request_data)

    def __createDataValue(self, data, data_keys_order):
        if data_keys_order is None:
            data_keys_order = _getDataKeyOrder(data['type'])
        datacopy = data.copy()
        datacopy['user'] = str(self.__session.getUserId())
        datacopy['id'] = self.__request_id
        datacopy['sig'] = ''
        datacopy['auth'] = ''
        datacopy['clientVersion'] = self.__session.CLIENT_VERSION
        data_value = collections.OrderedDict()
        for key in data_keys_order:
            if key in datacopy:
                data_value[key] = datacopy[key]
        message_type = datacopy['type']
        if message_type == 'START':
            info_keys = ["uid", "bdate", "country", "first_name",
                         "sex", "city", "last_name"]
            data_value['info'] = collections.OrderedDict()
            for info_key in info_keys:
                if info_key in datacopy['info']:
                    data_value['info'][info_key] = datacopy['info'][info_key]
        self.__addSigOrAuth(data_value)
        result = json.dumps(data_value, separators=(',', ':'),
                            ensure_ascii=False, encoding="utf-8")
        self._generateRequestId()
        return result

    def __addSigOrAuth(self, objectData):
        sessionKey = self.__session.getSessionKey()
        auth_key = self.__session.getAuthKey()
        authSessionKey = self.__session.getAuthSessionKey()

        if sessionKey is not None:
            #objectData["sig"] = calcSig(sessionKey, self.__request_id, auth_key)
            objectData["sig"] = self.calcSig(sessionKey, self.__request_id, auth_key)
        else:
            objectData["auth"] = calcAuth(self.__request_id, auth_key)
            if authSessionKey is not None:
                objectData["key"] = authSessionKey
        return objectData

    """
    def calcSig(self,sessionKey, requestId, authKey):
        #if hasattr(self,'sig') and isinstance(self.sig,dict) and self.sig.has_key(str(requestId)):
        #    return hashsum._md5hash(self.sig[str(requestId)])
        if hasattr(self,'sig') and isinstance(self.sig,dict):
            if self.sig.has_key(str(requestId)):
                return hashsum._md5hash(self.sig[str(requestId)])
            else:
                delattr(self,'sig')
                raise GameError("No sig for %s"%(" ".join([authKey,str(requestId),sessionKey])))            
        if not os.path.isdir('C:\\Python27\\sig'): os.makedirs('C:\\Python27\\sig')
        if not os.path.isdir('C:\\Python27\\sig\\bin'): os.makedirs('C:\\Python27\\sig\\bin')
        #if not os.path.isdir('.\sig'): os.makedirs('.\sig')
        #if not os.path.isdir('.\sig\\bin'): os.makedirs('.\sig\\bin')
        with open("..\\sig\\bin\\keys.txt",'wt') as f:
            f.write(" ".join([authKey,str(requestId),sessionKey]))
        cwd = os.getcwd()
        os.chdir("..\\sig")
        subprocess.call(["Run.bat"])
        os.chdir(cwd)
        with open("..\\sig\\bin\\sig.txt",'rt') as f:
            data=f.read()
            self.sig=eval(data)
            return hashsum._md5hash(self.sig[str(requestId)])
        raise GameError("No sig for %s"%(" ".join([authKey,str(requestId),sessionKey])))
    """
    def calcSig(self,sessionKey, requestId, authKey):
        postfix = sessionKey.split(':')[1]
        if not hasattr(self,'postfix') or self.postfix != postfix:
            self.postfix = postfix
            url = base_redirect_url+'/salt'
            #logger.info('Getting %s?postfix=%s'%(url,postfix))
            opener = urllib2.build_opener()
            response = opener.open(url, 'postfix='+postfix, timeout=8)
            if response:
                content = response.read()
                response.close()
            else:
                raise GameError("Cannot load salt swf")
            self.functions = swf2functions(content,postfix,self.__selected_site)
        sig = sessionKey + str(requestId) + authKey
        saltFunction_sig = sig
        for f in self.functions:
            saltFunction_sig = f(saltFunction_sig)
        sig += saltFunction_sig
        sig = (game_state.hashsum)._md5hash(sig)
        return sig      
        
    def _generateRequestId(self):
        self.__request_id += 1

    def setRequestId(self, request_id):
        self.__request_id = request_id

    def _getSessionKey(self):
        return self.__session.getSessionKey()

    def setSessionKey(self, session_key):
        self.__session.setSessionKey(session_key)

    def set_auth_key(self, auth_key):
        self.__session.set_auth_key(auth_key)

class Request():
    '''
    This class represents a POST body ready to be send via HTTP
    '''
    def __init__(self, data):
        self.__data = data

    def __str__(self):
        return str(self.__data)

    def getData(self):
        return self.__data

    def send(self, connection):
        '''
        Sends request data to server,
        handles redirect
        Returns response as dict
        '''
        global base_redirect_url
        response = self.send_request_get_response(connection)
        if 'redirect' in response:
            #if not os.path.isdir('C:\\Python27\\sig'): os.makedirs('C:\\Python27\\sig')
            #if not os.path.isdir('C:\\Python27\\sig\\bin'): os.makedirs('C:\\Python27\\sig\\bin')
            #  if not os.path.isdir('.\sig'): os.makedirs('.\sig')
            #  if not os.path.isdir('.\sig\\bin'): os.makedirs('.\sig\\bin')        
            #with open("..\\sig\\bin\\url.txt",'wt') as f:
            #    f.write(response['redirect'])
            base_redirect_url = response['redirect']
            server_url = response['redirect'] + '/go'
            connection.setUrl(server_url)
        if 'cmd' in response:
            if response['cmd'] == 'REDIRECT':
                # send request again with new url
                response = self.send_request_get_response(connection)
            elif response['cmd'] == 'ERR':
                error_msg = response["msg"]
                logger.error(error_msg)
                # TODO send error to the game server
                # open('error_log.txt','a').write("Connection: " + str(self.getData())+'\nResponse: '+str(response)+'\n\n')
                logger.info('Connection : ' + str(self.getData()))
                logger.info('Response : ' + str(response))
                raise GameError('Game server returned error: ' + error_msg)
        return response

    def send_request_get_response(self, connection):
        return Response(connection.sendRequest(self.getData())).getDict()


class GameError(Exception): pass


class Response():
    '''
    This class represents a response
    '''
    def __init__(self, response_string):
        if response_string != None and '$' in response_string:
            crc, response = response_string.split("$", 1)
            if(calcCRC(response) != crc):
                raise ValueError("CRC is invalid: " + crc)
        else:
            response = response_string
        self.__response = json.loads(response)
        
        # if 'state' in self.__response:
            # if 'buffs' in self.__response['state']:
                # aaa = self.__response['state']['buffs']['list']
                # for k in aaa:
                  # # if ('HARVEST' in k['item']) or ('DIGGER' in k['item']) or ('COOK' in k['item']):
                  # if 'BUFF_FIX_' in k['item']:
                    # _exp_mins = float(k['expire']['endDate'])/60000.0
                    # _exp_hrs = _exp_mins//60
                    # if _exp_hrs>0:
                        # print '*** ', k['item'], '- time %02d:%02d' % (_exp_hrs, _exp_mins - _exp_hrs*60)

    def getDict(self):
        return self.__response


def _getInitialId():
    '''
    flash.utils.getTimer() called to get initial request id.
    http://help.adobe.com/en_US/FlashPlatform/reference/
    actionscript/3/flash/utils/package.html#getTimer()
    varies randomly from 40 to 60
    '''
    random.seed()
    return random.randrange(40, 60)


def _getDataKeyOrder(message_type):
    keys = []
    if message_type == 'TIME':
        keys = ['auth', 'type', 'clientVersion', 'user',  'id', 'key' ]
    if message_type == 'START':
        keys = [
            'id',
            'sig',
            'clientTime',
            'serverTime',
            'info',
            'type',
            'user',
            'ad',
            'lang',
        ]
    if message_type == 'EVT':
        keys = [
            'user',
            'type',
            'id',
            'sig',
            'events',
            'time'
        ]
    return keys

