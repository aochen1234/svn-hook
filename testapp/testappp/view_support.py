import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from testappp.models import ResultNumber, TestResult, TestRule
import time


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
    result_num = TestResult.objects.filter(is_target=True).order_by('-created_at')
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
            paginator = CustomPaginator(current_page, 11, USER_LIST, 10)
        except:
            current_page = 1
            paginator = CustomPaginator(current_page, 11, USER_LIST, 10)

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
                    paginator = CustomPaginator(current_page, 11, USER_LIST, 10)
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
        elif types == '2':
            try:
                int(stuff)
                if int(stuff[:4]) < 2017 or int(stuff[-2:]) < 0 or int(stuff[-2:]) > 12 or len(stuff) != 6:
                    error = '请输入合适的年月'
                    ret['errors'] = error
                else:
                    try:
                        if int(stuff[-2:]) < 10:
                            all_data_list = TestResult.objects.filter(created_at__startswith='{}-0{}'.format(int(stuff[:4]), int(stuff[-2:]))).order_by('-created_at')
                        else:
                            all_data_list = TestResult.objects.filter(created_at__startswith='{}-{}'.format(int(stuff[:4]), int(stuff[-2:]))).order_by('-created_at')
                        ret['number'] = all_data_list.count()
                        paginator = pagedivide(request, all_data_list)
                        ret['result'] = paginator
                    except:
                        error = '当月未检测'
                        ret['errors'] = error
            except:
                error = '请输入合适的年月'
                ret['errors'] = error
        elif types == '3':
            try:
                origin_id = int(stuff)
                result_list = TestResult.objects.filter(origin_id=origin_id).order_by('-created_at')
                result_n = result_list.count()
                if result_n == 0:
                    error = '该ID不存在'
                    ret['errors'] = error
                else:
                    ret['number'] = result_n
                    paginator = pagedivide(request, result_list)
                    ret['result'] = paginator
            except:
                error = '请输入合适的ID'
                ret['errors'] = error
        elif types == '4':
            try:
                re = TestRule.objects.get(name=stuff)
                result_list = re.testresult_set.all().order_by('-created_at')
                res_num = result_list.count()
                if res_num == 0:
                    error = '该规则未匹配到数据'
                    ret['errors'] = error
                else:
                    ret['number'] = res_num
                    paginator = pagedivide(request, result_list)
                    ret['result'] = paginator
            except:
                error = '该条规则不存在'
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
        if types == '1':
            result_page = TestResult.objects.filter(is_target=True).count()
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
                    USER_LIST = TestResult.objects.filter(is_target=True).order_by('-created_at')
                    paginator = CustomPaginator(current_page, 11, USER_LIST, 10)
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
        elif types == '2':
            try:
                int(stuff)
                if int(stuff[:4]) < 2017 or int(stuff[-2:]) < 0 or int(stuff[-2:]) > 12 or len(stuff) != 6:
                    error = '请输入合适的年月'
                    ret['errors'] = error
                else:
                    try:
                        if int(stuff[-2:]) < 10:
                            all_data_list = TestResult.objects.filter(is_target=True, created_at__startswith='{}-0{}'.format(int(stuff[:4]), int(stuff[-2:]))).order_by('-created_at')
                        else:
                            all_data_list = TestResult.objects.filter(is_target=True, created_at__startswith='{}-{}'.format(int(stuff[:4]), int(stuff[-2:]))).order_by('-created_at')
                        ret['number'] = all_data_list.count()
                        paginator = pagedivide(request, all_data_list)
                        ret['result'] = paginator
                    except:
                        error = '当月未检测'
                        ret['errors'] = error
            except:
                error = '请输入合适的年月'
                ret['errors'] = error
        elif types == '3':
            try:
                origin_id = int(stuff)
                result_list = TestResult.objects.filter(is_target=True, origin_id=origin_id).order_by('-created_at')
                result_n = result_list.count()
                if result_n == 0:
                    error = '该ID不存在'
                    ret['errors'] = error
                else:
                    ret['number'] = result_n
                    paginator = pagedivide(request, result_list)
                    ret['result'] = paginator
            except:
                error = '请输入合适的ID'
                ret['errors'] = error
        elif types == '4':
            try:
                re = TestRule.objects.get(name=stuff)
                result_list = re.testresult_set.all().order_by('-created_at')
                res_num = result_list.count()
                if res_num == 0:
                    error = '该规则未匹配到数据'
                    ret['errors'] = error
                else:
                    ret['number'] = res_num
                    paginator = pagedivide(request, result_list)
                    ret['result'] = paginator
            except:
                error = '该条规则不存在'
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
                    paginator = CustomPaginator(current_page, 11, USER_LIST, 10)
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
        elif types == '2':
            try:
                int(stuff)
                if int(stuff[:4]) < 2017 or int(stuff[-2:]) < 0 or int(stuff[-2:]) > 12 or len(stuff) != 6:
                    error = '请输入合适的年月'
                    ret['errors'] = error
                else:
                    try:
                        if int(stuff[-2:]) < 10:
                            all_data_list = TestResult.objects.filter(is_check=False, is_target=True, created_at__startswith='{}-0{}'.format(int(stuff[:4]), int(stuff[-2:]))).order_by('-created_at')
                        else:
                            all_data_list = TestResult.objects.filter(is_check=False, is_target=True, created_at__startswith='{}-{}'.format(int(stuff[:4]), int(stuff[-2:]))).order_by('-created_at')
                        ret['number'] = all_data_list.count()
                        paginator = pagedivide(request, all_data_list)
                        ret['result'] = paginator
                    except:
                        error = '当月未检测'
                        ret['errors'] = error
            except:
                error = '请输入合适的年月'
                ret['errors'] = error
        elif types == '3':
            try:
                origin_id = int(stuff)
                result_list = TestResult.objects.filter(is_check=False, is_target=True, origin_id=origin_id).order_by('-created_at')
                result_n = result_list.count()
                if result_n == 0:
                    error = '该ID不存在'
                    ret['errors'] = error
                else:
                    ret['number'] = result_n
                    paginator = pagedivide(request, result_list)
                    ret['result'] = paginator
            except:
                error = '请输入合适的ID'
                ret['errors'] = error
        elif types == '4':
            try:
                re = TestRule.objects.get(name=stuff)
                result_list = re.testresult_set.filter(is_check=False).order_by('-created_at')
                res_num = result_list.count()
                if res_num == 0:
                    error = '该规则未匹配到数据'
                    ret['errors'] = error
                else:
                    ret['number'] = res_num
                    paginator = pagedivide(request, result_list)
                    ret['result'] = paginator
            except:
                error = '该条规则不存在'
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
    che = r'{}'.format(sorts)
    result_li = []
    if types == '1':
        result = TestRule.objects.all()
        for i in result:
            ismatch = re.search(che, i.name, re.S)
            if ismatch:
                result_li.append(i)
        ret['numbers'] = len(result_li)
        ret['page'] = page_pa(page, result_li)
        return ret
    elif types == '2':
        result = TestRule.objects.all()
        for i in result:
            ismatch = re.search(che, i.url, re.S)
            if ismatch:
                result_li.append(i)
        ret['numbers'] = len(result_li)
        ret['page'] = page_pa(page, result_li)
        return ret
    elif types == '3':
        result = TestRule.objects.all()
        for i in result:
            ismatch = re.search(che, i.cookie, re.S)
            if ismatch:
                result_li.append(i)
        ret['numbers'] = len(result_li)
        ret['page'] = page_pa(page, result_li)
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
    b = []
    try:
        if a[1] < 10:
            all_data_list = ResultNumber.objects.filter(created_at__startswith='{}-0{}'.format(a[0], a[1]))
            for i in all_data_list:
                b.append(i.created_at.strftime('%d'))
            return sorted(list(set(b)))
        else:
            all_data_list = ResultNumber.objects.filter(created_at__startswith='{}-{}'.format(a[0], a[1]))
            for i in all_data_list:
                b.append(i.created_at.strftime('%d'))
            return sorted(list(set(b)))
    except:
        return b


