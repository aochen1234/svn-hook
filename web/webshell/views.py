from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import NewUser, ResultNumber, TestResult, TestRule, TagetResult
from .view_support import alldataorderbymonth, baddataorderbtmonth, waitcheckdata, waitcheckdatatime, resultdisplay
import json
import time

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
global target_id
@login_required
def index(request):
    user = request.user
    all_data = alldataorderbymonth()
    bad_data = baddataorderbtmonth()
    wait_check_data = waitcheckdata()
    wait_time = waitcheckdatatime()
    target_id = []
    target_list = TagetResult.objects.all().order_by('-created_at')
    for i in target_list:
        target_id.append(i.origin_id)
    target_num = len(target_list)
    target_last = target_list[0]
    result_list = resultdisplay(4)
    return render(request, 'index.html', locals())


#  检验结果查看
@login_required
def result_dis(request):
    user = request.user
    result_list = resultdisplay(10)
    global target_id
    return render(request, 'result_dis.html', locals())


#  检验来源设置
@login_required
def test_source(request):

    return render(request, 'source.html', locals())








