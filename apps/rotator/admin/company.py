# -*- coding:utf-8 -*-
from django.contrib import admin
from rotator.models import Account


class AccountInlineTabular(admin.TabularInline):
    model = Account
    extra = 0


class CompanyAdmin(admin.ModelAdmin):
    inlines = [AccountInlineTabular]
