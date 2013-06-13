# -*- coding:utf-8 -*-
from django.conf.urls import url, patterns
from accounts.views.active_sessions import active_sessions
from accounts.views.active_sessions_ajax import active_sessions_ajax
from accounts.views.ping import ping


urlpatterns = patterns('',
                       url(r'ping/$', ping, name='ping'),
                       url(r'active_sessions/$', active_sessions, name='active_sessions'),
                       url(r'active_sessions/ajax/$', active_sessions_ajax, name='active_sessions_ajax'),
                       )
