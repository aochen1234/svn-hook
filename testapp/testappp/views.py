from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import NewUser, TestSet
from .view_support import *
from .test_handle import main_handle
from .forms import ChangePasswordForm
import json
import cx_Oracle


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
            res = HttpResponseRedirect('/webshell/')
            res.set_cookie('username', username)
            return res
        else:
            return render(request, 'login.html', {'error': error})
    return render(request, 'login.html')


#  处理退出
@login_required
def log_out(request):
    logout(request)
    return HttpResponseRedirect('/')


#  首页
@login_required
def index(request):
    all_data = alldataorderbymonth()
    wait_check_data = waitcheckdata()
    wait_time = waitcheckdatatime()
    result_list = resultdisplay(4)
    result_num = baddata()
    wait_check_num = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at').count()
    bad_data = len(result_num)
    if bad_data <= 0:
        try:
            bad_data_time = TestResult.objects.filter(is_target=True, is_check=True).order_by('-created_at')[0].created_at
        except:
            bad_data_time = 0
    else:
        bad_data_time = result_num[0].created_at
    return render(request, 'index.html', locals())


#  检验结果查看
@login_required
def result_dis(request):
    cata = request.GET.get('catagory')
    user = request.user
    if cata == 'result':
        USER_LIST = TestResult.objects.all().order_by('-created_at')
        result_num = USER_LIST.count()
        paginator = pagedivide(request, USER_LIST)
        return render(request, 'result_dis.html', {'user': user, 'users':paginator, 'result': result_num, "cata": cata})
    elif cata == 'allbaddata':
        USER_LIST = TestResult.objects.filter(is_target=True).order_by('-created_at')
        result_num = USER_LIST.count()
        paginator = pagedivide(request, USER_LIST)
        return render(request, 'result_dis.html', {'user': user, 'users':paginator, 'result': result_num, "cata": cata})
    elif cata == 'baddata':
        USER_LIST = TestResult.objects.filter(is_target=True, is_check=False).order_by('-created_at')
        result_num = USER_LIST.count()
        paginator = pagedivide(request, USER_LIST)
        return render(request, 'result_dis.html', {'user': user, 'users':paginator, 'result': result_num, "cata": cata})
    else:
        USER_LIST = TestResult.objects.all().order_by('-created_at')
        result_num = USER_LIST.count()
        paginator = pagedivide(request, USER_LIST)
        return render(request, 'result_dis.html', {'user': user, 'users': paginator, 'result': result_num, "cata": 'result'})

#  累计有害信息查看
@login_required
def baddatacheck(request):
    user = request.user
    result_l = TestResult.objects.filter(is_target=True).order_by('-created_at')
    result_num = TestResult.objects.filter(is_target=True).count()
    paginator = pagedivide(request, result_l)
    return render(request, 'result_dis.html', {'user': user, 'users':paginator, 'result': result_num})


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
    return render(request, 'result_dis.html', {'user': user, 'users': paginator, 'result': result_num})


#  待查看结果的详细信息
@login_required
def alldata(request, re_id):
    user = request.user
    result = get_object_or_404(TestResult, id=re_id)
    result.is_check = True
    result.save()
    return render(request, 'baddataalldata.html', locals())


#  检验规则查看
@login_required
def testrulecheck(request):
    user = request.user
    cus_list = TestRule.objects.all().order_by('-created_at')
    result = cus_list.count()
    paginator = pagedivide(request, cus_list)

    return render(request, 'testrulecheck.html', {'user': user, 'users': paginator, 'result': result})


#  检验规则删除
@login_required
def testruledel(request, re_id):
    user = request.user
    c = get_object_or_404(TestRule, id=re_id)
    rule_id = re_id
    return render(request, 'testrulede.html', locals())


#  检验规则增加
@login_required
def testruleup(request):
    user = request.user
    return render(request, 'ruleform.html', locals())


@login_required
@csrf_exempt
def ruleup(request):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        name = request.POST.get('names', )
        url = request.POST.get('urls', )
        cookie = request.POST.get('cookies', )
        isch = request.POST.get('ischecked', )
        result = TestRule.objects.filter(name=name)
        if len(result) > 0:
            ret['error'] = '该条规则已存在'
        elif url == '' and cookie == '':
            ret['error'] = '配置错误'
        else:
            TestRule.objects.create(name=name, url=url, cookie=cookie)
            ret['status'] = 1002
            if isch == 'true':
                a = TestSet.objects.all().order_by('-created_at')[0]
                a.lastid = 0
                a.save()
                main_handle()
            else:
                pass
        return HttpResponse(json.dumps(ret))


@login_required
@csrf_exempt
def ruledel(request, rule_id, c_id):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        is1 = request.POST.get('is1', )
        is2 = request.POST.get('is2', )
        result = get_object_or_404(TestRule, id=c_id)
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


#  检验来源设置
@login_required
def test_source(request):
    user = request.user
    try:
        dbinfo = TestSet.objects.all()[0]
    except:
        dbinfo = []
    return render(request, 'testsource.html', locals())


#  检验来源表单
@login_required
def sourceset(request):
    user = request.user
    try:
        dbinfo = TestSet.objects.all()[0]
    except:
        dbinfo = []
    return render(request, 'sourceform.html', locals())



#  检验速度表单
@login_required()
def speedset(request):
    user = request.user
    try:
        db = TestSet.objects.all()[0]
        speed = db.speed
    except:
        speed = 0
    return render(request, 'speedsets.html', locals())


