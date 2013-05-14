# -*- coding:utf-8 -*-
from django.db import models


class AdvertiserAccountCapacity(models.Model):
    advertiser = models.ForeignKey('rotator.Advertiser', related_name='account_capacity')
    account = models.ForeignKey('rotator.Account', related_name='advertiser_capacity')
    capacity = models.FloatField(default=25)

    class Meta:
        verbose_name = "Advertiser's Account Capacity"
        verbose_name_plural = "Advertiser's Account Capacity instances"
        app_label = 'rotator'

    def __unicode__(self):
        return u'%s/%s' % (self.advertiser, self.account)
