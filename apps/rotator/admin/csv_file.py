# -*- coding:utf-8 -*-
from django import forms
from django.contrib import admin
from rotator.models import CSVFile


class CSVFileAdminForm(forms.ModelForm):
    model = CSVFile

    def clean(self):
        data = self.cleaned_data
        if 'csv_files' in data and 'filesize' in data and not data['filesize']:  # only for creating
            str = ''
            for chunk in data['csv_files'].chunks():
                str += chunk

            data['filesize'] = len(str)
            if CSVFile.objects.filter(filesize=data['filesize'], filename='rotator/csvfiles/%s' % data['csv_files'].name).count():
                raise forms.ValidationError("File %s was uploaded earlierly. Please download new file." % data['csv_files'].name)

        return data


class CSVFileAdmin(admin.ModelAdmin):
    model = CSVFile
    form = CSVFileAdminForm
    filter_horizontal = ['workers']
    list_display = ('date_time', 'filename', 'niche', 'status', 'uploaded_by', 'filesize', 'max_offers', 'active_leads', 'completed_leads', 'leads', )
    fieldsets = [
        (None, {'fields': [
            'lead_source', 'niche', 'date_time', 'uploaded_by', 'filename', 'cost', 'max_offers', 'csv_headers',
            'status', 'description', 'csv_files', 'workers', 'has_header', 'filesize'
        ]}),

    ]

    def leads(self, csv):
        leads_count = csv.leads.count()
        if leads_count:
            return u'<a href="/admin/rotator/lead/?csv__id__exact={}" target="_blank">{}</a>'.format(csv.id, leads_count)
        return 0
    leads.allow_tags = True

    def active_leads(self, csv):
        return csv.unlocked_leads().filter(status='active', worker__isnull=True, deleted=False).count()

    def completed_leads(self, csv):
        completed_leads_count = csv.leads.filter(status='completed').count()
        if completed_leads_count:
            return u'<a href="/admin/rotator/lead/?csv__id__exact={}&status=completed" target="_blank">{}</a>'.format(csv.id, completed_leads_count)
        return 0
    completed_leads.allow_tags = True
