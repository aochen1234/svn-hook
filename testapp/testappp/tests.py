import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from testappp.models import ResultNumber, TestResult, TestRule
import time
result = []
res = {'name': '', 'url': '', 'cookie': ''}
a = TestRule.objects.all()
b = a.count()
c1 = []
c2 = []
c3 = []
for i in a:
    c1.append(i.name)
    c2.append(i.url)
    c3.append(i.cookie)
print(c3)





