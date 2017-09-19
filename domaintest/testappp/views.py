import re
import json
import cx_Oracle
import shutil
import random
import datetime
import requests

from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import NewUser, TestSet
from haystack.forms import SearchForm
from .view_support import *
from .forms import ChangePasswordForm



# Create your views here.
#  ajax处理账户
@csrf_exempt
def user_ajax(request):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        user = request.POST.get('username',)
        result = NewUser.objects.filter(username=user)
        if len(result) > 0:
            ret['status'] = 1002
        else:
            ret['error'] = '账户错误，请重新输入'
        return HttpResponse(json.dumps(ret))


#  处理登陆
def log_handle(request):
    error = '密码错误，请重新输入'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            res = HttpResponseRedirect('/domain/')
            res.set_cookie('username', username)
            return res
        else:
            return render(request, 'users/login.html', {'error': error})
    return render(request, 'users/login.html')


#  处理退出
@login_required
def log_out(request):
    logout(request)
    return HttpResponseRedirect('/')


#  首页
@login_required
def index(request):
    wait_time = waitcheckdatatime()
    result_list = resultdisplay(4)
    result_num = baddata()
    bad_data = len(result_num)
    if bad_data <= 0:
        try:
            bad_data_time = TestResult.objects.filter(is_target=True, is_check=True).order_by('-created_at')[0].created_at
        except:
            bad_data_time = 0
    else:
        bad_data_time = result_num[0].created_at
    return render(request, 'index.html', locals())


#  获取检验头信息
@login_required
@csrf_exempt
def getheader(request):
    if request.method == 'POST':
        host = request.POST.get('host',)
        cookies = request.POST.get('cookie',).replace('请求或COOKIE:<br>', '')
        if cookies.startswith('GET') or cookies.startswith('POST'):
            ret = getheaderinfo(cookies)
            types = ret['type']
            if ret['url'].strip().startswith('http'):
                url = ret['url'].strip()
                del ret['url']
            else:
                if 'Referer' in ret:
                    url = ret['Referer'] + ret['url'].strip()
                else:
                    url = 'http://' + host + ret['url'].strip()
                try:
                    del ret['url']
                    del ret['Cookie']
                    del ret['type']
                except KeyError:
                    pass
                b = r'h.*?1.1'
                c = re.search(b, url)
                url = c.group()
            if types == 'GET':
                r = requests.get(url, headers=ret)
            else:
                r = requests.post(url, headers=ret)
            return HttpResponse(json.dumps(r.text))
        else:
            if host != '':
                url = 'http://' + host
                r = requests.get(url)
                return HttpResponse(json.dumps(r.text))
            else:
                pass


@login_required
@csrf_exempt
def changestatus(request):
    if request.method == 'POST':
        ret = {'success': 'ture'}
        hostid = request.POST.get('hostid', )
        try:
            a = TestResult.objects.get(id=hostid)
            a.is_check = True
            a.save()
        except:
            pass
        return HttpResponse(json.dumps(ret))


#  检验结果查看
@login_required
def result_dis(request):
    cata = request.GET.get('catas')
    user = request.user
    if cata == 'result':
        USER_LIST = TestResult.objects.all().order_by('-created_at')
        result_num = USER_LIST.count()
        paginator = pagedivide(request, USER_LIST)
        return render(request, 'result/result_dis.html', {'user': user, 'users':paginator, 'result': result_num, "cata": cata})
    elif cata == 'allbaddata':
        USER_LIST = TestResult.objects.filter(is_target=True).order_by('-created_at')
        result_num = USER_LIST.count()
        paginator = pagedivide(request, USER_LIST)
        return render(request, 'result/result_dis.html', {'user': user, 'users':paginator, 'result': result_num, "cata": cata, 'status': '异常'})
    elif cata == 'baddata':
        USER_LIST = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at')
        result_num = USER_LIST.count()
        paginator = pagedivide(request, USER_LIST)
        return render(request, 'result/result_dis.html', {'user': user, 'users':paginator, 'result': result_num, "cata": cata, 'status': '异常'})
    else:
        USER_LIST = TestResult.objects.all().order_by('-created_at')
        result_num = USER_LIST.count()
        paginator = pagedivide(request, USER_LIST)
        return render(request, 'result/result_dis.html', {'user': user, 'users': paginator, 'result': result_num, "cata": 'result'})



