# -*- coding:utf-8 -*-
import csv
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Q
from django.utils.timezone import now
import os
from locking.managers import point_of_timeout
from rotator.models import STATUS_LIST, ACTIVE
from django.conf import settings


class CSVFile(models.Model):
    lead_source = models.ForeignKey('rotator.LeadSource')
    niche = models.ForeignKey('rotator.Niche')
    filename = models.CharField(max_length=255, null=True, blank=True, unique=True)
    filesize = models.IntegerField(default=0)
    date_time = models.DateTimeField(default=now)
    uploaded_by = models.CharField(max_length=30)
    cost = models.FloatField(default=0)
    workers = models.ManyToManyField(User, null=True, blank=True,
                                     related_name='assignments')
    max_offers = models.FloatField(default=1)
    csv_headers = models.TextField(null=False, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_LIST,
                              default=ACTIVE)
    description = models.CharField(max_length=255, null=True, blank=True)
    csv_files = models.FileField(upload_to=settings.LEAD_FILE_DIR,
                                 help_text='Make sure your CSV file has Excel format\
                             (fields are separated with a <tt>comma</tt>)')
    has_header = models.BooleanField(default=True,
                                     help_text='Whether uploading file has the first\
                                         row as a header')

    class Meta:
        verbose_name = 'CSV File'
        verbose_name_plural = 'CSV Files'
        app_label = 'rotator'

    @property
    def leads_count(self):
        return self.leads.count()

    def create_leads_from_file(self):
        """If there is an uploaded file but there is no leads it process them"""
        if not self.has_leads() and (self.csv_files and self.csv_files.name):

            csv_full_path = os.path.join(settings.MEDIA_ROOT, self.csv_files.name)
            with open(csv_full_path, 'rb') as csvFile:
                rows = csv.reader(csvFile)
                for idx, row in enumerate(rows):
                    if not row[0]:
                        continue
                    if idx == 0 and self.has_header:
                        self.csv_headers = ','.join(row)
                        continue
                    from rotator.models.lead import Lead
                    Lead.objects.create(csv=self, status=ACTIVE, lead_data=','.join(row))

    def has_leads(self):
        return self.leads_count > 0

    def locked_leads(self):
        timeout = point_of_timeout()
        return self.leads.filter(_locked_at__gt=timeout, _locked_at__isnull=False)

    def unlocked_leads(self):
        timeout = point_of_timeout()
        return self.leads.filter(Q(_locked_at__lte=timeout) | Q(_locked_at__isnull=True))

    def is_active(self):
        return self.status == ACTIVE

    def get_revenue(self):  # todo: unused
        return self.leads.aggregate(Sum('offers_completed__payout'))['offers_completed__payout__sum']

    def getPercentOfCompleted(self):  # todo: unused
        if self.leads_count == 0:
            return 0
        return self.leads.offers_completed.count() / self.leads.count() * 100

    def save(self, *args, **kwargs):
        if self.csv_files:
            self.filename = self.csv_files.name

        super(CSVFile, self).save(*args, **kwargs)
        self.create_leads_from_file()
        super(CSVFile, self).save(*args, **kwargs)

    def __unicode__(self):
        name = self.filename or self.csv_files.name
        return u'{} is {} uploaded by {} contains {} leads'.format(name, self.status, self.uploaded_by, self.leads_count)
