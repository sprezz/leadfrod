from django.contrib import admin
from models import *
from locking.admin import LockableAdmin

admin.site.register(LeadSource)
admin.site.register(Niche)
admin.site.register(CSVFile)
admin.site.register(WorkManager)
admin.site.register(Owner)
admin.site.register(Company)
admin.site.register(Network)
admin.site.register(Advertiser)
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
