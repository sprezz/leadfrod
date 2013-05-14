# -*- coding:utf-8 -*-
import csv
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
import os
from rotator.models import STATUS_LIST, ACTIVE
import settings


class CSVFile(models.Model):
    lead_source = models.ForeignKey('rotator.LeadSource')
    niche = models.ForeignKey('rotator.Niche')
    filename = models.CharField(max_length=255, null=True, blank=True, unique=True)
    filesize = models.IntegerField(default=0)
    date_time = models.DateTimeField(default=datetime.datetime.now())
    uploaded_by = models.CharField(max_length=30)
    cost = models.FloatField(default=0)
    #   revenue = models.FloatField(default = 0) to be calculated
    #   percent_completed = models.FloatField(default = 0) to be calculated
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

    def hasLeads(self):
        """Checks if this file has leads to process. If there is an uploaded file but there is no leads it process them"""
        if (self.csv_files is None or self.csv_files.name is None) and self.leads.count() == 0:
            return False
        if (self.csv_files is None or self.csv_files.name is None) and self.leads.count() > 0:
            return True
        if (self.csv_files is not None and self.csv_files.name is not None) and self.leads.count() > 0:
            return True

        self.filename = self.csv_files.name
        #        self.save()

        name = self.csv_files.name
        csv_full_path = os.path.join(settings.MEDIA_ROOT, name)
        with open(csv_full_path, 'rb') as csvFile:
        #        rows = csv.reader(csvFile, delimiter=';', quotechar='"')
            rows = csv.reader(csvFile)
            for idx, row in enumerate(rows):
                if not row[0]:
                    continue
                if idx == 0 and self.has_header:
                    self.csv_headers = ','.join(row)
                    #                    self.save()
                    continue
                from rotator.models.lead import Lead
                Lead.objects.create(csv=self, status=ACTIVE, lead_data=','.join(row))

        return self.leads.count() > 0

    def is_active(self):
        return self.status == ACTIVE

    def getRevenue(self):
        return self.leads.aggregate(Sum('offers_completed__payout'))['offers_completed__payout__sum']

    def getPercentOfCompleted(self):
        if self.leads.count() == 0:
            return 0
        return self.leads.offers_completed.count() / self.leads.count() * 100

    def save(self, *args, **kwargs):
        super(CSVFile, self).save(*args, **kwargs)
        self.hasLeads()
        super(CSVFile, self).save(*args, **kwargs)

    def __unicode__(self):
        name = self.filename or self.csv_files.name
        #        nleads = 0
        #        if self.hasLeads():
        nleads = self.leads.count()
        return u'%s is %s uploaded by %s contains %s leads' % (name, self.status, self.uploaded_by, nleads)
