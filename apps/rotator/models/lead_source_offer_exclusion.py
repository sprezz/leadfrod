# -*- coding:utf-8 -*-
from django.db import models
from rotator.models import STATUS_LIST, ACTIVE


class LeadSourceOfferExclusion(models.Model):
    leadsource = models.ForeignKey('rotator.LeadSource')
    advertiser = models.ForeignKey('rotator.Advertiser')
    status = models.CharField(max_length=30, choices=STATUS_LIST, default=ACTIVE)
    description = models.CharField(max_length=30, null=True)

    class Meta:
        app_label = 'rotator'