#  拿出每天的检验总数
def datahandle():
    a = time.localtime()
    day = searchbytime()
    all_data = 0
    result = []
    if a[1] < 10:
        for i in day:
            all_data_list = ResultNumber.objects.filter(created_at__startswith='{}-0{}-{}'.format(a[0], a[1], i))
            for item in all_data_list:
                all_data += item.all_data
            result.append(all_data)
            all_data = 0
        return result
    else:
        for i in day:
            all_data_list = ResultNumber.objects.filter(created_at__startswith='{}-0{}-{}'.format(a[0], a[1], i))
            for item in all_data_list:
                all_data += item.all_data
            result.append(all_data)
            all_data = 0
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


#  时间整理
def timehandle():
    a = time.localtime()
    result = []
    day = searchbytime()
    if day == []:
        return result
    else:
        if a[1] < 10:
            for i in day:
                result.append(('0{}' + i).format(a[1]))
            return result
        else:
            for i in day:
                result.append(('{}' + i).format(a[1]))
            return result


#  获取所有月份
def getmonth():
    a = time.localtime()
    num = a[0] - 2017
    number = a[1] - 7
    result = []
    result_list = []
    if num == 0:
        if number == 0:
            result.append('2017-' + '07')
        else:
            for i in range(7, (8 + number)):
                if i < 10:
                    result.append('2017-0' + str(i))
                else:
                    result.append('2017-' + str(i))
    else:
        number = a[1]
        result = ['2017-07', '2017-08', '2017-09', '2017-10', '2017-11', '2017-12']
        for i in range(1, number + 1):
            if i < 10:
                result.append('2018-0' + str(i))
            else:
                result.append('2018-' + str(i))
    result = ['2017-07', '2017-08', '2017-09', '2017-10', '2017-11', '2017-12']
    for i in result:
        try:
            ResultNumber.objects.filter(created_at__startswith='{}'.format(i))[0]
            result_list.append(i)
        except:
            pass
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


