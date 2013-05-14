# -*- coding:utf-8 -*-
from django.db import models
from rotator.models import STATUS_LIST, ACTIVE


class Owner(models.Model):
    name = models.CharField(max_length=30)
    daily_cap = models.FloatField(default=0)
    capacity = models.FloatField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_LIST, default=ACTIVE)
    description = models.CharField(max_length=30, null=True, blank=True)
    #    order_id = models.CharField(max_length = 30)

    def is_active(self):
        return self.status == ACTIVE

    class Meta:
        verbose_name = 'Owner'
        verbose_name_plural = 'Owners'
        app_label = 'rotator'

    def __unicode__(self):
        return u'%s cap: %s/%s' % (self.name, self.capacity, self.daily_cap)
