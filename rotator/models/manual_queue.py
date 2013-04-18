# -*- coding:utf-8 -*-
import datetime
from django.db import models


class ManualQueue(models.Model):
    url = models.URLField(max_length=2000, verify_exists=False)
    size = models.SmallIntegerField(default=10)
    createdDate = models.DateTimeField(default=datetime.datetime.now())

    def decreaseSize(self):
        if self.size > 0:
            self.size -= 1
            self.save()

    def __unicode__(self):
        return "[%s] %s" % (self.size, self.url)

    class Meta:
        app_label = 'rotator'
