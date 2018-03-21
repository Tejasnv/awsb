from django.conf.urls import url, include
from . import views

urlpatterns = [ 
    url(r'^$', views.index, name = 'index'),
    url(r'^update/$', views.update, name='update'),
    url(r'^getday/$', views.getday, name='getday'),
#    url(r'^populate/$', views.populate, name='populate'),


    url(r'^daily/$', views.daily, name='daily'),
    url(r'^weekly/$', views.weekly, name='daily'),
    url(r'^monthly/$', views.monthly, name='daily'),
];
