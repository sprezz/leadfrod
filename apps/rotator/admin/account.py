# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import Offer, Account, Earnings


class OfferInline(admin.TabularInline):
    model = Offer
    extra = 0


class AccountAdmin(admin.ModelAdmin):
    model = Account
    list_display = ('owner', 'network', 'username', 'last_checked', 'revenue', 'today_revenue',)
    list_display_links = ('owner', )
    list_filter = ('network',)
    inlines = [OfferInline]

    def revenue(self, account):
        return Earnings.objects.filter(offer__account=account).extra(
            select={'total': 'sum(revenue)'})[0].total

        #def today_revenue(self, account):
        #    today = datetime.date.today()
        #    return Earnings.objects.filter(offer__account=account, date__month=today.month,
        #        date__year=today.year, date__day=today.day).extra(
        #            select={'total': 'sum(revenue)'})[0].total
