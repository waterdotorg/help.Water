from django.conf.urls import patterns, url

urlpatterns = patterns('tickets.views',
    url(r'^create/$', 'ticket_create', name='ticket_create'),
)
