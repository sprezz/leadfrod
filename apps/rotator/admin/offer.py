# -*- coding:utf-8 -*-
from django.contrib import admin


class OfferAdmin(admin.ModelAdmin):
    save_as = True

    raw_id_fields = ['advertiser', 'network', 'account', 'niche']

    list_display = ('name', 'offer_num', 'network', 'account', 'owner_name', 'capacity', 'daily_cap', 'advertiser', 'status', 'capacity_error', 'submits_today', 'submits_total')
    list_display_links = ('name', )
    search_fields = ['name', 'network__name', 'network__description', 'account__username', 'account__company__owner__name', 'advertiser__name', 'advertiser__description']
    list_filter = ('status', 'niche', 'network', 'account', )

    actions = ['add_clicks_dailycap', 'substract_clicks_dailycap', 'add_clicks_capacity', 'substract_clicks_capacity', 'activate', 'paused', 'set_submits_today', ]

    def capacity_error(self, offer):
        """
        Checks if offer have enough budget to be selected
        """
        daily_cap = offer.get_capacity_today
        if not daily_cap.checkOfferCapacity(offer.payout):
            return 'run out of offer capacity'
        if offer.hasAdvertiser() and not daily_cap.checkAdvertiserCapacity(
                offer.payout):
            return "run out of advertiser's offer capacity \
                                                    with %s" % (offer.account)
        if not daily_cap.checkAccountCapacity(offer.payout):
            return 'run out of account capacity %s' % (daily_cap.account)

        if not daily_cap.checkCompanyCapacity(offer.payout):
            return 'run out of company capacity %s' % (daily_cap.company)

        if not daily_cap.checkOwnerCapacity(offer.payout):
            return 'run out of owner capacity %s' % (daily_cap.owner)
        return "OK"

    capacity_error.allow_tags = True

    def add_clicks_dailycap(self, request, queryset):
        for q in queryset:
            q.daily_cap += 5
            q.save()

    add_clicks_dailycap.short_description = "Add 5 clicks to daily cap"

    def substract_clicks_dailycap(self, request, queryset):
        for q in queryset:
            if q.daily_cap < 5:
                q.daily_cap = 0
            else:
                q.daily_cap -= 5
            q.save()

    substract_clicks_dailycap.short_description = "Substract 5 clicks from daily cap"

    def add_clicks_capacity(self, request, queryset):
        for q in queryset:
            q.capacity += 5
            q.save()

    add_clicks_capacity.short_description = "Add 5 clicks to capacity"

    def substract_clicks_capacity(self, request, queryset):
        for q in queryset:
            if q.capacity < 5:
                q.capacity = 0
            else:
                q.capacity -= 5
            q.save()

    substract_clicks_capacity.short_description = "Substract 5 clicks from capacity"

    def activate(self, request, queryset):
        queryset.update(status='active')

    activate.short_description = "Set active"

    def paused(self, request, queryset):
        queryset.update(status='paused')

    paused.short_description = "Set paused"

    def set_submits_today(self, request, queryset):
        queryset.update(submits_today=1)

    set_submits_today.short_description = "Set submits_today to 1"