#  累计有害信息查看
@login_required
def baddatacheck(request):
    user = request.user
    result_l = TestResult.objects.filter(is_target=True).order_by('-created_at')
    result_num = TestResult.objects.filter(is_target=True).count()
    paginator = pagedivide(request, result_l)
    return render(request, 'result/result_dis.html', {'user': user, 'users':paginator, 'result': result_num})


#  待查看结果
@login_required
def waitdata(request):
    user = request.user
    try:
        result_list = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at')
        result_num = result_list.count()
    except:
        result_list = None
        result_num = 0
    paginator = pagedivide(request, result_list)
    return render(request, 'result/result_dis.html', {'user': user, 'users': paginator, 'result': result_num})


#  待查看结果的详细信息
@login_required
def alldata(request, re_id):
    user = request.user
    result = get_object_or_404(TestResult, id=re_id)
    result.is_check = True
    result.save()
    return render(request, 'result/baddataallda.html', locals())


#  查看结果的详细信息
@login_required
def checkalldata(request, re_id):
    user = request.user
    result = get_object_or_404(TestResult, id=re_id)
    result.is_check = True
    result.save()
    return render(request, 'result/baddataallda.html', locals())


#  检验规则查看
@login_required
def testrulecheck(request):
    user = request.user
    cus_list = TestDomain.objects.all().order_by('-created_at')
    result = cus_list.count()
    paginator = pagedivide(request, cus_list)

    return render(request, 'rule/testrulecheck.html', {'user': user, 'users': paginator, 'result': result})


#  检验规则删除
@login_required
def testruledel(request, re_id):
    user = request.user
    c = get_object_or_404(TestDomain, id=re_id)
    rule_id = re_id
    return render(request, 'rule/testruledel.html', locals())


#  查看已匹配的域名
@login_required
def domaincheck(request, re_id):
    cata = 'allbaddata'
    user = request.user
    USER_LIST = TestResult.objects.filter(is_target=True, testdomain__id=re_id).order_by('-created_at')
    result_num = USER_LIST.count()
    paginator = pagedivide(request, USER_LIST)
    return render(request, 'result/result_dis.html', {'user': user, 'users': paginator, 'result': result_num, "cata": cata})

#  检验规则增加
@login_required
def testruleup(request):
    user = request.user
    return render(request, 'rule/ruleform.html', locals())


#  处理检验规则提交
@login_required
@csrf_exempt
def ruleup(request):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        name = request.POST.get('names', ).strip(' ')
        content = request.POST.get('content', ).strip(' ')
        types = request.POST.get('type', )
        if types == 'option1':
            cata = 'webshell'
        else:
            cata = 'domain'
        if name == '':
            b = random.randint(0, 100)
            name = '规则' + str(b)
        if content == '':
            ret['error'] = '请输入规则条件'
        else:
            result = TestDomain.objects.filter(content=content, ruletype=cata)
            if result.count() > 0:
                ret['error'] = '该条规则已存在,请重新输入'
            else:
                TestDomain.objects.create(name=name, content=content, ruletype=cata)
                ret['status'] = 1002
        return HttpResponse(json.dumps(ret))


#  检验规则删除
@login_required
@csrf_exempt
def ruledel(request, rule_id, c_id):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        is1 = request.POST.get('is1', )
        is2 = request.POST.get('is2', )
        result = get_object_or_404(TestDomain, id=c_id)
        if is1 == 'true' and is2 == 'true':
            ret['status'] = 1002
            try:
                a = result.testresult_set.all()
                for i in a:
                    i.is_target = False
                    i.is_check = False
                    i.save()
            except:
                pass
            finally:
                result.delete()
        elif is1 == 'true' and is2 == 'false':
            ret['status'] = 1002
            result.delete()
        else:
            ret['error'] = '请重新选择或返回'
        return HttpResponse(json.dumps(ret))


