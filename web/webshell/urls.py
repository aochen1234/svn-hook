from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'logout/$', views.log_out, name='log_out'),
    url(r'result/$', views.result_dis, name='result_dis'),
    url(r'source/$', views.test_source, name='test_source'),
]