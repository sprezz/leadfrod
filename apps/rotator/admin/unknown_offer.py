# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import UnknownOffer


class UnknownOfferAdmin(admin.ModelAdmin):
    model = UnknownOffer

    list_display = ('network', 'account', 'offer_num', 'date')
    list_filter = ('date', 'network',)
