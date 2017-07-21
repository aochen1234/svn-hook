# -*- coding: utf-8 -*-
import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()


from testappp.models import TestResult, ResultNumber, TestRule, TestSet
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
    db = TestSet.objects.all()[0]
    db.lastid = int(Id)
    db.save()


def targetresult(id, names):
    try:
        target = TestResult.objects.get(origin_id=id)
        na = TestRule.objects.get(name=names)
        target.is_target = True
        target.testrule_id = na.id
        target.save()
    except:
        url_list = []
        cookie_list = []
        target = TestResult.objects.filter(origin_id=id).order_by('-created_at')
        for i in target[1:]:
            url_list.append(i.origin_url)
            cookie_list.append(i.origin_cookie)
        if target[0].origin_url in url_list and target[0].origin_cookie in cookie_list:
            target[0].delete()
        else:
            na = TestRule.objects.get(name=names)
            target[0].is_target = True
            target[0].testrule_id = na.id
            target[0].save()


def poccheck(poclist, checkitem, ID):
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

def main_handle():
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
        dbinfo = TestSet.objects.all()[0]
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
        conn = cx_Oracle.connect(dbinfo.username, dbinfo.password,
                                 dbinfo.host + ":" + (dbinfo.port) + "/" + dbinfo.type)

        cursor = conn.cursor()
        print  ("* connect db success")
    except:
        print  ("- connect db false")
        exit()

    try:
        print  ('* last check id  [' + str(dbinfo.lastid) + ']')
        global outfile
        outfile = os.getcwd() + '/' + 'res.txt'
        print  ('* result save in  [' + outfile + ']')
        print  ('* check speed  [' + str(dbinfo.speed) + ']')

        total_q = ('select  count(*) as c from {}  where id >  {}').format(dbinfo.table, str(dbinfo.lastid))
        x = cursor.execute(total_q)
        resss = x.fetchone()
        totalcount = resss[0]
        num = totalcount - int(dbinfo.lastid)
        if num > 0:
            ResultNumber.objects.create(all_data=num)
        else:
            pass
        print ('* waitting check :[' + str(totalcount) + ']')
        bar = ProgressBar(total=(totalcount + 1))

        check_info = ('select  * from {}  where id >  {} and  ROWNUM  < {}').format(dbinfo.table, dbinfo.lastid, dbinfo.speed)
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



if __name__ == '__main__':
    main_handle()


