from django.contrib import admin
from .models import TestResult, TestRule, NewUser, ResultNumber, TagetResult
# Register your models here.

#  匹配规则排列
@admin.register(TestRule)
class TestruleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'cookie', 'created_at', 'updated_at',)
    list_display_links = ('name',)
    list_per_page = 50
    ordering = ['-created_at']
    search_fields = ['name', 'url', 'cookie']
    exclude = ('created_at', 'updated_at',)
    prepopulated_fields = {'slug': ('name',)}


#  匹配结果排列
@admin.register(TestResult)
class TestresultAdmin(admin.ModelAdmin):
    list_display = ('origin_id', 'origin_url', 'origin_cookie', 'created_at',)
    list_display_links = ('origin_id',)
    list_per_page = 50
    ordering = ['-created_at']
    search_fields = ['origin_id', 'origin_url', 'origin_cookie']
    exclude = ('created_at', )


#  匹配数量排列
@admin.register(ResultNumber)
class ResultnumberAdmin(admin.ModelAdmin):
    list_display = ('all_data', 'wait_check_data', 'created_at', 'updated_at',)
    list_display_links = ('all_data',)
    list_per_page = 50
    ordering = ['-created_at']


@admin.register(TagetResult)
class TargetresultAdmin(admin.ModelAdmin):
    list_display = ('origin_id', 'origin_url', 'origin_cookie', 'created_at', 'is_check',)
    list_display_links = ('origin_id',)
    list_per_page = 50
    ordering = ['-created_at']
    search_fields = ['origin_id', 'origin_url', 'origin_cookie']
    exclude = ('created_at', )



admin.site.register(NewUser)
admin.site.site_header = 'webshell检测'
