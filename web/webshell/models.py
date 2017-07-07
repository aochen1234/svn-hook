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
    user = models.ForeignKey(NewUser)
    slug = models.SlugField("Slug", max_length=50, unique=True, help_text='根据name生成的，用于生成页面URL，必须唯一')
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

    def get_absolute_url(self):
        return reverse('webshell_testrule', args=(self.slug,))


#  定义结果表
class TestResult(models.Model):
    origin_id = models.IntegerField('原始ID')
    origin_url = models.TextField('原始路由', null=True)
    origin_cookie = models.TextField('原始Cookie', null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

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


class TagetResult(models.Model):
    origin_id = models.IntegerField('原始ID')
    origin_url = models.TextField('原始路由', null=True)
    origin_cookie = models.TextField('原始Cookie', null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    is_check = models.BooleanField('是否查看', default=False)
    testrule = models.ForeignKey(TestRule)

    class Meta:
        db_table = 'webshell_testresult'
        ordering = ['-created_at']
        verbose_name = '命中结果'
        verbose_name_plural = '命中结果'

    def __str__(self):
        return str(self.origin_id)



