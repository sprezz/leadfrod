# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from rotator.models import STATUS_LIST, ACTIVE


class WorkerProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    odesk_id = models.CharField(max_length=30, null=True, blank=True)
    ip_solution = models.ForeignKey('rotator.IPSolution', null=True, blank=True)
    now_online = models.BooleanField(default=False, editable=False)
    status = models.CharField(max_length=30, choices=STATUS_LIST, default=ACTIVE)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Worker profile'
        verbose_name_plural = 'Workers profiles'
        app_label = 'rotator'

    def __unicode__(self):
        return u'%s (%s %s) @ odesk as %s' % (self.user.username,
                                              self.user.first_name,
                                              self.user.last_name, self.odesk_id)
