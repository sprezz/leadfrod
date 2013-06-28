# -*- coding:utf-8 -*-
from django.db import models
from rotator.models import STATUS_LIST, ACTIVE


class Niche(models.Model):
    name = models.CharField(max_length=30)
    min_clicks = models.FloatField(null=True, blank=True)
    max_clicks = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_LIST, default=ACTIVE)
    description = models.CharField(max_length=30, null=True, blank=True)
    priority = models.IntegerField(default=10)
    url = models.URLField(default="http://cpagodfather.com/autoinsurance/pagea.php")
    
    class Meta:
        ordering = ['name']
        app_label = 'rotator'

    def is_active(self):
        return self.status == ACTIVE

    def __unicode__(self):
        return u'%s' % self.name
