from django.contrib import admin
from .models import TestResult, NewUser, ResultNumber, TestSet, TestDomain
# Register your models here.

#  匹配规则排列
@admin.register(TestDomain)
class TestruleAdmin(admin.ModelAdmin):
    list_display = ('name', 'content', 'created_at', 'updated_at',)
    list_display_links = ('name',)
    list_per_page = 50
    ordering = ['-created_at']
    search_fields = ['name', 'content']
    exclude = ('created_at', 'updated_at',)



#  匹配结果排列
@admin.register(TestResult)
class TestresultAdmin(admin.ModelAdmin):
    list_display = ('host', 'is_check', 'is_target', 'created_at', 'updated_at',)
    list_display_links = ('host',)
    list_per_page = 50
    ordering = ['-created_at']
    search_fields = ['host', 'is_target', 'is_check']
    exclude = ('created_at', 'updated_at', )


#  匹配数量排列
@admin.register(ResultNumber)
class ResultnumberAdmin(admin.ModelAdmin):
    list_display = ('all_data', 'wait_check_data', 'created_at', 'updated_at',)
    list_display_links = ('all_data',)
    list_per_page = 50
    ordering = ['-created_at']


@admin.register(TestSet)
class TessetAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'username', 'password', 'type', 'table', 'lastid', 'starttime')
    list_display_links = ('host',)
    list_per_page = 50
    ordering = ['-created_at']
    search_fields = ['host', 'port', 'username']
    exclude = ('created_at',)



admin.site.register(NewUser)
admin.site.site_header = '鉴影系统'
