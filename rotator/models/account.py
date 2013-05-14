# -*- coding:utf-8 -*-
import datetime
from django.db import models
from rotator.models import PAYMENT_TYPE_LIST, STATUS_LIST, ACTIVE


class Account(models.Model):
    network = models.ForeignKey('rotator.Network', related_name='accounts')
    company = models.ForeignKey('rotator.Company', related_name='accounts')

    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30, null=True, blank=True)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    AM = models.CharField(max_length=30)
    phone = models.CharField(max_length=30, null=True, blank=True)
    AM_phone_list = models.CharField(max_length=30, null=True, blank=True)
    AM_email_list = models.CharField(max_length=30, null=True, blank=True)
    AM_IM_list = models.CharField(max_length=30, null=True, blank=True)
    recieved_check_once = models.BooleanField(default=False, blank=True)
    stats_configured = models.BooleanField(default=False, blank=True)
    payments_via = models.CharField(max_length=30, choices=PAYMENT_TYPE_LIST)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    payment_frequency = models.CharField(max_length=30, null=True, blank=True)
    daily_cap = models.FloatField(default=100)
    capacity = models.FloatField(default=100)
    status = models.CharField(max_length=30, choices=STATUS_LIST,
                              default=ACTIVE)
    description = models.CharField(max_length=255, null=True, blank=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    today_revenue = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    primary = models.BooleanField(default=True)

    def owner(self):
        return self.company.owner

    owner.short_description = "Owner"

    def is_active(self):
        return self.status == ACTIVE

    def checked(self):
        self.last_checked = datetime.datetime.now()
        self.save()

    def setRevenue(self, revenue):
        self.today_revenue = revenue
        self.save()

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['username', 'capacity']
        app_label = 'rotator'

    def __unicode__(self):
        return u'%s,%s,%s[%s/%s]' % (self.company, self.network, self.username, self.capacity, self.daily_cap)
