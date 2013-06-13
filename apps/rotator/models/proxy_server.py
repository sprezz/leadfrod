# -*- coding:utf-8 -*-
from django.db import models


class ProxyServer(models.Model):
    host = models.CharField(max_length=300)
    exceptions = models.IntegerField(default=0)

    def catchException(self):
        self.exceptions += 1
        self.save()

    class Meta:
        app_label = 'rotator'
