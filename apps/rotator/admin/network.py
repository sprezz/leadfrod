# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import Account, Network


class AccountInline(admin.StackedInline):
    model = Account
    extra = 0


class NetworkAdmin(admin.ModelAdmin):
    model = Network
    list_display = ('name', 'single', 'url', 'status')
    actions = ['activate_single', 'set_single_false', ]
    inlines = [AccountInline]

    def activate_single(self, request, queryset):
        queryset.update(single=True)

    activate_single.short_description = "Activate single"

    def set_single_false(self, request, queryset):
        queryset.update(single=False)

    set_single_false.short_description = "Set single False"