#  检验规则修改
@login_required
def testrulechange(request, re_id):
    user = request.user
    rule_id = re_id
    return render(request, 'rule/changeruleform.html', locals())


#  获取检验规则信息
@login_required
def getruleinfo(request, re_id):
    if request.method == 'GET':
        ret = {'name': '', 'content': '', 'type': ''}
        try:
            result = TestDomain.objects.get(id=re_id)
            ret['name'] = result.name
            ret['content'] = result.content
            ret['type'] = result.ruletype
        except:
            ret = {'name': '', 'content': '', 'type': ''}
        return HttpResponse(json.dumps(ret))


#  最终修改检验规则
@login_required
@csrf_exempt
def rulechange(request, re_id):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        name = request.POST.get('names', )
        content = request.POST.get('content', )
        if content == '':
            ret['error'] = '请输入合适的内容'
        else:
            if name == '':
                name = content
            result = TestDomain.objects.get(id=re_id)
            result.name = name
            result.content = content
            result.save()
            ret['status'] = 1002
        return HttpResponse(json.dumps(ret))


#  检验来源设置
@login_required
def test_source(request):
    user = request.user
    try:
        dbinfo = TestSet.objects.all()[0]
    except:
        dbinfo = []
    return render(request, 'testsource/testsource.html', locals())


#  检验来源表单
@login_required
def sourceset(request):
    user = request.user
    try:
        dbinfo = TestSet.objects.all()[0]
    except:
        dbinfo = []
    return render(request, 'testsource/sourceform.html', locals())



#  检验速度表单
@login_required()
def speedset(request):
    user = request.user
    try:
        db = TestSet.objects.all()[0]
        speed = db.starttime
    except:
        speed = 0
    return render(request, 'testsource/speedsets.html', locals())


#  检验速度设置提交表单处理
@login_required
@csrf_exempt
def speedposthandle(request):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        spe = request.POST.get('speed', )
        try:
            speed = spe
            int(speed)
            if len(speed) < 8:
                ret['error'] = '请输入正确的年份'
            elif int(speed[4:6]) > 12 or int(speed[4:6]) < 0:
                ret['error'] = '请输入正确的月份'
            elif int(speed[6:]) > 31 or int(speed[6:]) < 0:
                ret['error'] = '请输入正确的天数'
            else:
                a = datetime.datetime.now()
                b = str(a).split(' ')[0]
                if int(spe[7:]) < 10:
                    c = spe[:4] + '-' + spe[4:6] + '-0' + spe[7:]
                else:
                    c = spe[:4] + '-' + spe[4:6] + '-' + spe[7:]
                if c > b:
                    ret['error'] = '时间设置错误,超过当前日期'
                else:
                    speedresult = TestSet.objects.all()[0]
                    speedresult.starttime = c
                    speedresult.save()
                    ret['status'] = 1002
        except:
            ret['error'] = '日期格式错误,请重新输入'
        return HttpResponse(json.dumps(ret))


