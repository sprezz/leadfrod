from django.contrib import admin
from models import *
from locking.admin import LockableAdmin

admin.site.register(LeadSource)

class NicheAdmin(admin.ModelAdmin):
    model=Niche
    list_display = ('name', 'status', 'min_clicks', 'max_clicks', 'priority', )
    
admin.site.register(Niche, NicheAdmin)

#class LeadInline(admin.TabularInline):
#    model = Lead
#class CSVFileAdmin(admin.ModelAdmin):
#    inlines = [LeadInline]
admin.site.register(CSVFile)

admin.site.register(WorkManager)
admin.site.register(Owner)
admin.site.register(Company)
admin.site.register(Network)

admin.site.register(AdvertiserAccountCapacity)

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

class AccountAdmin(admin.ModelAdmin):
    model = Account
    list_display = ('owner','network', 'username', )
    list_display_links = ('owner', )

admin.site.register(Account, AccountAdmin)

class OfferAdmin(admin.ModelAdmin):
    model = Offer
    list_display = ('name','offer_num','network', 'account','owner_name', 'capacity', 'daily_cap')
    list_display_links = ('name', )
    search_fields = ['owner','network','account']
    list_filter = ('network', 'account',)
    
admin.site.register(Offer,OfferAdmin)
admin.site.register(IPSolution)
admin.site.register(WorkerProfile)
admin.site.register(Capacity)

class LeadAdmin(LockableAdmin):
    model=Lead
#    list_display = ('lock','csv','status','worker','deleted', )
#    list_display_links = ('csv','status','worker','deleted' )
admin.site.register(Lead, LeadAdmin)
#admin.site.register(Lead)

admin.site.register(TrafficHolderOrder)

class OfferQueueAdmin(admin.ModelAdmin): 
    model=OfferQueue
    list_display = ('network', 'account', 'offerName', 'offerId', )

admin.site.register(OfferQueue, OfferQueueAdmin)

class EarningsAdmin(admin.ModelAdmin):
    model=Earnings
    
admin.site.register(Earnings, EarningsAdmin)    
#class OfferInline(admin.TabularInline):
#    model = Offer
#    
#class CapacityAdmin(admin.ModelAdmin):
#    inlines = [OfferInline]
#admin.site.register(Capacity,CapacityAdmin)    
