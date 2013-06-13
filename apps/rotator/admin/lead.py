# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import ACTIVE


class LeadAdmin(admin.ModelAdmin):
    filter_horizontal = ['offers_requested', 'offers_completed', 'advertisers']
    raw_id_fields = ['csv', 'worker']
    list_filter = ['worker', 'status', 'csv', '_locked_at']
    list_display = ['csv', 'worker', 'status', 'started_on', 'ended_on', 'deleted', '_locked_at', '_locked_by', '_hard_lock', 'is_locked']
    actions = ('unlock', 'activate_unlock_and_clean_worker')

    def unlock(self, request, queryset):
        queryset.update(_locked_at=None, _locked_by=None)

    def activate_unlock_and_clean_worker(self, request, queryset):
        queryset.update(status=ACTIVE, worker=None, _locked_at=None, _locked_by=None)
    activate_unlock_and_clean_worker.short_description = 'Activate, unlock and clean worker'
