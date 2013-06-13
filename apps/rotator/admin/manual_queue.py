# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import ManualQueue


class ManualQueueAdmin(admin.ModelAdmin):
    model = ManualQueue
    list_display = ('url', 'size', 'createdDate')
