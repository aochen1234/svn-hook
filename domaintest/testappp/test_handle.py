# -*- coding: utf-8 -*-
#  导入django的orm,报错的话设置环境变量 export PYTHONPATH=/home/xxx/xxx/testapp 根据自己时间情况更改,可以写
#  进/etc/profile中永久生效
import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()


from testappp.models import TestResult, ResultNumber, TestSet, TestDomain
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


def savelastid(id):
    a = TestSet.objects.all()[0]
    a.lastid = id
    a.save()


#  检测当天是否有结果数量记录
def monthcheck():
    a = time.localtime()
    if a[1] < 10:
        if a[2] < 10:
            aa = ResultNumber.objects.filter(created_at__startswith='{}-0{}-0{}'.format(a[0], a[1], a[2])).count()
        else:
            aa = ResultNumber.objects.filter(created_at__startswith='{}-0{}-{}'.format(a[0], a[1], a[2])).count()
    else:
        if a[2] < 10:
            aa = ResultNumber.objects.filter(created_at__startswith='{}-{}-0{}'.format(a[0], a[1], a[2])).count()
        else:
            aa = ResultNumber.objects.filter(created_at__startswith='{}-{}-{}'.format(a[0], a[1], a[2])).count()
    if aa != 0:
        pass
    else:
        ResultNumber.objects.create(all_data=0, wait_check_data=0)


#  检测起始时间获取
def gettesttime(dbinfo):
    if dbinfo.starttime == None:
        a = time.localtime()
        if a[1] < 10:
            b = str(a[0]) + '-0' + str(a[1]) + '-01'
        else:
            b = str(a[0]) + '-' + str(a[1]) + '-01'
    else:
        c = str(dbinfo.starttime).split(' ')
        b = c[0]
    return b


