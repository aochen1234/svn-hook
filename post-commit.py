#!/usr/bin/env python
#-*-coding:utf-8-*-
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def recordlog(content):
    import logging.handlers
    LOG_FILE = '/var/log/svnerror.log'
    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)
    fmt = '%(asctime)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger = logging.getLogger('test')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.info(content)

def main(argv):
    repos = argv[1]
    txn = argv[3]
    svninfo = os.popen("/usr/bin/svnlook info '%s'" % repos).readlines()
    a = (u"提交人: %s\t提交时间: %s\t当前版本: %s\t提交说明: %s" % (svninfo[0], svninfo[1], txn, svninfo[3]))
    a += ("===============================================")
    a += (u"\r\n提交内容: ")
    changelist = os.popen("/usr/bin/svnlook changed '%s'" % repos).readlines()
    for i in changelist:
        a += i
    recordlog(a)
if __name__== "__main__":
    os.chdir(sys.path[0])
    main(sys.argv[1:])
