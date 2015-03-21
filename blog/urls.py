from django.conf.urls import patterns, url

from blog import views

urlpatterns = patterns('',
                       url(r'^$', views.home),
                       url(r'^(?P<pid>\d+)/(?P<slug>[-\w\d]+)$', views.home),
                       url(r'^c/(?P<slug>[-\w\d]+)$', views.home),
                       url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<y>\day+)$',
                           views.home)
)
