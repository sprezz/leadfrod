# -*- coding:utf-8 -*-
from django.db import models
from rotator.models import STATUS_LIST, ACTIVE


class Company(models.Model):
    owner = models.ForeignKey('rotator.Owner', related_name='companies')
    name_list = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    county = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    w9_file = models.CharField(max_length=100, null=True, blank=True)
    im_list = models.CharField(max_length=100, null=True, blank=True)
    email_list = models.CharField(max_length=100, null=True, blank=True)
    phone_list = models.CharField(max_length=100, null=True, blank=True)
    daily_cap = models.FloatField(default=0)
    capacity = models.FloatField(default=0)
    websites = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_LIST,
                              default=ACTIVE)
    description = models.CharField(max_length=255, null=True, blank=True)

    def is_active(self):
        return self.status == ACTIVE

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        app_label = 'rotator'

    def __unicode__(self):
        return u'%s (owned by %s) cap: %s/%s' % (self.name_list, self.owner, self.capacity, self.daily_cap)
