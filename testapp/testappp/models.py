from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
# Create your models here.

#  定义用户类
class NewUser(AbstractUser):
    profile = models.CharField('profile', default='', max_length=256)

    def __str__(self):
        return self.username


#  定义检验规则表
class TestRule(models.Model):
    name = models.CharField('名字', max_length=255)
    user = models.ForeignKey(NewUser, null=True)
    url = models.CharField('路由', max_length=255, blank=True, editable=True)
    cookie = models.CharField('Cookie', max_length=255, blank=True, editable=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '检验规则'
        verbose_name_plural = '检验规则'

    def __str__(self):
        if self.url:
            return self.url
        else:
            return self.cookie



#  定义结果表
class TestResult(models.Model):
    origin_id = models.IntegerField('原始ID')
    origin_url = models.TextField('原始路由', null=True)
    origin_cookie = models.TextField('原始Cookie', null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    is_check = models.BooleanField('是否查看', default=False)
    is_target = models.BooleanField('是否目标', default=False)
    testrule = models.ForeignKey(TestRule, null=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '检验结果'
        verbose_name_plural = '检验结果'

    def __str__(self):
        return str(self.origin_id)


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
    lastid = models.IntegerField('检测ID')
    speed = models.IntegerField('检测速度')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '检测配置'
        verbose_name_plural = '检测配置'








