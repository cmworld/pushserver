# -*- coding:utf-8 -*-
import logging
import logging.handlers
import sys

#LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '[%(asctime)s] %(funcName)s(%(filename)s:%(lineno)s) [%(levelname)s]:%(message)s'

CONSOLE_FORMAT = '[%(levelname)s]:%(message)s'

log = logging.getLogger()


def create_log(log_file,level=30):
    global log

    log.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)
    filehandler = logging.handlers.TimedRotatingFileHandler(log_file,when="D",interval=1, backupCount=0, encoding=None, delay=False, utc=False)
    filehandler.setFormatter(formatter)
    log.addHandler(filehandler)

def console_log(level=10):
    global log

    log.setLevel(level)
    formatter = logging.Formatter(CONSOLE_FORMAT)
    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(formatter)
    log.addHandler(consolehandler)

console_log = console_log
create_log = create_log

def log_ex(msg=None):
    if msg:
        log.error(msg)
    excinfo = sys.exc_info()
    log.error(excinfo[0])
    log.error(excinfo[1])
    return excinfo