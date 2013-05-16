# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import AdvertiserAccountCapacity


class AdvertiserAccountCapacityInline(admin.TabularInline):
    model = AdvertiserAccountCapacity
    extra = 0


class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('name', 'daily_cap', 'status', 'numberOfAccounts' )
    list_display_links = ('name', 'daily_cap', 'status' )
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': ['name', 'daily_cap', 'status']}),
        # ('Offer information', {'fields': ['offers'], 'classes': ['collapse']}),
    ]
    inlines = [AdvertiserAccountCapacityInline]
