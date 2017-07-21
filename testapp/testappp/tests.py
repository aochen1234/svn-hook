import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from testappp.models import ResultNumber, TestResult, TestRule
import time


a = time.localtime()
num = a[0] - 2017
number = a[1] - 7
result = []
result_list = []
if num == 0:
    if number == 0:
        result.append('2017-'+ '07')
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
print(result_list)