#  检验规则查找
def rulesearch_set(request, types, stuff):
    ret = {'result':'', 'errors': '', 'number': '', 'type': '', 'sort': ''}
    if len(stuff) >= 3:
        if types == '1':
            result = TestRule.objects.filter(name__icontains=stuff)
            result_nu = result.count()
            ret['number'] = result_nu
            paginator = pagedivide(request, result)
            ret['result'] = paginator
        elif types == '2':
            result = TestRule.objects.filter(url__icontains=stuff)
            result_nu = result.count()
            ret['number'] = result_nu
            paginator = pagedivide(request, result)
            ret['result'] = paginator
        elif types == '3':
            result = TestRule.objects.filter(cookie__icontains=stuff)
            result_nu = result.count()
            ret['number'] = result_nu
            paginator = pagedivide(request, result)
            ret['result'] = paginator
    else:
        error = '输入长度最少3位'
        ret['errors'] = error
    return ret


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
        elif types == '4':
            all_list = TestRule.objects.get(name=sorts)
            all_data_list = all_list.testresult_set.all().order_by('-created_at')
            ret['numbers'] = all_data_list.count()
            ret['page'] = page_pa(page, all_data_list)
            return ret
        else:
            all_list = TestResult.objects.filter(is_target=True).order_by('-created_at')
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
        elif types == '4':
            all_list = TestRule.objects.get(name=sorts)
            all_data_list = all_list.testresult_set.all().order_by('-created_at')
            ret['numbers'] = all_data_list.count()
            ret['page'] = page_pa(page, all_data_list)
            return ret
        else:
            all_list = TestResult.objects.filter(is_target=True).order_by('-created_at')
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
        elif types == '4':
            all_list = TestRule.objects.get(name=sorts)
            all_data_list = all_list.testresult_set.filter(is_check=False).order_by('-created_at')
            ret['numbers'] = all_data_list.count()
            ret['page'] = page_pa(page, all_data_list)
            return ret
        else:
            all_list = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at')
            ret['numbers'] = all_list.count()
            ret['page'] = page_pa(page, all_list)
            return ret
