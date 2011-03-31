from django.contrib import admin
from models import *
from locking.admin import LockableAdmin


class NicheAdmin(admin.ModelAdmin):
    model=Niche
    list_display = ('name', 'status', 'min_clicks', 'max_clicks', 'priority', )


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


class AccountAdmin(admin.ModelAdmin):
    model = Account
    list_display = ('owner','network', 'username', 'last_checked')
    list_display_links = ('owner', )


class OfferAdmin(admin.ModelAdmin):
    model = Offer
    
    class Media:
        js = ['/media/admin/js/offer.js', ]

    list_display = ('name','offer_num','network', 'account','owner_name',
                    'capacity', 'daily_cap', 'advertiser', 'status',)
    list_display_links = ('name', )
    search_fields = ['name', 'network__name', 'network__description',
                     'account__username', 'account__company__owner__name', 
                     'advertiser__name', 'advertiser__description']
    list_filter = ('network', 'account', 'status', )
    
    actions = ['add_clicks_dailycap', 'substract_clicks_dailycap',
               'add_clicks_capacity', 'substract_clicks_capacity',]

    def add_clicks_dailycap(self, request, queryset):
        for q in queryset:
            q.daily_cap +=5
            q.save()
    add_clicks_dailycap.short_description = "Add 5 clicks to daily cap"
    
    def substract_clicks_dailycap(self, request, queryset):
        for q in queryset:
            if q.daily_cap < 5:
                q.daily_cap = 0
            else:
                q.daily_cap -=5
            q.save()
    substract_clicks_dailycap.short_description = "Substract 5 clicks from daily cap"
    
    def add_clicks_capacity(self, request, queryset):
        for q in queryset:
            q.capacity +=5
            q.save()
    add_clicks_capacity.short_description = "Add 5 clicks to capacity"
    
    def substract_clicks_capacity(self, request, queryset):
        for q in queryset:            
            if q.capacity < 5:
                q.capacity = 0
            else:
                q.capacity -=5
            q.save()
    substract_clicks_capacity.short_description = "Substract 5 clicks from capacity"


class LeadAdmin(LockableAdmin):
    model=Lead
#    list_display = ('lock','csv','status','worker','deleted', )
#    list_display_links = ('csv','status','worker','deleted' )


class OfferQueueAdmin(admin.ModelAdmin): 
    model = OfferQueue
    list_display = ('network', 'account', 'offerName', 'offerNum', 'size',)
    
    actions = ['add_clicks_size', 'substract_clicks_size',]

    def add_clicks_size(self, request, queryset):
        for q in queryset:
            q.size +=5
            q.save()
    add_clicks_size.short_description = "Add 5 clicks to size"
    
    def substract_clicks_size(self, request, queryset):
        for q in queryset:
            if q.size < 5:
                q.size = 0
            else:
                q.size -=5
            q.save()
    substract_clicks_size.short_description = "Substract 5 clicks from size"
    

class EarningsAdmin(admin.ModelAdmin):
    model = Earnings
    
    list_display = ('network', 'account', 'offer_name', 'offer_num', 'date',
        'campaign', 'status', 'payout', 'clicks', 'pps', 'mpps', 'revenue')
    list_filter = ('date', 'status', 'network',)

    
class UnknownOfferAdmin(admin.ModelAdmin):
    model = UnknownOffer
    
    list_display = ('network', 'account', 'offer_num', 'date')
    list_filter = ('date', 'network',)
    

#class LeadInline(admin.TabularInline):
#    model = Lead
#class CSVFileAdmin(admin.ModelAdmin):
#    inlines = [LeadInline]

#class OfferInline(admin.TabularInline):
#    model = Offer
#    
#class CapacityAdmin(admin.ModelAdmin):
#    inlines = [OfferInline]
#admin.site.register(Capacity,CapacityAdmin) 

admin.site.register(Niche, NicheAdmin)
admin.site.register(LeadSource)
admin.site.register(CSVFile)
admin.site.register(WorkManager)
admin.site.register(Owner)
admin.site.register(Company)
admin.site.register(Network)
admin.site.register(AdvertiserAccountCapacity)
admin.site.register(Advertiser,AdvertiserAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Offer,OfferAdmin)
admin.site.register(IPSolution)
admin.site.register(WorkerProfile)
admin.site.register(Capacity)
admin.site.register(Lead, LeadAdmin)
admin.site.register(TrafficHolderOrder)
admin.site.register(UnknownOffer, UnknownOfferAdmin)      
admin.site.register(OfferQueue, OfferQueueAdmin)    
admin.site.register(Earnings, EarningsAdmin)  
  
