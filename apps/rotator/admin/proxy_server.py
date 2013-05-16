# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import ProxyServer


class ProxyServerAdmin(admin.ModelAdmin):
    model = ProxyServer
    list_display = ('host', 'exceptions')
