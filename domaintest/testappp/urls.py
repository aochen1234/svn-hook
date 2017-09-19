from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    #  首页路由
    url(r'^$', views.index, name='index'),
    url(r'logout/$', views.log_out, name='log_out'),
    #  密码设置路由
    url(r'accountset/formpost$', views.accountset, name='accountset'),
    url(r'accountset/$', views.accountform, name='accountform'),

    #  检验结果路由
    url(r'result/(?P<cata>\w*)/searchact/$', views.search, name='search_action'),
    url(r'result/searchresult/$', views.full_search, name='full_search'),       #  全文检索路由
    url(r'result/$', views.result_dis, name='result_dis'),
    url(r'result/changestatus/$', views.changestatus, name='changestatus'),
    url(r'baddata/$', views.baddatacheck, name='baddatacheck'),
    url(r'waitdata/$', views.waitdata, name='wait_data'),
    url(r'waitdata/(?P<re_id>\d+)/check/$', views.alldata, name='all_data'),
    url(r'waitdata/(?P<re_id>\d+)/checkall/$', views.checkalldata, name='check_all_data'),
    url(r'waitdata/(?P<re_id>\d+)/checkall/name$', views.gettestrule, name='gettestrule'),
    url(r'month/$', views.monthcheck, name='month'),
    url(r'getdata/$', views.getdata, name='getdata'),
    url(r'getalldata/$', views.getalldata, name='getalldata'),
    url(r'getmonthdata/$', views.getmonthalldata, name='getmonthdata'),
    url(r'getba/$', views.getba, name='getba'),
    url(r'result/getheader/$', views.getheader, name='getheader'),

    #  来源设置路由
    url(r'source/inforget/$', views.infoget, name='info_get'),
    url(r'source/setting/$', views.infoset, name='info_set'),
    url(r'source/$', views.sourceset, name='source_set'),

    #  规则设置路由
    url(r'testrule/(?P<rule_id>\d+)/setting/(?P<c_id>\d+)/delete/$', views.ruledel, name='ruledel'),
    url(r'testrule/(?P<re_id>\d+)/setting/$', views.testruledel, name='testruledel'),
    url(r'testrule/(?P<re_id>\d+)/change/$', views.testrulechange, name='testrulecha'),
    url(r'testrule/(?P<re_id>\d+)/change/rulechange$', views.rulechange, name='rulechange'),
    url(r'testrule/(?P<re_id>\d+)/change/getinfo$', views.getruleinfo, name='getruleinfo'),
    url(r'testrule/rulesearch/$', views.rulesearch, name='rulesearch'),
    url(r'testrule/$', views.testrulecheck, name='testrule'),
    url(r'testrule/(?P<re_id>\d+)/domain/$', views.domaincheck, name='domain'),
    url(r'testrule/testruleup/ruleup/$', views.ruleup, name='testrule_up'),
    url(r'testrule/testruleup/$', views.testruleup, name='testruleup'),

    #  批数设置路由
    url(r'speed/$', views.speedset, name='speed'),
    url(r'speed/speedset/$', views.speedposthandle, name='speedset'),

    #  数据导出路由
    # url(r'resexport/$', views.resexport, name='resexport'),
    # url(r'resexport/respost$', views.respost, name='respost'),

    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)