# -*- coding:utf-8 -*-
from django.db import models

from locking import models as locking
from rotator.models import STATUS_LIST, ACTIVE


class Lead(locking.LockableModel):
    csv = models.ForeignKey('rotator.CSVFile', related_name='leads')
    worker = models.ForeignKey('auth.User', null=True, blank=True, related_name='leads_in_work')
    advertisers = models.ManyToManyField('rotator.Advertiser', related_name='leads', null=True, blank=True)

    started_on = models.DateTimeField(null=True, blank=True)
    ended_on = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)  # Should be accessible after?
    offers_requested = models.ManyToManyField('rotator.Offer', related_name='proposed_leads', null=True, blank=True)
    offers_completed = models.ManyToManyField('rotator.Offer', related_name='completed_leads', null=True, blank=True)

    lead_data = models.TextField()
    ip_address = models.CharField(max_length=30, null=True, blank=True)
    user_agent = models.CharField(max_length=100, null=True, blank=True)
    subid = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_LIST, null=True, blank=True)
    description = models.CharField(max_length=30, null=True, blank=True)

    def is_active(self):
        return self.status == ACTIVE

    def checkAdvertiser(self, anAdvertiser):
        return anAdvertiser in self.advertisers.all()

    def getNiche(self):
        return self.csv.niche

    def __unicode__(self):
        _str = u'%s %s' % (self.csv, self.status)
        if self.worker:
            _str += u' in work %s' % self.worker
        return _str

    class Meta:
        app_label = 'rotator'
