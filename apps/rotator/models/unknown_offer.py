# -*- coding:utf-8 -*-
from django.db import models
from django.utils.timezone import now


class UnknownOffer(models.Model):
    offer_num = models.CharField(max_length=10, null=True, blank=True)
    network = models.ForeignKey('rotator.Network')
    account = models.ForeignKey('rotator.Account')
    date = models.DateTimeField(default=now)

    def __unicode__(self):
        return "%s / %s / %s" % (self.offer_num, self.account.username,
                                 self.network.name)

    class Meta:
        app_label = 'rotator'
