# -*- coding:utf-8 -*-
from django.db import models
from rotator.models import STATUS_LIST, ACTIVE


class Advertiser(models.Model):
    name = models.CharField(max_length=30)
    daily_cap = models.FloatField(default=25)
    status = models.CharField(max_length=30, choices=STATUS_LIST)
    description = models.CharField(max_length=255, null=True, blank=True)

    def is_active(self):
        return self.status == ACTIVE

    def numberOfAccounts(self):
        return self.account_capacity.count()

    numberOfAccounts.short_description = u"Account qty"

    def clearCapacityOfAllAccounts(self):
        self.account_capacity.all().update(capacity=self.daily_cap)

    def getAccountCapacity(self, adv_account):
        from rotator.models.advertiser_account_capacity import AdvertiserAccountCapacity
        if AdvertiserAccountCapacity.objects.filter(advertiser=self, account=adv_account).exists():
            return self.account_capacity.get(account=adv_account)
        return None

    @property
    def getAccounts(self):
        return self.account_capacity.all()

    class Meta:
        verbose_name = 'Advertiser'
        verbose_name_plural = 'Advertisers'
        ordering = ['name']
        app_label = 'rotator'

    def __unicode__(self):
        return u'%s' % self.name
