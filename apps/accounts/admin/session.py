# -*- coding:utf-8 -*-
from django.contrib.admin import ModelAdmin, site

from accounts.models import UserSession


class UserSessionAdmin(ModelAdmin):
    list_display = ('user', 'datetime_login', 'datetime_last_activity', 'session_duration', 'active')
    list_filter = ('user', )
    date_hierarchy = 'datetime_login'


site.register(UserSession, UserSessionAdmin)

