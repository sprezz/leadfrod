# -*- coding:utf-8 -*-
from django.db import models
from rotator.models import STATUS_LIST, ACTIVE


class Network(models.Model):
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=100)
    single = models.BooleanField(default=True)
    status = models.CharField(max_length=30, choices=STATUS_LIST, default=ACTIVE)
    description = models.CharField(max_length=30, null=True, blank=True)

    def is_active(self):
        return self.status == ACTIVE

    class Meta:
        verbose_name = 'Network'
        verbose_name_plural = 'Networks'
        ordering = ['name']
        app_label = 'rotator'

    def __unicode__(self):
        return u'%s' % self.name
