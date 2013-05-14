# -*- coding:utf-8 -*-
from django.db import models


class IPSolution(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'IP Solution'
        verbose_name_plural = 'IP Solutions'
        app_label = 'rotator'