#  检验来源表单验证
@login_required
@csrf_exempt
def infoset(request):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        ip = request.POST.get('ips', ).strip(' ')
        port = request.POST.get('ports', ).strip(' ')
        username = request.POST.get('usernames', ).strip(' ')
        password = request.POST.get('passwords', ).strip(' ')
        type = request.POST.get('types', ).strip(' ')
        ischeck = request.POST.get('ischecked', )
        try:
            conn = cx_Oracle.connect(username, password, ip + ":" + (port) + "/" + type)
            cursor = conn.cursor()
            re = TestSet.objects.all().count()
            if re == 0:
                TestSet.objects.create(host=ip, port=port, username=username, password=password, type=type, lastid='0')
                ret['status'] = 1002
            else:
                result = TestSet.objects.all().order_by('-created_at')[0]
                result.host = ip
                result.port = port
                result.username = username
                result.password = password
                result.type = type
                if ischeck == 'true':
                    result.lastid = '0'
                    result.save()
                    ret['status'] = 1002
                else:
                    ret['status'] = 1002
                    result.save()
            cursor.close()
            conn.close()
        except cx_Oracle.DatabaseError as e:
            source = {'name': 'ORA-01017', 'host': 'ORA-12170', 'port': 'ORA-12541', 'orcl': 'ORA-12514'}
            if str(e)[:9] == source['name']:
                ret['error'] = '数据库用户名或密码错误,请重新配置'
            elif str(e)[:9] == source['host']:
                ret['error'] = '数据库IP地址配置错误,请重新配置'
            elif str(e)[:9] == source['port']:
                ret['error'] = '数据库端口配置错误,请重新配置'
            elif str(e)[:9] == source['orcl']:
                ret['error'] = '数据库名称配置错误,请重新配置'
            else:
                ret['error'] = '数据库配置错误,请重新配置'
        return HttpResponse(json.dumps(ret))


#  获取所有月份信息
@login_required
@csrf_exempt
def getmonthalldata(request):
    try:
        a = getmonth()
        b = getmonthdata()
        c = getmonthbaddata()
        ret = {}
        ret['time'] = a
        ret['alldata_list'] = b
        ret['allbdata_list'] = c
    except:
        ret = {'time': [], 'alldata_list': [], 'allbdata_list': []}
    return HttpResponse(json.dumps(ret))


#  ajax获取配置信息并显示
@login_required
def infoget(request):
    if request.method == 'GET':
        ret = {'ip': '', 'port': '', 'type': '', 'username': '', 'password': '', 'table': ''}
        try:
            result = TestSet.objects.all()[0]
            ret['ip'] = result.host
            ret['port'] = result.port
            ret['type'] = result.type
            ret['username'] = result.username
            ret['password'] = result.password
            ret['table'] = result.table
        except:
            ret = {'ip': '', 'port': '', 'type': '', 'username': '', 'password': '', 'table': ''}
        return HttpResponse(json.dumps(ret))


@login_required
def accountform(request):
    form = ChangePasswordForm(user=request.user)
    return render(request, 'users/accountform.html', locals())


#  账户设置
@login_required
def accountset(request):
    if request.method =='POST':
        form = ChangePasswordForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'users/accountform.html', locals())


#  检验结果查询处理
@login_required
@csrf_exempt
def search(request, cata):
    if request.method == 'GET':
        user = request.user
        types = request.GET.get('type')
        page = request.GET.get('page')
        sorts = request.GET.get('sort')
        catas = request.GET.get('catas')
        res = pag_get(types, page, sorts, catas)
        return render(request, 'result/result_dis.html', {'user': user, 'users':res['page'], 'result': res['numbers'], 'type': types, 'sort':sorts, 'cata': catas})

    if request.method == 'POST':
        user = request.user
        types = request.POST.get('myselect',)
        stuff = request.POST.get('stuff', )
        if types == None:
            types = '1'
        else:
            pass
        result = search_set(request, types, stuff, cata)
        paginator = result['result']
        if types == '1':
            if result['errors'] == '10':
                return render(request, 'result/result_dis.html', {'user': user, 'users': paginator, 'result': result['number'], 'type': types, 'sort': stuff, 'cata': cata})
            else:
                return render(request, 'result/result_dis.html', {'user': user, 'errors': result['errors'], 'cata': cata, 'result': result['number'], 'users': paginator})
        else:
            if result['errors'] == '10':
                result = result['number']
                return render(request, 'result/result_dis.html', {'user': user, 'users': paginator, 'result': result, 'type': types, 'sort': stuff, 'cata': cata})
            else:
                return render(request, 'result/result_dis.html', {'user': user, 'errors': result['errors'], 'cata': cata, 'result': result['number'], 'users': paginator})


#  月份查看
@login_required
def monthcheck(request):
    user = request.user
    return render(request, 'result/monthcheck.html', locals())