#  检验速度设置提交表单处理
@login_required
@csrf_exempt
def speedposthandle(request):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        spe = request.POST.get('speed', )
        try:
            speed = int(spe)
            if speed <= 0:
                ret['error'] = '速度不能小于0，请重新输入'
            else:
                speedresult = TestSet.objects.all()[0]
                if speed == speedresult.speed:
                    ret['error'] = '重复设置，请重新处理'
                else:
                    speedresult.speed = speed
                    speedresult.save()
                    ret['status'] = 1002
        except:
            ret['error'] = '请重新输入'
        return HttpResponse(json.dumps(ret))


#  检验来源表单验证
@login_required
@csrf_exempt
def infoset(request):
    if request.method == 'POST':
        ret = {'status': 1001, 'error': ''}
        ip = request.POST.get('ips', )
        port = request.POST.get('ports', )
        username = request.POST.get('usernames', )
        password = request.POST.get('passwords', )
        type = request.POST.get('types', )
        table = request.POST.get('tables', )
        ischeck = request.POST.get('ischecked', )
        try:
            conn = cx_Oracle.connect(username, password, ip + ":" + (port) + "/" + type)
            cursor = conn.cursor()
            total_q = ("select count(*) from user_tables where table_name = '{}'").format(table.upper())
            x = cursor.execute(total_q)
            resss = x.fetchone()
            totalcount = resss[0]
            if totalcount == 1:
                re = TestSet.objects.all().count()
                if re == 0:
                    print(1)
                    TestSet.objects.create(host=ip, port=port, username=username, password=password, type=type, table=table, lastid=0, speed=0)
                    print(2)
                    ret['status'] = 1002
                else:
                    result = TestSet.objects.all().order_by('-created_at')[0]
                    result.host = ip
                    result.port = port
                    result.username = username
                    result.password = password
                    result.type = type
                    result.table = table
                    if ischeck == 'true':
                        result.lastid = 0
                        result.save()
                        ret['status'] = 1002
                    else:
                        ret['status'] = 1002
                        result.save()
            else:
                ret['error'] = '配置错误，请重新配置'
            cursor.close()
            conn.close()
        except:
            ret['error'] = '配置错误，请重新配置'
        return HttpResponse(json.dumps(ret))


#  ajax获取配置信息
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
    return render(request, 'accountform.html', locals())


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
    return render(request, 'accountform.html', locals())


#  查找
@login_required
def search(request, cata):
    if request.method == 'GET':
        user = request.user
        types = request.GET.get('type')
        page = request.GET.get('page')
        sorts = request.GET.get('sort')
        catas = request.GET.get('catas')
        res = pag_get(types, page, sorts, catas)
        return render(request, 'result_dis.html', {'user': user, 'users':res['page'], 'result': res['numbers'], 'type': types, 'sort':sorts, 'cata': catas})

    if request.method == 'POST':
        user = request.user
        types = request.POST.get('myselect',)
        stuff = request.POST.get('stuff', )
        result = search_set(request, types, stuff, cata)
        if types == '1':
            if result['errors'] == '10':
                paginator = result['result']
                return render(request, 'result_dis.html', {'user': user, 'users': paginator, 'result': result['number'], 'type': types, 'sort': stuff, 'cata': cata})
            else:
                return render(request, 'result_dis.html', {'user': user, 'errors': result['errors'], 'cata': cata, 'result': 0})
        else:
            if result['errors'] == '10':
                paginator = result['result']
                result = result['number']
                return render(request, 'result_dis.html', {'user': user, 'users': paginator, 'result': result, 'type': types, 'sort': stuff, 'cata': cata})
            else:
                return render(request, 'result_dis.html', {'user': user, 'errors': result['errors'], 'cata': cata, 'result': 0})


#  月份查看
@login_required
def monthcheck(request):
    user = request.user
    a = getmonth()
    b = getmonthdata()
    c = getmonthbaddata()
    return render(request, 'monthcheck.html', locals())


#  图表数据
@csrf_exempt
def getdata(request):
    try:
        time = timehandle()
        alldata_list = datahandle()
        baddata_list = baddatahandle()
        ret = {}
        ret['time'] = time
        ret['alldata_list'] = alldata_list
        ret['baddata_list'] = baddata_list
    except:
        ret = {'time': [], 'alldata_list': [], 'baddata_list': []}
    return HttpResponse(json.dumps(ret))


#  规则搜索
@login_required
def rulesearch(request):
    if request.method == 'GET':
        user = request.user
        types = request.GET.get('type')
        page = request.GET.get('page')
        sorts = request.GET.get('sort')
        res = page_get(types, page, sorts)
        success = '10'
        return render(request, 'result_dis.html', {'user': user, 'success' :success, 'users':res['page'], 'result': res['numbers'], 'type': types, 'sort':sorts})

    if request.method == 'POST':
        user = request.user
        types = request.POST.get('myselect',)
        stuff = request.POST.get('stuff', )
        result = rulesearch_set(request, types, stuff)
        if result['errors'] == '':
            paginator = result['result']
            success = '10'
            return render(request, 'testrulecheck.html', {'user': user, 'success' :success, 'users': paginator, 'result': result['number'], 'type': types, 'sort': stuff})
        else:
            return render(request, 'testrulecheck.html', {'user': user, 'errors': result['errors'], 'result': 0})

#  测试
def testa(request):
    return render(request, 'test.html')










