from django.contrib import admin
from models import *
from locking.admin import LockableAdmin

admin.site.register(LeadSource)
admin.site.register(Niche)

class LeadInline(admin.TabularInline):
    model = Lead
class CSVFileAdmin(admin.ModelAdmin):
    inlines = [LeadInline]
admin.site.register(CSVFile,CSVFileAdmin)

admin.site.register(WorkManager)
admin.site.register(Owner)
admin.site.register(Company)
admin.site.register(Network)

class AdvertiserAccountCapacityInline(admin.TabularInline):
    model = AdvertiserAccountCapacity
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('name','daily_cap', 'status','numberOfAccounts' )
    list_display_links = ('name','daily_cap', 'status' )
    search_fields = ['name']
    fieldsets = [
        (None,               {'fields': ['name','daily_cap', 'status']}),
        # ('Offer information', {'fields': ['offers'], 'classes': ['collapse']}),
    ]
    inlines = [AdvertiserAccountCapacityInline]
admin.site.register(Advertiser,AdvertiserAdmin)

admin.site.register(Account)
admin.site.register(LeadSourceOfferExclusion)
admin.site.register(Offer)
admin.site.register(IPSolution)
admin.site.register(WorkerProfile)

class LeadAdmin(LockableAdmin):
    list_display = ('lock','csv','status','worker','deleted', )
    list_display_links = ('csv','status','worker','deleted' )
admin.site.register(Lead, LeadAdmin)

admin.site.register(TrafficHolder)
admin.site.register(OfferClicks)
admin.site.register(DailyCap)
