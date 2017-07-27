from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'accountset/formpost$', views.accountset, name='accountset'),
    url(r'accountset/$', views.accountform, name='accountform'),
    url(r'testrule/(?P<rule_id>\d+)/setting/(?P<c_id>\d+)/delete/$', views.ruledel, name='ruledel'),
    url(r'logout/$', views.log_out, name='log_out'),
    url(r'result/(?P<cata>\w*)/searchact/$', views.search, name='search_action'),
    url(r'result/$', views.result_dis, name='result_dis'),
    url(r'speed/$', views.speedset, name='speed'),
    url(r'source/information/inforget/$', views.infoget, name='info_get'),
    url(r'source/information/setting/$', views.infoset, name='info_set'),
    url(r'speed/speedset/$', views.speedposthandle, name='speedset'),
    url(r'source/$', views.test_source, name='test_source'),
    url(r'source/information/$', views.sourceset, name='source_set'),
    url(r'baddata/$', views.baddatacheck, name='baddatacheck'),
    url(r'waitdata/$', views.waitdata, name='wait_data'),
    url(r'waitdata/(?P<re_id>\d+)/check/$', views.alldata, name='all_data'),
    url(r'testrule/(?P<re_id>\d+)/setting/$', views.testruledel, name='testruledel'),
    url(r'testrule/rulesearch$', views.rulesearch, name='rulesearch'),
    url(r'testrule/$', views.testrulecheck, name='testrule'),
    url(r'testrule/testruleup/ruleup/$', views.ruleup, name='testrule_up'),
    url(r'testrule/testruleup/$', views.testruleup, name='testruleup'),
    url(r'month/$', views.monthcheck, name='month'),
    url(r'getdata/$', views.getdata, name='getdata'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)