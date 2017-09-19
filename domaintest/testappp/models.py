from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
# Create your models here.

#  定义用户类
class NewUser(AbstractUser):
    profile = models.CharField('profile', default='', max_length=256)

    def __str__(self):
        return self.username


#  定义检验规则表
class TestDomain(models.Model):
    rule_type = (
        ('webshell', '后门检测'),
        ('domain', '域名检测'),
    )
    name = models.CharField('名字', max_length=255)
    content = models.CharField('内容', max_length=255, blank=True, editable=True)
    ruletype = models.CharField('规则类型', max_length=255, choices=rule_type)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '检验规则'
        verbose_name_plural = '检验规则'

    def __str__(self):
        return self.name


#  定义结果表
class TestResult(models.Model):
    record_id = models.CharField('事件id', null=True, max_length=255)
    proplist_id = models.CharField('具体id', null=True, max_length=255)
    host = models.TextField('原始域名', null=True)
    sip = models.TextField('原始ip', null=True)
    sloc = models.TextField('原始地址', null=True)
    request_header = models.TextField('原始请求头', max_length=4000, blank=True, null=True)
    pattition_time = models.DateTimeField('记录时间', null=True)
    origin_url = models.TextField('原始url', max_length=2000, blank=True, null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    is_check = models.BooleanField('是否查看', default=False)
    is_target = models.BooleanField('是否目标', default=False)
    testdomain= models.ForeignKey(TestDomain, null=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '检测结果'
        verbose_name_plural = '检测结果'

    def __str__(self):
        return self.host

    def get_ip(self):
        try:
            num = int(self.sip)
            s = []
            for i in range(4):
                s.append(str(int(num % 256)))
                num /= 256
            return '.'.join(s[::-1])
        except:
            pass


#  结果数量
class ResultNumber(models.Model):
    all_data = models.IntegerField('累计数量', default=0)
    wait_check_data = models.IntegerField('待检测数量', default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '结果数量'
        verbose_name_plural = '结果数量'


class TestSet(models.Model):
    host = models.CharField('IP', max_length=255)
    port = models.CharField('端口', max_length=255)
    username = models.CharField('用户名', max_length=255)
    password = models.CharField('密码', max_length=255)
    type = models.CharField('数据库', max_length=255, help_text='只支持Oracle数据库')
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    table = models.CharField('数据表', max_length=255, help_text='Oracle下的数据表')
    starttime = models.DateTimeField('检测起始时间', null=True)
    lastid = models.CharField('检测ID', max_length=255)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '检测配置'
        verbose_name_plural = '检测配置'








