from django.conf.urls import patterns, url

urlpatterns = patterns('watch.views',
    url(r'^ajax/$', 'watch_ticket_ajax', name='watch_ticket_ajax'),
)
