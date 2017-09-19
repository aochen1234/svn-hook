#-*-coding:utf-8-*-
import os,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
django.setup()

import os
import json
import time
import datetime
import cx_Oracle
import pymongo
from pymongo import MongoClient
from collections import Counter
from testappp.models import TestResult, ResultNumber, TestDomain, TestSet
from testappp.view_support import *
from testappp.templatetags.iptags import ip2loc
from testappp.templatetags.mytags import truncate_ip
import random
import os
import sys
import csv
