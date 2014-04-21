from django.conf.urls import patterns, url

urlpatterns = patterns('waterauth.views',
    url(r'^auth/signout/$', 'waterauth_signout', name='auth_signout'),
    url(r'^auth/signin/$', 'waterauth_signin', name='auth_signin'),
)