def multiple_replace(text, adict):
    rx = re.compile('|'.join(map(re.escape,adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat,text)


def getheader(li):
    if li != None:
        if li.startswith('POST') or li.startswith('GET'):
            try:
                lis = {'Content-Length': '\nContent-Length', 'Connection': '\nConnection',
                           'X-Forwarded-For': '\nX-Forwarded-For',
                           'Cache-Control': '\nCache-Control', 'Cookie': '\nCookie', 'Pragma': '\nPragma',
                           'User-Agent': '\nUser-Agent',
                           'Accept': '\nAccept', 'Host': '\nHost', 'Accept-Encoding': '\nAccept-Encoding', 'Referer': '\nReferer',
                           'Accept-Language': '\nAccept-Language', 'If-Modified-Since': '\nIf-Modified-Since',
                           'X-Requested-With': '\nX-Requested-With'}
                b = multiple_replace(li, lis)
                c = b.split('\n')
                return c[0]
            except TypeError:
                return None


#  匹配域名
def domaincheck(domainlist, source):
    a = {'id':''}
    for i in domainlist:
        if '或' in domainlist[i]:
            b = domainlist[i].split('或')
            try:
                ismatch = re.search(b[0], source[2], re.S)
                if ismatch:
                    a['id'] = i
                    return a
                else:
                    istarget = re.search(b[1], source[2], re.S)
                    if istarget:
                        a['id'] = i
                        return a
            except:
                pass
        else:
            try:
                ismatchs = re.search(domainlist[i], source[2], re.S)
                if ismatchs:
                    a['id'] = i
                    return a
            except:
                pass
    return 10


# E.id, P.name, P.value, P.id, E.sip, E.sloc, E.partition_time
#  数据批量插入
def datainsert(num, domainlist):
    pro = []
    prolist = []
    if len(num['REQUEST_HEADER']) != 0:
        for i in num['REQUEST_HEADER']:
            try:
                b = TestResult.objects.get(proplist_id=i[3])
                pass
            except:
                isdomain = domaincheck(domainlist, i)
                url = getheader(i[2])
                if isdomain != 10:
                    a = isdomain['id']
                    prolist.append(TestResult(origin_url=url, record_id=i[0], proplist_id=i[3], is_target=True, testdomain_id=a, sip=i[4], sloc=i[5],
                                              pattition_time=i[6], request_header=i[2]))
                else:
                    pro.append(TestResult(origin_url=url, record_id=i[0], proplist_id=i[3], sip=i[4], sloc=i[5], pattition_time=i[6], request_header=i[2]))
        if len(prolist) != 0:
            TestResult.objects.bulk_create(prolist)
        if len(pro) != 0:
            TestResult.objects.bulk_create(pro)
    if len(num['HOST']) != 0:
        for i in num['HOST']:
            b = TestResult.objects.filter(record_id=i[0])
            if b.count() != 0:
                for j in b:
                    j.host = i[2]
                    j.save()


def main_handle():
    monthcheck()
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
        #  获取检验规则
        domainlist = {}
        domain = TestDomain.objects.all()
        for i in domain:
            domainlist.setdefault(i.id, re.escape(i.content))
        print  ("* load rule success")
    except:
        print  ("- load rule  error")
        exit()

    try:
        conn = cx_Oracle.connect(dbinfo.username, dbinfo.password, dbinfo.host + ":" + (dbinfo.port) + "/" + dbinfo.type)
        cursor = conn.cursor()
        print  ("* connect db success")
    except:
        print  ("- connect db false")
        exit()

    try:
        global outfile
        outfile = os.getcwd() + '/' + 'res.txt'
        print  ('* result save in  [' + outfile + ']')

        total_q = ("select  count(*) as c from event_proplist P, event_record E  where P.event_id = E.id and to_char(E.Partition_Time,'yyyy-mm-dd') > '{}' ").format(gettesttime(dbinfo))
        x = cursor.execute(total_q)
        resss = x.fetchone()
        totalcount = resss[0]
        wait_check_data = ResultNumber.objects.all().order_by('-created_at')[0]
        wait_check_data.wait_check_data = totalcount
        wait_check_data.save()
        print ('* waitting check :[' + str(totalcount) + ']')

        bar = ProgressBar(total= (totalcount))
        res = TestSet.objects.all()[0]
        if res.lastid == '0':
            check_info = ("SELECT E.id, P.name, P.value, P.id, E.sip, E.sloc, E.partition_time  from event_proplist P, event_record E  where P.event_id = E.id and to_char(E.Partition_Time,'yyyy-mm-dd') > '{}' and ROWNUM < 20000").format(gettesttime(dbinfo))
        else:
            ff = TestResult.objects.get(proplist_id=res.lastid)
            times = str(ff.pattition_time).split('+')
            check_info = ("SELECT E.id, P.name, P.value, P.id, E.sip, E.sloc, E.partition_time  from event_proplist P, event_record E  where P.event_id = E.id and to_date(E.Partition_Time,'yyyy-mm-dd hh24:mi:ss') > '{}' and ROWNUM < 20000").format(times[0])
        x = cursor.execute(check_info)
        rresss = x.fetchone()

        ik = 0
        checkik = {}
        desciption = cursor.description
        for kk in desciption:
            if kk[0] == 'VALUE':
                checkik["value"] = ik
            elif kk[0] == 'Name':
                checkik["name"] = ik
            elif kk[0] == 'ID':
                checkik["id"] = ik
            ik = ik + 1

        webshell_result = 0
        result_host = []
        result_request = []
        b = 0
        nu = 0
        while rresss:
            if rresss[1] == 'HOST' and rresss[2] != None:
                result_host.append(rresss)
            elif rresss[1] == 'REQUEST_HEADER' or rresss[1] == 'COOKIE' and rresss[2] != None:
                result_request.append(rresss)
            else:
                pass
            nu += 1
            if nu < 3000:
                pass
            else:
                result_list = {}
                result_list.setdefault('HOST', result_host)
                result_list.setdefault('REQUEST_HEADER', result_request)
                savelastid(rresss[3])
                datainsert(result_list, domainlist)
                all_data = ResultNumber.objects.all().order_by('-created_at')[0]
                all_data.all_data += 3000
                all_data.wait_check_data -= 3000
                all_data.save()
                result_list = []
                b += 1
                nu = 0
            bar.move()
            checkitem = {}

            for k, v in checkik.items():
                checkitem[k] = str(rresss[v])
            krresss = x.fetchone()
            if krresss:
                rresss = krresss
            else:
                rresss = krresss
        if len(result_host) != 0 or len(result_request) != 0:
            result_list = {}
            result_list.setdefault('HOST', result_host)
            result_list.setdefault('REQUEST_HEADER', result_request)
            datainsert(result_list, domainlist)
            lastid = TestSet.objects.all()[0]
            lastid.lastid = '0'
            lastid.save()
            wait_data = ResultNumber.objects.all().order_by('-created_at')[0]
            wait_data.wait_check_data = 0
            wait_data.all_data += (len(result_list['HOST']) + len(result_list['REQUEST_HEADER']))
            wait_data.save()
        else:
            wait_data = ResultNumber.objects.all().order_by('-created_at')[0]
            wait_data.wait_check_data = 0
            wait_data.save()
            lastid = TestSet.objects.all()[0]
            lastid.lastid = '0'
            lastid.save()

                # break

        # $q = 'select  * from http_restore_info where ID >  12 and ROWNUM  <10'
        print  ('* handel finish, find webshell  ['+ str(webshell_result)+"]")
    except:
        print ('-  handle error ' + traceback.print_exc())

    finally:
        cursor.close()  # 关闭cursor
        conn.close()



if __name__ == '__main__':
    while True:
        main_handle()


