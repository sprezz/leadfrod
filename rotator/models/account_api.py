# -*- coding:utf-8 -*-
from django.db import models


class AccountAPI(models.Model):
    account = models.OneToOneField('rotator.Account', related_name="api")
    affiliate_id = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)

    class Meta:
        app_label = 'rotator'
