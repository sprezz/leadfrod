# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import Niche


class NicheAdmin(admin.ModelAdmin):
    model = Niche
    list_display = ('name', 'status', 'min_clicks', 'max_clicks', 'priority', )
