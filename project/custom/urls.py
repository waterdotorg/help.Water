from django.conf.urls import patterns, url

urlpatterns = patterns('custom.views',
    url(r'^dashboard/$', 'dashboard', name='dashboard'),
    url(r'^$', 'homepage', name='homepage'),
)
