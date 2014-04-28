from django.conf.urls import patterns, url

urlpatterns = patterns('tickets.views',
    url(r'^create/$', 'ticket_create', name='ticket_create'),
    url(r'^detail/(?P<pk>\d+)/$', 'ticket_detail', name='ticket_detail'),
    url(r'^edit/(?P<pk>\d+)/$', 'ticket_edit', name='ticket_edit'),
    url(r'^$', 'tickets', name='tickets'),
)
