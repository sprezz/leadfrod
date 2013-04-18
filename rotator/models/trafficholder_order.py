# -*- coding:utf-8 -*-
from django.db import models
from rotator.models import TRAFFIC_HOLDER_STATUS_LIST, AWAITING_APPROVAL


class TrafficHolderOrder(models.Model):
    owner = models.ForeignKey('rotator.Owner', related_name='orders')
    order_id = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=36, null=True, blank=True)
    hourly_rate = models.IntegerField(blank=True, null=True)
    clicks_received = models.IntegerField(default=0)
    clicks_total = models.IntegerField(default=1000000)
    #    internal_url = models.CharField(max_length=2000)
    approval_url = models.CharField(max_length=2000, blank=True, null=True)
    status = models.CharField(max_length=30,
                              choices=TRAFFIC_HOLDER_STATUS_LIST,
                              default=AWAITING_APPROVAL)
    description = models.CharField(max_length=30, blank=True, null=True)

    def __unicode__(self):
        return '%s %s %s' % (self.order_id, self.owner.name, self.status)

    class Meta:
        app_label = 'rotator'
