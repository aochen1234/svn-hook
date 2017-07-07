# -*- coding: utf-8 -*-
import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()


from webshell.models import TestResult, ResultNumber, TestRule, TagetResult
import sys
import configparser
import re
import time
import traceback
import logging


class ProgressBar:
    def __init__(self, count=0, total=0, width=50):
        self.count = count
        self.total = total
        self.width = width

    def move(self):
        self.count += 1

    def log(self, s):
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        print (s)
        progress = int(self.width * self.count / self.total)
        sys.stdout.write('{0:3}/{1:3}: '.format(self.count, self.total))
        sys.stdout.write('#' * progress + '-' * (self.width - progress) + '\r')
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()


def writepoc(content):
    global outfile
    logging.basicConfig(level=logging.DEBUG,

                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',

                        datefmt='%a, %d %b %Y %H:%M:%S',

                        filename=outfile,

                        filemode='a+')
    logging.warning(content)


#  cfg.ini 文件操作
def savelastId(Id):
    global cf
    global crpath
    cf.set("check", "lastid", str(Id))
    cf.write(open(crpath, 'w'))


def targetresult(id, names):
    target = TestResult.objects.filter(origin_id=id)
    na = TestRule.objects.get(name=names)
    for i in target:
        TagetResult.objects.create(origin_id=i.origin_id, origin_url=i.origin_url, origin_cookie=i.origin_cookie, is_check=False, testrule_id=na.id)


def poccheck(poclist, checkitem, ID):
    global target
    for name, pocinfo in poclist.items():
        for pocitem, poccheckinfo in pocinfo.items():
            if pocitem in checkitem:
                # print  poccheckinfo +","+checkitem[pocitem]
                ismatch = re.search(poccheckinfo, checkitem[pocitem], re.S)
                if ismatch:
                    nowtime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                    writepoc(ID + ":match->" + name + "." + pocitem + ":" + checkitem[pocitem])
                    targetresult(ID, name)
                    return True
    return False

def main():
    try:
        import cx_Oracle
    except:
        print("- Model cx_Oracle not install ")
        print("- Run  pip install  cx_Oracle ")
        exit()

    try:
        global cf
        global crpath
        cf = configparser.ConfigParser()
        crpath = os.getcwd() + '/cfg.ini'
        cf.read(crpath)
        db = cf.items("db")
        dbinfo = {}
        for aa in db:
            dbinfo[aa[0]] = aa[1]

        check = cf.items("check")
        checkinfo = {}
        for aa in check:
            checkinfo[aa[0]] = aa[1]
        print  ("* load cfg.ini success")
    except:
        print  ("- load cfg.ini  error")
        exit()

    try:
        poclist = {}
        poc = TestRule.objects.all()
        for i in poc:
            temppoclist = {}
            if i.url:
                temppoclist.setdefault('url', i.url)
            if i.cookie:
                temppoclist.setdefault('cookie', i.cookie)
            poclist.setdefault(i.name, temppoclist)

        print  ("* load poc.ini success")
    except:
        print  ("- load poc.ini  error")
        exit()

    try:
        conn = cx_Oracle.connect(dbinfo['username'], dbinfo['password'],
                                 dbinfo['host'] + ":" + (dbinfo['port']) + "/" + dbinfo['type'])

        cursor = conn.cursor()
        print  ("* connect db success")
    except:
        print  ("- connect db false")
        exit()

    try:
        print  ('* last check id  [' + checkinfo['lastid'] + ']')
        global outfile
        outfile = os.getcwd() + '/' + checkinfo['out_file']
        print  ('* result save in  [' + outfile + ']')
        print  ('* check speed  [' + checkinfo['speed'] + ']')

        total_q = ('select  count(*) as c from {}  where id >  {}').format(dbinfo['table'], checkinfo['lastid'])
        x = cursor.execute(total_q)
        resss = x.fetchone()
        totalcount = resss[0]
        ResultNumber.objects.create(all_data=totalcount)
        print ('* waitting check :[' + str(totalcount) + ']')
        bar = ProgressBar(total=totalcount)

        check_info = ('select  * from {}  where id >  {} and  ROWNUM  < {}').format(dbinfo['table'], checkinfo['lastid'], checkinfo['speed'])
        x = cursor.execute(check_info)
        rresss = x.fetchone()

        ik = 0
        checkik = {}
        desciption = cursor.description
        for kk in desciption:
            if kk[0] == 'URL':
                checkik["url"] = ik
            elif kk[0] == 'COOKIE':
                checkik["cookie"] = ik
            elif kk[0] == 'ID':
                checkik["id"] = ik
            ik = ik + 1

        webshell_result = 0
        while rresss:
            if rresss[14] != None or rresss[18] != None:
                TestResult.objects.create(origin_id=rresss[0], origin_url=rresss[14], origin_cookie=rresss[18])
            bar.move()
            bar.log('* checking [' + str(rresss[checkik['id']]) + "->" + str(rresss[checkik['url']]) + ']')
            number = (int(totalcount) - int(rresss[checkik['id']]))
            numbers = ResultNumber.objects.order_by('-created_at')
            numbers_id = numbers[0].id
            numbers_res = ResultNumber.objects.get(id=numbers_id)
            numbers_res.wait_check_data = number
            numbers_res.save()
            checkitem = {}

            for k, v in checkik.items():
                checkitem[k] = str(rresss[v])

            ismatch = poccheck(poclist, checkitem, str(rresss[checkik['id']]))
            if (ismatch):
                bar.log("+ -> find webshell ->[" + str(rresss[checkik['id']]) + ":" + str(rresss[checkik['url']]) + ']')
                webshell_result = webshell_result + 1

            if rresss[checkik['id']] % 1000 == 0:
                savelastId(rresss[checkik['id']])
            krresss = x.fetchone()
            if krresss:
                rresss = krresss
            else:
                savelastId(rresss[checkik['id']])
                rresss = krresss

                # break

        # $q = 'select  * from http_restore_info where ID >  12 and ROWNUM  <10'
        print  ('* handel finish, find webshell  ['+ str(webshell_result)+"]")
    except:
        print ('-  handle error ' + traceback.print_exc())

    finally:
        cursor.close()  # 关闭cursor
        conn.close()

main()
