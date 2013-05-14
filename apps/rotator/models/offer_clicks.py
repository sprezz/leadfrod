# -*- coding:utf-8 -*-
from django.db import models


class OfferClicks(models.Model):
    offer_id = models.ForeignKey('rotator.Offer')
    clicks_remaining = models.IntegerField(null=True)
    last_click_date_time = models.DateTimeField(null=True)
    priority = models.IntegerField(default=1)

    class Meta:
        app_label = 'rotator'
