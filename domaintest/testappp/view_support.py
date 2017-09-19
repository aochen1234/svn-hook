import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()

import time
import calendar
import json
import re
import csv
import zipfile
from collections import Counter
from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import StreamingHttpResponse
from testappp.models import ResultNumber, TestResult, TestDomain
from testappp.templatetags.iptags import ip2loc
from testappp.templatetags.mytags import truncate_ip


def multiple_replace(text, adict):
    rx = re.compile('|'.join(map(re.escape,adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat,text)


#  去重复
def norepeat(li):
    a = []
    b = []
    for i in li:
        if i.sip not in a:
            a.append(i.sip)
            b.append(i)
    return b


#  获得请求头信息
def getheaderinfo(li):
    c = li.split('\n')
    res = {}
    a = ['Origin', 'Referer']
    b = ['GET', 'POST']
    h = c[0]
    if c[0][-1] != '1':
        h = c[0] + c[1]
    else:
        pass
    for j in b:
        if j in c[0]:
            va = h.replace(j, '')
            res.setdefault('url', va.encode("utf-8").decode("latin1"))
            res.setdefault('type', j)
    for i in c[1:]:
        for m in a:
            if m in i:
                value = i.replace(m + ':', '').strip()
                res[m] = value.encode("utf-8").decode("latin1")
            else:
                try:
                    value = i.split(':')
                    res.setdefault(value[0], value[1].strip().encode("utf-8").decode("latin1"))
                except:
                    pass
    return res


def alldataorderbymonth():
    all_data = 0
    a = time.localtime()
    if a[1] < 10:
        all_data_list = ResultNumber.objects.filter(created_at__startswith='{}-0{}'.format(a[0], a[1]))
        for i in all_data_list:
            all_data += i.all_data
        return all_data
    else:
        all_data_list = ResultNumber.objects.filter(created_at__startswith='{}-{}'.format(a[0], a[1]))
        for i in all_data_list:
            all_data += i.all_data
        return all_data


def waitcheckdata():
    try:
        wait_data = ResultNumber.objects.all().order_by('-updated_at')[0]
        wait_data_num = wait_data.wait_check_data
        if wait_data_num < 0:
            wait_data_num = 0
    except:
        wait_data_num = 0
    return wait_data_num


def waitcheckdatatime():
    wait_data = waitcheckdata()
    if wait_data == 1 or wait_data == 0:
        return ('0 s')
    elif wait_data != 1 and wait_data // 10000 == 0:
        return ('2 min')
    else:
        n = wait_data // 10000
        return ('{} min').format(2 * n)


def resultdisplay(n):
    result_list = TestResult.objects.all().order_by('-created_at')[:n]
    return result_list


def baddata():
    a = time.localtime()
    if a[1] < 10:
        result_num = TestResult.objects.filter(is_target=True, created_at__startswith= '{}-0{}'.format(a[0], a[1])).order_by('-created_at')
    else:
        result_num = TestResult.objects.filter(is_target=True, created_at__startswith= '{}-{}'.format(a[0], a[1])).order_by('-created_at')
    return result_num


#  自定义分页组件
class CustomPaginator(Paginator):
    def __init__(self, current_page, per_pager_num, *args, **kwargs):
        self.current_page = int(current_page)
        self.per_pager_num = int(per_pager_num)
        super(CustomPaginator, self).__init__(*args, **kwargs)

    def pager_num_range(self):
        if self.num_pages < self.per_pager_num:
            return range(1, self.num_pages + 1)

        half_part = int(self.per_pager_num / 2)
        if self.current_page <= half_part:
            return range(1, self.per_pager_num + 1)

        if (self.current_page + half_part) > self.num_pages:
            return range(self.num_pages - self.per_pager_num + 1, self.num_pages)
        return range((self.current_page - half_part), (self.current_page + half_part + 1))

def pagedivide(request, USER_LIST):
        try:
            current_page = request.GET.get('page')
            paginator = CustomPaginator(current_page, 11, USER_LIST, 12)
        except:
            current_page = 1
            paginator = CustomPaginator(current_page, 11, USER_LIST, 12)

        try:
            paginator = paginator.page(current_page)
        except PageNotAnInteger:
            paginator = paginator.page(1)
        except EmptyPage:
            paginator = paginator.page(paginator.num_pages)
        return paginator


#  搜索设置
def search_set(request, types, stuff, cata):
    ret = {'result':'', 'errors': '10', 'number': '', 'type': '', 'sort': ''}
    if cata == 'result':
        current_page = 1
        USER_LIST = TestResult.objects.all().order_by('-created_at')
        paginator = CustomPaginator(current_page, 11, USER_LIST, 12)
        try:
            paginator = paginator.page(current_page)
        except PageNotAnInteger:
            paginator = paginator.page(1)
        except EmptyPage:
            paginator = paginator.page(paginator.num_pages)
        ret['result'] = paginator
        ret['number'] = USER_LIST.count()
        if types == '1':
            result_page = TestResult.objects.all().count()
            if result_page % 10 == 0:
                result_num = result_page // 10
            else:
                result_num = (result_page // 10) + 1
            try:
                page = int(stuff)
                if  page < 0 or page > result_num:
                    error = '请输入正确的整数'
                    ret['errors'] = error
                else:
                    current_page = page
                    USER_LIST = TestResult.objects.all().order_by('-created_at')
                    paginator = CustomPaginator(current_page, 11, USER_LIST, 12)
                    try:
                        paginator = paginator.page(current_page)
                    except PageNotAnInteger:
                        paginator = paginator.page(1)
                    except EmptyPage:
                        paginator = paginator.page(paginator.num_pages)
                    ret['result'] = paginator
                    ret['number'] = USER_LIST.count()
            except:
                error = '请输入整数'
                ret['errors'] = error
        else:
            re_list = TestResult.objects.filter(is_target=True).order_by('-created_at')
            re_num = re_list.count()
            if re_num == 0:
                error = '未匹配到数据'
                ret['errors'] = error
            else:
                ret['number'] = re_num
                paginator = pagedivide(request, re_list)
                ret['result'] = paginator
        return ret
    elif cata == 'allbaddata':
        current_page = 1
        USER_LIST = TestResult.objects.filter(is_target=True).order_by('-created_at')
        paginator = CustomPaginator(current_page, 11, USER_LIST, 12)
        try:
            paginator = paginator.page(current_page)
        except PageNotAnInteger:
            paginator = paginator.page(1)
        except EmptyPage:
            paginator = paginator.page(paginator.num_pages)
        ret['result'] = paginator
        ret['number'] = USER_LIST.count()
        if types == '1':
            result_page = TestResult.objects.filter(is_target=True).count()
            if result_page % 10 == 0:
                result_num = result_page // 10
            else:
                result_num = (result_page // 10) + 1
            try:
                page = int(stuff)
                if page < 0 or page > result_num:
                    error = '请输入正确的整数'
                    ret['errors'] = error
                else:
                    current_page = page
                    USER_LIST = TestResult.objects.filter(is_target=True).order_by('-created_at')
                    paginator = CustomPaginator(current_page, 11, USER_LIST, 12)
                    try:
                        paginator = paginator.page(current_page)
                    except PageNotAnInteger:
                        paginator = paginator.page(1)
                    except EmptyPage:
                        paginator = paginator.page(paginator.num_pages)
                    ret['result'] = paginator
                    ret['number'] = USER_LIST.count()
            except:
                error = '请输入整数'
                ret['errors'] = error
        else:
            re_list = TestResult.objects.filter(is_target=True).order_by('-created_at')
            re_num = re_list.count()
            if re_num == 0:
                error = '未匹配到数据'
                ret['errors'] = error
            else:
                ret['number'] = re_num
                paginator = pagedivide(request, re_list)
                ret['result'] = paginator
        return ret
    elif cata == 'baddata':
        current_page = 1
        USER_LIST = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at')
        paginator = CustomPaginator(current_page, 11, USER_LIST, 12)
        try:
            paginator = paginator.page(current_page)
        except PageNotAnInteger:
            paginator = paginator.page(1)
        except EmptyPage:
            paginator = paginator.page(paginator.num_pages)
        ret['result'] = paginator
        ret['number'] = USER_LIST.count()
        if types == '1':
            result_page = TestResult.objects.filter(is_target=True, is_check=False).count()
            if result_page % 10 == 0:
                result_num = result_page // 10
            else:
                result_num = (result_page // 10) + 1
            try:
                page = int(stuff)
                if  page < 0 or page > result_num:
                    error = '请输入正确的整数'
                    ret['errors'] = error
                else:
                    current_page = page
                    USER_LIST = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at')
                    paginator = CustomPaginator(current_page, 11, USER_LIST, 12)
                    try:
                        paginator = paginator.page(current_page)
                    except PageNotAnInteger:
                        paginator = paginator.page(1)
                    except EmptyPage:
                        paginator = paginator.page(paginator.num_pages)
                    ret['result'] = paginator
                    ret['number'] = USER_LIST.count()
            except:
                error = '请输入整数'
                ret['errors'] = error
        else:
            re_list = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at')
            re_num = re_list.count()
            if re_num == 0:
                error = '未匹配到数据'
                ret['errors'] = error
            else:
                ret['number'] = re_num
                paginator = pagedivide(request, re_list)
                ret['result'] = paginator
        return ret



#  分页GET方法处理
def page_get(types, page, sorts):
    ret = {'numbers': '', 'page': ''}
    if types == '1':
        result = TestDomain.objects.filter(name__icontains=sorts)
        result_nu = result.count()
        ret['numbers'] = result_nu
        ret['page'] = page_pa(page, result)
    return ret

#  分页
def page_pa(page, lists):
    paginator = CustomPaginator(int(page), 11, lists, 10)
    try:
        paginator = paginator.page(int(page))
    except PageNotAnInteger:
        paginator = paginator.page(1)
    except EmptyPage:
        paginator = paginator.page(paginator.num_pages)
    return paginator


#  拿出当前月所有检查天数
def searchbytime():
    a = time.localtime()
    day = calendar.monthrange(a[0], a[1])[1]
    day_list = []
    for i in range(1, day + 1):
        if i < 10:
            day_list.append('0' + str(i))
        else:
            day_list.append(str(i))
    return day_list


#  拿出每天的检验总数
def datahandle():
    a = time.localtime()
    day = searchbytime()
    result = []
    alldata = 0
    if a[1] < 10:
        for i in day:
            all_data_list = ResultNumber.objects.filter(created_at__startswith='{}-0{}-{}'.format(a[0], a[1], i))
            if all_data_list.count() == 0:
                alldata = 0
            else:
                for i in all_data_list:
                    alldata += i.all_data
            result.append(str(alldata))
            alldata = 0
    else:
        for i in day:
            all_data_list = ResultNumber.objects.filter(created_at__startswith='{}-{}-{}'.format(a[0], a[1], i))
            if all_data_list.count() == 0:
                alldata = 0
            else:
                for i in all_data_list:
                    alldata += i.all_data
            result.append(str(alldata))
            alldata = 0
    return result


#  拿出每天检验的名字次数
def baddatahandle():
    a = time.localtime()
    day = searchbytime()
    all_data = 0
    result = []
    if a[1] < 10:
        for i in day:
            all_data_list = TestResult.objects.filter(is_target=True, created_at__startswith='{}-0{}-{}'.format(a[0], a[1], i))
            all_data += all_data_list.count()
            result.append(all_data)
            all_data = 0
        return result
    else:
        for i in day:
            all_data_list = TestResult.objects.filter(is_target=True, created_at__startswith='{}-0{}-{}'.format(a[0], a[1], i))
            all_data += all_data_list.count()
            result.append(all_data)
            all_data = 0
        return result


#  获取所有月份
def getmonth():
    result_list = ['2017-07', '2017-08', '2017-09', '2017-10', '2017-11', '2017-12','2018-01', '2018-02', '2018-03', '2018-04', '2018-05', '2018-06','2018-07', '2018-08', '2018-09', '2018-10', '2018-11', '2018-12',]
    return result_list


#  获得每月检查次数
def getmonthdata():
    b = getmonth()
    result = []
    all_data = 0
    for i in b:
        all_data_list = ResultNumber.objects.filter(created_at__startswith='{}'.format(i))
        for num in all_data_list:
            all_data += num.all_data
        result.append(all_data)
        all_data = 0
    return result


#  获取每月有害的信息
def getmonthbaddata():
    b = getmonth()
    result = []
    all_data = 0
    for i in b:
        bad_data = TestResult.objects.filter(is_target=True, created_at__startswith='{}'.format(i))
        all_data += len(bad_data)
        result.append(all_data)
        all_data = 0
    return result


#  检验结果查询
def pag_get(types, page, sorts, catas):
    ret = {'numbers': '', 'page': ''}
    if catas == 'result':
        if types == '1':
            USER_LIST = TestResult.objects.all().order_by('-created_at')
            result_num = USER_LIST.count()
            ret['numbers'] = result_num
            ret['page'] = page_pa(page, USER_LIST)
            return ret
        elif types == '2':
            if int(sorts[-2:]) < 10:
                all_data_list = TestResult.objects.filter(
                    created_at__startswith='{}-0{}'.format(int(sorts[:4]), int(sorts[-2:]))).order_by('-created_at')
            else:
                all_data_list = TestResult.objects.filter(
                    created_at__startswith='{}-{}'.format(int(sorts[:4]), int(sorts[-2:]))).order_by('-created_at')
            ret['numbers'] = all_data_list.count()
            ret['page'] = page_pa(page, all_data_list)
            return ret
        elif types == '3':
            all_data_list = TestResult.objects.filter(origin_id=sorts).order_by('-created_at')
            ret['numbers'] = all_data_list.count()
            ret['page'] = page_pa(page, all_data_list)
            return ret
        else:
            all_list = TestResult.objects.all().order_by('-created_at')
            ret['numbers'] = all_list.count()
            ret['page'] = page_pa(page, all_list)
            return ret
    elif catas == 'allbaddata':
        if types == '1':
            USER_LIST = TestResult.objects.filter(is_target=True).order_by('-created_at')
            result_num = USER_LIST.count()
            ret['numbers'] = result_num
            ret['page'] = page_pa(page, USER_LIST)
            return ret
        elif types == '2':
            if int(sorts[-2:]) < 10:
                all_data_list = TestResult.objects.filter(is_target=True,
                    created_at__startswith='{}-0{}'.format(int(sorts[:4]), int(sorts[-2:]))).order_by('-created_at')
            else:
                all_data_list = TestResult.objects.filter(is_target=True,
                    created_at__startswith='{}-{}'.format(int(sorts[:4]), int(sorts[-2:]))).order_by('-created_at')
            ret['numbers'] = all_data_list.count()
            ret['page'] = page_pa(page, all_data_list)
            return ret
        elif types == '3':
            all_data_list = TestResult.objects.filter(origin_id=sorts, is_target=True).order_by('-created_at')
            ret['numbers'] = all_data_list.count()
            ret['page'] = page_pa(page, all_data_list)
            return ret
        else:
            all_list =TestResult.objects.filter(is_target=True).order_by('-created_at')
            ret['numbers'] = all_list.count()
            ret['page'] = page_pa(page, all_list)
            return ret
    elif catas == 'baddata':
        if types == '1':
            USER_LIST = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at')
            result_num = USER_LIST.count()
            ret['numbers'] = result_num
            ret['page'] = page_pa(page, USER_LIST)
            return ret
        elif types == '2':
            if int(sorts[-2:]) < 10:
                all_data_list = TestResult.objects.filter(is_target=True, is_check=False,
                    created_at__startswith='{}-0{}'.format(int(sorts[:4]), int(sorts[-2:]))).order_by('-created_at')
            else:
                all_data_list = TestResult.objects.filter(is_target=True, is_check=False,
                    created_at__startswith='{}-{}'.format(int(sorts[:4]), int(sorts[-2:]))).order_by('-created_at')
            ret['numbers'] = all_data_list.count()
            ret['page'] = page_pa(page, all_data_list)
            return ret
        elif types == '3':
            all_data_list = TestResult.objects.filter(origin_id=sorts, is_target=True, is_check=False).order_by('-created_at')
            ret['numbers'] = all_data_list.count()
            ret['page'] = page_pa(page, all_data_list)
            return ret
        else:
            all_list = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at')
            ret['numbers'] = all_list.count()
            ret['page'] = page_pa(page, all_list)
            return ret


def zip_dir():
    filelist = []
    a = os.getcwd()
    startdir = a + '\\testappp\download'
    for root, dirs, files in os.walk(startdir):
        for name in files:
            filelist.append(os.path.join(root, name))
    zf = zipfile.ZipFile('testresult.zip', "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(startdir):]
        zf.write(tar, arcname)
    zf.close()


#  下载
def download(request, name):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    zip_dir()
    the_file_name = 'testresult.zip'
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="testresult.zip"'
    return response


#  检测数据分析
def changelocation(li):
    h = ''
    result = ''
    try:
        if '省' in li or '市' in li:
            h = '中国'
        elif li == '北美地区':
            h = '美国'
        elif li == '亚太地区':
            h = '中国'
        else:
            h = li
    except:
        pass
    if h == '美国':
        result = 'United States of America'
    elif h == '俄罗斯':
        result = 'Russia'
    else:
        a = os.getcwd()
        f = open(a + '\\testappp\static\js\countryname.json', encoding='utf-8')
        name = json.load(f)
        for i in name['country']:
            if h in i['chineses']:
                result = i['english']
                break
    return result


def alldatahandle(li):
    alldata = {}
    alldata_list = []
    for i in li[0]:
        alldata.setdefault('name', li[0][i])
        alldata.setdefault('itemStyle', {'normal': {'color': 'red'}})
    alldata_list.append(alldata)
    alldata = {}
    if len(li) >= 1:
        for i in range(1, len(li)):
            for m in li[i]:
                alldata.setdefault('name', li[i][m])
                alldata.setdefault('itemStyle', {'normal': {'color': 'gold'}})
            alldata_list.append(alldata)
            alldata = {}
    return alldata_list


def singlebaddata(li, color):
    alldata = {}
    alldata_list = []
    c = 0
    if len(li) == 1:
        for i in li:
            alldata.setdefault('name', li[i])
            alldata.setdefault('itemStyle', {'normal': {'color': 'red'}})
        alldata_list.append(alldata)
        alldata = {}
    else:
        for i in li:
            if c == 0:
                alldata.setdefault('name', li[i])
                alldata.setdefault('itemStyle', {'normal': {'color': 'red'}})
                c += 1
                alldata_list.append(alldata)
                alldata = {}
            else:
                alldata.setdefault('name', li[i])
                alldata.setdefault('itemStyle', {'normal': {'color': color}})
                alldata_list.append(alldata)
                alldata = {}
    return alldata_list

