# -*- coding:utf-8 -*-
from django.db import models
from rotator.models import STATUS_LIST, ACTIVE


class LeadSource(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=STATUS_LIST, default=ACTIVE)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Lead Source'
        verbose_name_plural = 'Lead Sources'
        app_label = 'rotator'

    def __unicode__(self):
        return u'%s' % self.name
