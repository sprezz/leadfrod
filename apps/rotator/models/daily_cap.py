# -*- coding:utf-8 -*-
from django.db import models


class DailyCap(models.Model):
    offer = models.ForeignKey('rotator.Offer')
    submits = models.IntegerField(default=0)
    lead_list = models.CharField(max_length=30)
    worker_list = models.CharField(max_length=30)

    class Meta:
        app_label = 'rotator'
