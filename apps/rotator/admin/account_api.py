# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import AccountAPI


class AccountAPIAdmin(admin.ModelAdmin):
    model = AccountAPI
    list_display = ('account', 'affiliate_id', 'api_key',)