#  检验规则搜索处理
@login_required
def rulesearch(request):
    if request.method == 'GET':
        user = request.user
        types = request.GET.get('type')
        page = request.GET.get('page')
        sorts = request.GET.get('sort')
        res = page_get(types, page, sorts)
        success = '10'
        return render(request, 'rule/testrulecheck.html', {'user': user, 'success' :success, 'users':res['page'], 'result': res['numbers'], 'type': types, 'sort':sorts})

    if request.method == 'POST':
        user = request.user
        types = request.POST.get('myselect',)
        stuff = request.POST.get('stuff', )
        result = rulesearch_set(request, types, stuff)
        if result['errors'] == '':
            paginator = result['result']
            success = '10'
            return render(request, 'rule/testrulecheck.html', {'user': user, 'success' :success, 'users': paginator, 'result': result['number'], 'type': types, 'sort': stuff})
        else:
            paginator = result['result']
            return render(request, 'rule/testrulecheck.html', {'user': user, 'errors': result['errors'], 'result': result['number'], 'users': paginator, 'type': 11, 'sort':None})


#  获取检验规则信息
@csrf_exempt
def gettestrule(request, re_id):
    if request.method == 'POST':
        ret = {'url': '', 'cookie': ''}
        name = request.POST.get('name',)
        try:
            result = get_object_or_404(TestRule, name=name)
            ret['url'] = result.url
            ret['cookie'] = result.cookie
        except:
            ret = {'url': '', 'cookie': ''}
        return HttpResponse(json.dumps(ret))


#  测试
def testa(request):
    a = []
    c = {}
    for i in range(10):
        c.setdefault('h', i)
        a.append(c)
        c = {}
    return render(request, 'test.html', locals())


@csrf_exempt
def getalldata(request):
    all_data = alldataorderbymonth()
    wait_chec = waitcheckdata()
    bad_data = len(baddata())
    wait_check_num = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at').count()
    res = {'wait_chec': str(wait_chec), 'all_data': str(all_data), 'bad_data': str(bad_data), 'wait_bad_data': str(wait_check_num)}
    result = json.dumps(res)
    return HttpResponse(result)


#  获取图表信息
@csrf_exempt
def getdata(request):
    times = searchbytime()
    alldata_list = datahandle()
    res = {'time': times, 'alldata_list': alldata_list}
    result = json.dumps(res)
    return HttpResponse(result)


#  自定义页面未找到
@login_required
def page_not_found(request):
    user = request.user
    return render(request, '404.html', locals())


#  500错误
def page_erro(request):
    user = request.user
    return render(request, '500.html', locals())


#  全文搜索
@login_required
def full_search(request):
    keywords = request.GET['q'].strip()
    if keywords == '':
        a = result_dis(request)
        return a
    else:
        user = request.user
        sform = SearchForm(request.GET)
        posts = sform.search()
        paginator = pagedivide(request, posts)
        result = posts.count()
        if result == 0:
            a = result_dis(request)
            return a
        else:
            return render(request, 'search/search.html', {'user': user, 'users': paginator, 'result': result,'query': keywords})


#  检验异常数据分析
@login_required
def getba(request):
    ret = {}
    f = TestResult.objects.filter(is_target=True)
    if f.count() == 0:
        pass
    else:
        a = get_baddata(f)
        b = get_all_baddata(f)
        rulename = ['所有异常IP']
        for i in a['rulename']:
            rulename.append(i)
        allbaddata = alldatahandle(b)
        first = singlebaddata(a['alldata'][0], 'rgba(14, 241, 242, 0.8)')
        second = singlebaddata(a['alldata'][1], 'rgba(37, 140, 249, 0.8)')
        third = singlebaddata(a['alldata'][2], 'yellowgreen')
        ret['name'] = rulename
        ret['alldata'] = allbaddata
        ret['first'] = first
        ret['second'] = second
        ret['third'] = third
    return HttpResponse(json.dumps(ret))


