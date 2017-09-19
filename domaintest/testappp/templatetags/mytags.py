from django import template
from django.shortcuts import get_object_or_404
from testappp.models import TestResult
import re
import json
import os

register = template.Library()

@register.filter
def truncate_ip(value):
    try:
        num = int(value)
        s = []
        for i in range(4):
            s.append(str(int(num % 256)))
            num /= 256
        return '.'.join(s[::-1])
    except:
        pass



@register.filter
def idhandle(li):
    a = li.split('.')[2]
    return a



#  更换国旗
@register.filter
def changepage(li):
    h = ''
    try:
        if '省' in li or '市' in li:
            h = '中国'
        elif li == '北美地区':
            h = '美国'
        else:
            h = li
    except:
        pass
    a = os.getcwd()
    f = open(a + '/testappp/templatetags/country.json', encoding='utf-8')
    country = json.load(f)
    b = ''
    for i in country['countrys']:
        if h == i['Name_zh']:
            b = i['Flag']
        else:
            pass
    return b


#  获取规则匹配的域名数量
@register.filter
def getdomainnum(li):
    a = TestResult.objects.filter(is_target=True, testdomain__id=li)
    return a.count()


@register.filter
def checktarget(li):
    a = li.split('.')
    if a[1] != 'testresult':
        return False
    else:
        b = TestResult.objects.filter(id=int(a[2]), is_target=True)
        if b.count() == 0:
            return False
        else:
            return True


@register.filter
def getruletype(li):
    a = li.split('.')
    b = TestResult.objects.get(id=int(a[2]), is_target=True)
    return b.testdomain.ruletype

@register.filter
def getrulecontent(li):
    a = li.split('.')
    b = TestResult.objects.get(id=int(a[2]), is_target=True)
    return b.testdomain.content

@register.filter
def gettype(li):
    a = li.split('.')
    if a[1] == 'testresult':
        return True
    else:
        return False


