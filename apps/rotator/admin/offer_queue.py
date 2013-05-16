# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import OfferQueue


class OfferQueueAdmin(admin.ModelAdmin):
    model = OfferQueue
    list_display = ('network', 'account', 'offerName', 'offerNum', 'size',)

    actions = ['add_clicks_size', 'substract_clicks_size', ]

    def add_clicks_size(self, request, queryset):
        for q in queryset:
            q.size += 5
            q.save()

    add_clicks_size.short_description = "Add 5 clicks to size"

    def substract_clicks_size(self, request, queryset):
        for q in queryset:
            if q.size < 5:
                q.size = 0
            else:
                q.size -= 5
            q.save()

    substract_clicks_size.short_description = "Substract 5 clicks from size"
