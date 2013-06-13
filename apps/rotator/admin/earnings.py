# -*- coding:utf-8 -*-
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from rotator.models import Earnings


class EarningChangeList(ChangeList):
    def get_summary(self):
        queryset_count = self.get_query_set().select_related()
        model_admin = self.model_admin
        list_summary_values = [0] * len(model_admin.list_display)
        for earning in queryset_count.all():
            for field in model_admin.list_summary:
                attr = getattr(model_admin, field, 0)
                if attr:
                    attr = attr(earning)
                else:
                    attr = getattr(earning, field, 0)
                    attr = attr() if callable(attr) else attr

                attr = float(attr)

                index = model_admin.list_display.index(field)
                list_summary_values[index] += attr
        return list_summary_values


class EarningsAdmin(admin.ModelAdmin):
    model = Earnings

    chlen = "qwert"

    list_display = ('network', 'account', 'offer_name', 'offer_num', 'date',
                    'campaign', 'payout', 'clicks', 'pps', 'mpps', 'revenue',
                    'submits_today', 'conv')
    list_filter = ('date', 'niche', 'status', 'network',)

    list_summary = ['pps', 'submits_today', 'revenue', 'clicks']

    actions = ['add_clicks_dailycap', 'substract_clicks_dailycap',
               'add_clicks_capacity', 'substract_clicks_capacity',
               'activate', 'paused', ]

    def activate(self, request, queryset):
        for q in queryset:
            q.offer.status = 'active'
            q.offer.save()
        queryset.update(status='active')

    activate.short_description = "Set active"

    def paused(self, request, queryset):
        for q in queryset:
            q.offer.status = 'paused'
            q.offer.save()

    paused.short_description = "Set paused"

    def add_clicks_dailycap(self, request, queryset):
        for q in queryset:
            q.offer.daily_cap += 5
            q.offer.save()

    add_clicks_dailycap.short_description = "Add 5 clicks to daily cap"

    def substract_clicks_dailycap(self, request, queryset):
        for q in queryset:
            if q.offer.daily_cap < 5:
                q.offer.daily_cap = 0
            else:
                q.offer.daily_cap -= 5
            q.offer.save()

    substract_clicks_dailycap.short_description = "Substract 5 clicks from daily cap"

    def add_clicks_capacity(self, request, queryset):
        for q in queryset:
            q.offer.capacity += 5
            q.offer.save()

    add_clicks_capacity.short_description = "Add 5 clicks to capacity"

    def substract_clicks_capacity(self, request, queryset):
        for q in queryset:
            if q.offer.capacity < 5:
                q.offer.capacity = 0
            else:
                q.offer.capacity -= 5
            q.save()

    substract_clicks_capacity.short_description = "Substract 5 clicks from capacity"

    class Media:
        css = {
            "all": ("css/admin_earnings.css",),
        }

    def submits_today(self, earning):
        return earning.offer.submits_today

    def pps(self, earning):
        return earning.pps()

    pps.admin_order_field = 'admin_pps'

    def conv(self, earning):
        result = earning.conv()
        if float(result) >= 0.3:
            result = '<span style="color:red">' + result + '</b>'
        return result

    conv.admin_order_field = 'admin_conv'
    conv.allow_tags = True

    def mpps(self, earning):
        result = earning.mpps()
        if float(result) <= 0.3:
            result = '<span style="color:red">' + result + '</b>'
        return result

    mpps.admin_order_field = 'admin_mpps'
    mpps.allow_tags = True

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return EarningChangeList

    def queryset(self, request):
        queryset = super(EarningsAdmin, self).queryset(request)
        queryset = queryset.select_related()
        queryset = queryset.extra(select={
            'admin_pps': "revenue / rotator_offer.submits_today",
            'admin_mpps': "(revenue + rotator_earnings.payout) / \
                                            (rotator_offer.submits_today + 1)",
            'admin_conv': "(revenue / rotator_earnings.payout) / clicks",
        })

        return queryset

    def __call__(self, *args, **kwargs):
        if args or kwargs:
            return super(EarningsAdmin, self).__call__(*args, **kwargs)
        return self
