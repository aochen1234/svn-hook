import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()

from testappp.models import ResultNumber, TestResult
import time
import os
import configparser

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


