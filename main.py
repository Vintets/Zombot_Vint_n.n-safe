# -*- coding: utf-8 -*-
#!/usr/bin/python
# coding=utf-8

import os
# os.chdir('C:\\Python27')
from game_state.game_engine import Game
# from game_state.game_engine import Game
from game_state.connection import Connection
from game_state.settings import Settings
from game_state.sn import Site
import logging
import errno
import sys
import re
from game_state.user_interface import UserPrompt
from ctypes import windll
stdout_handle = windll.kernel32.GetStdHandle(-11)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute

logger = logging.getLogger('main')
friends = 'None'

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def setup_basic_logging(gui_logger):
    #FORMAT = '[%(asctime)s] %(message)s'
    FORMAT = '%(asctime)s.%(msecs)d %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%H:%M:%S', # , filename='my_app.log'
                        stream=MyLogger(gui_logger))
    connection_logger = logging.getLogger('connection')
    connection_logger.propagate = False


def setup_file_logging(user_name, log_level):
    log_directory = 'statistics/' + user_name + '/logs/'
    mkdir_p(log_directory)
    connection_logger = logging.getLogger('connection')
    connection_logger.propagate = False
    connection_logger.addHandler(
        logging.FileHandler(log_directory + '/connection.log')
    )
    connection_logger.setLevel(log_level)
    unknownEventLogger = logging.getLogger('unknownEventLogger')
    unknownEventLogger.propagate = False
    unknownEventLogger.addHandler(
        logging.FileHandler(log_directory + '/unknown_events.log')
    )
    unknownEventLogger.setLevel(log_level)


def strip_special(string):
    return string
    return ''.join(e for e in string if e.isalnum())


def get_site(gui_input):
    settings = Settings()
    default_user = settings.get_default_user()
    users = settings.getUsers()
    #selected_user = UserPrompt(gui_input).prompt_user('Select user:', users)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        #logger.info('пользователь передан с параметром 1')
        selected_user = users[int(sys.argv[1])]
    elif len(sys.argv) > 2 and sys.argv[2].isdigit():
        #logger.info('пользователь передан с параметром 2')
        selected_user = users[int(sys.argv[2])]
    elif default_user == None:
        selected_user = UserPrompt(gui_input).prompt_user('Select user:', users)
    else:
        selected_user = users[int(default_user)]
    
    print 'You selected "'+selected_user+'"'
    log_level = settings.get_file_log_level()
    setup_file_logging(strip_special(selected_user), log_level)
    settings.setUser(selected_user)
    site = Site(settings)        
    return site, settings


def run_game(gui_input=None):
    setup_basic_logging(gui_input)

    logger.info('Выбираем пользователя...')

    site, settings = get_site(gui_input)

    Game(site, settings, UserPrompt(gui_input), gui_input=gui_input).start()

def cprint(cstr):
    clst = cstr.split('^')
    color = 0x0001

    for cstr in clst:
        dglen = re.search("\D", cstr).start()
        color = int(cstr[:dglen])
        text = cstr[dglen:]
        if text[:1] == "_": text = text[1:]
        SetConsoleTextAttribute(stdout_handle, color | 0x0070) #78
        print text,
    #sys.stdout.flush()
    print ""
    SetConsoleTextAttribute(stdout_handle, 0x0001 | 0x0070)

MyLogger = None

BRANCH = 'master by Vanuan'
__version__ = '0.9.7++ ' + BRANCH + ' changed by Vint' + ' and many, many other...'
__copyright__ = '2013 (c) github.com/Vanuan/zombot'

if __name__ == '__main__':
    #print '\n2013 (c) github.com/Vanuan/zombot\n version %s\n\n' % __version__
    #print '#'*80+'2013 (c) github.com/Vanuan/zombot\n version %s\n' % (__version__)+'#'*80

    print (u' '*80*3)
    # cprint(u'1%s' % (u' '*79*20))
    line1 = ' '*((80-len(__copyright__))/2)
    line2 = ' '*((80-len(__version__)-8)/2)
    print '#'*80+line1+__copyright__+line1+"\n"+line2+"version %s"%(__version__)+line2+"\n"+'#'*80
    name_product = "!!! ZomBot !!!"
    tab = ' '*((80-len(name_product))/2)
    print tab+name_product+tab
    SetConsoleTextAttribute(stdout_handle, 0x0001 | 0x0070)
    #import sys
    if len(sys.argv) == 1:
        import game_state.gui
        MyLogger = game_state.gui.MyLogger
        import game_state.app
        app.run_application(run_game)
    if len(sys.argv) > 2 and sys.argv[2] == '-c':
        import game_state.console
        MyLogger = game_state.console.MyLogger
        run_game()
    elif sys.argv[1] != '-c':
        import game_state.gui
        MyLogger = game_state.gui.MyLogger
        import game_state.app
        app.run_application(run_game)
    else:
        import game_state.console
        MyLogger = game_state.console.MyLogger
        run_game()
