# -*- coding:utf-8 -*-
from django.db import models
from django.utils.timezone import now


class ManualQueue(models.Model):
    url = models.URLField(max_length=2000)
    size = models.SmallIntegerField(default=10)
    createdDate = models.DateTimeField(default=now)

    def decreaseSize(self):
        if self.size > 0:
            self.size -= 1
            self.save()

    def __unicode__(self):
        return "[{}] {}".format(self.size, self.url)

    class Meta:
        app_label = 'rotator'
