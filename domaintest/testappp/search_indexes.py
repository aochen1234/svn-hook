import datetime
from haystack import indexes
from testappp.models import TestResult, TestDomain


class TestResultIndex(indexes.SearchIndex, indexes.Indexable):  # 类名必须为需要检索的Model_name+Index，这里需要检索Note，所以创建NoteIndex
    text = indexes.CharField(document=True, use_template=True)  # 创建一个text字段

    host = indexes.CharField(model_attr='host', null=True)  # 创建一个author字段

    created_at = indexes.DateTimeField(model_attr='created_at', null=True)  # 创建一个pub_date字段host = indexes.CharField(model_attr='host')  # 创建一个author字段

    sip = indexes.CharField(model_attr='get_ip', null=True)  # 创建一个pub_date字段host = indexes.CharField(model_attr='host')  # 创建一个author字段

    sloc = indexes.CharField(model_attr='sloc', null=True)  # 创建一个pub_date字段host = indexes.CharField(model_attr='host')  # 创建一个author字段

    request_header = indexes.CharField(model_attr='request_header', null=True)  # 创建一个pub_date字段host = indexes.CharField(model_attr='host')  # 创建一个author字段

    pattition_time = indexes.DateTimeField(model_attr='pattition_time', null=True)  # 创建一个pub_date字段host = indexes.CharField(model_attr='host')  # 创建一个author字段

    origin_url = indexes.CharField(model_attr='origin_url', null=True)  # 创建一个pub_date字段host = indexes.CharField(model_attr='host')  # 创建一个author字段


    def get_model(self):  # 重载get_model方法，必须要有！
        return TestResult

    def index_queryset(self, using=None):  # 重载index_..函数
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all().order_by('-created_at')



class TestDomainIndex(indexes.SearchIndex, indexes.Indexable):  # 类名必须为需要检索的Model_name+Index，这里需要检索Note，所以创建NoteIndex
    text = indexes.CharField(document=True, use_template=True)  # 创建一个text字段

    name = indexes.CharField(model_attr='name', null=True)  # 创建一个author字段

    content = indexes.CharField(model_attr='content', null=True)# 创建一个pub_date字段
    ruletype = indexes.CharField(model_attr='ruletype', null=True)# 创建一个pub_date字段

    created_at = indexes.DateTimeField(model_attr='created_at')

    def get_model(self):  # 重载get_model方法，必须要有！
        return TestDomain

    def index_queryset(self, using=None):  # 重载index_..函数
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all().order_by('-created_at')