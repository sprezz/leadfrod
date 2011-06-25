from django.contrib import admin
from rotator.models import *
from django.db.models import Sum
from locking.admin import LockableAdmin
from django.contrib.admin.views.main import ChangeList
from django import forms


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
    list_display = ('owner', 'network', 'username', 'last_checked', 'revenue', 'today_revenue',)
    list_display_links = ('owner', )
    list_filter = ('network',)
    
    def revenue(self, account):
        return Earnings.objects.filter(offer__account=account).extra(
                    select={'total': 'sum(revenue)'})[0].total
    
    #def today_revenue(self, account):
    #    today = datetime.date.today()
    #    return Earnings.objects.filter(offer__account=account, date__month=today.month, 
    #        date__year=today.year, date__day=today.day).extra(
    #            select={'total': 'sum(revenue)'})[0].total


class OfferAdmin(admin.ModelAdmin):
    model = Offer

    class Media:
        js = ['/media/admin/js/offer.js', ]

    list_display = ('name','offer_num','network', 'account','owner_name',
                    'capacity', 'daily_cap', 'advertiser', 'status',
                    'capacity_error', 'submits_today')
    list_display_links = ('name', )
    search_fields = ['name', 'network__name', 'network__description',
                     'account__username', 'account__company__owner__name',
                     'advertiser__name', 'advertiser__description']
    list_filter = ('status', 'niche', 'network', 'account',  )

    actions = ['add_clicks_dailycap', 'substract_clicks_dailycap',
               'add_clicks_capacity', 'substract_clicks_capacity',
               'activate', 'paused', 'set_submits_today',]

    def capacity_error(self, offer):
        """
        Checks if offer have enough budget to be selected
        """
        daily_cap = offer.get_capacity_today
        if not daily_cap.checkOfferCapacity(offer.payout):
            return 'run out of offer capacity'
        if offer.hasAdvertiser() and not daily_cap.checkAdvertiserCapacity(
                                                                offer.payout):
            return "run out of advertiser's offer capacity \
                                                    with %s" % (offer.account)
        if not daily_cap.checkAccountCapacity(offer.payout):
            return 'run out of account capacity %s' % (daily_cap.account)

        if not daily_cap.checkCompanyCapacity(offer.payout):
            return 'run out of company capacity %s' % (daily_cap.company)

        if not daily_cap.checkOwnerCapacity(offer.payout):
            return 'run out of owner capacity %s' % (daily_cap.owner)
        return "OK"
    capacity_error.allow_tags = True

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
    
    def activate(self, request, queryset):
        queryset.update(status='active')
    activate.short_description = "Set active"

    def paused(self, request, queryset):
        queryset.update(status='paused')
    paused.short_description = "Set paused"
   
    def set_submits_today(self, request, queryset):
        queryset.update(submits_today=1)
    set_submits_today.short_description = "Set submits_today to 1"


class LeadAdmin(LockableAdmin):
    model = Lead


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


class EarningChangeList(ChangeList):
    def get_summary(self):        
        queryset_count = self.get_query_set().select_related()
        model_admin = self.model_admin
        list_summary_values = [0]*len(model_admin.list_display)
        for earning in queryset_count.all():
            for field in model_admin.list_summary:
                attr = getattr(model_admin, field, 0)
                if attr:
                    attr = attr(earning)
                else:                
                    attr = getattr(earning, field, 0)
                    attr = attr() if callable(attr) else attr
                
                attr = float(attr)
                                        
                index = model_admin.list_display.index(field)               
                list_summary_values[index] += attr  
        return list_summary_values
        

class EarningsAdmin(admin.ModelAdmin):    
    model = Earnings
    
    chlen = "qwert"
    
    list_display = ('network', 'account', 'offer_name', 'offer_num', 'date',
        'campaign', 'payout', 'clicks', 'pps', 'mpps', 'revenue', 
        'submits_today', 'conv')
    list_filter = ('date', 'niche', 'status', 'network',)
    
    list_summary = ['pps', 'mpps', 'submits_today', 'revenue', 'clicks', 
                    'conv']    
    
    actions = ['add_clicks_dailycap', 'substract_clicks_dailycap',
               'add_clicks_capacity', 'substract_clicks_capacity',
               'activate', 'paused',]    
    
    def activate(self, request, queryset):
        for q in queryset:
            q.offer.status ='active'
            q.offer.save()
        queryset.update(status='active')
    activate.short_description = "Set active"

    def paused(self, request, queryset):
        for q in queryset:
             q.offer.status ='paused'
             q.offer.save()          
    paused.short_description = "Set paused"
    
    def add_clicks_dailycap(self, request, queryset):
        for q in queryset:
            q.offer.daily_cap +=5
            q.offer.save()
    add_clicks_dailycap.short_description = "Add 5 clicks to daily cap"

    def substract_clicks_dailycap(self, request, queryset):
        for q in queryset:
            if q.offer.daily_cap < 5:
                q.offer.daily_cap = 0
            else:
                q.offer.daily_cap -=5
            q.offer.save()
    substract_clicks_dailycap.short_description = "Substract 5 clicks from daily cap"

    def add_clicks_capacity(self, request, queryset):
        for q in queryset:
            q.offer.capacity +=5
            q.offer.save()
    add_clicks_capacity.short_description = "Add 5 clicks to capacity"

    def substract_clicks_capacity(self, request, queryset):
        for q in queryset:            
            if q.offer.capacity < 5:
                q.offer.capacity = 0
            else:
                q.offer.capacity -=5
            q.save()
    substract_clicks_capacity.short_description = "Substract 5 clicks from capacity"
    
    class Media:
        css = {
            "all": ("css/admin_earnings.css",),
        }

    def submits_today(self, earning):
        return earning.offer.submits_today
    
    def pps(self, earning):        
        return earning.pps()        
    pps.admin_order_field = 'admin_pps'
    
    def conv(self, earning):        
        return earning.conv()        
    conv.admin_order_field = 'admin_conv'
    
    def mpps(self, earning):
        return earning.mpps()
    mpps.admin_order_field = 'admin_mpps'
    
    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return EarningChangeList

    def queryset(self, request):
        queryset = super(EarningsAdmin, self).queryset(request)
        queryset = queryset.select_related()
        queryset = queryset.extra(select={
                'admin_pps': "revenue / rotator_offer.submits_today",
                'admin_mpps': "(revenue + rotator_earnings.payout) / \
                                            (rotator_offer.submits_today + 1)",                    
                'admin_conv': "(revenue / rotator_earnings.payout) / clicks",
        })
            
        return queryset
    
    def __call__(self, *args, **kwargs):
        if args or kwargs:
            return super(EarningsAdmin, self).__call__(*args, **kwargs)
        return self
        

class UnknownOfferAdmin(admin.ModelAdmin):
    model = UnknownOffer

    list_display = ('network', 'account', 'offer_num', 'date')
    list_filter = ('date', 'network',)


class AccountAPIAdmin(admin.ModelAdmin):
    model = AccountAPI
    list_display = ('account', 'affiliate_id', 'api_key',)
    

class CSVFileAdminForm(forms.ModelForm):
    model = CSVFile

    def clean(self):
        data = self.cleaned_data
        if 'csv_files' in data and 'filesize' in data and not data['filesize']: # only for creating
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
    list_display = ('date_time', 'filename', 'niche', 'status', 'uploaded_by', 'filesize', 'active_leads', 'completed_leads', 'leads', )
    fieldsets = [
        (None, {'fields': [
                'lead_source', 'niche', 'date_time', 'uploaded_by', 'filename', 'cost', 'max_offers', 'csv_headers', 
                'status', 'description', 'csv_files', 'workers', 'has_header', 'filesize'
                ]}),

    ]  
        
    def leads(self, csv):
        return csv.leads.count()
    
    def active_leads(self, csv):
        return csv.leads.unlocked.filter(csv=csv, status='active', worker__isnull=True, deleted=False).count()
    
    def completed_leads(self, csv):
        return csv.leads.filter(status='completed').count()


class ManualQueueAdmin(admin.ModelAdmin):
    model = ManualQueue
    list_display = ('url', 'size', 'createdDate')
    
    
class ProxyServerAdmin(admin.ModelAdmin):
    model = ProxyServer
    list_display = ('host', 'exceptions')
        

admin.site.register(ProxyServer, ProxyServerAdmin)
admin.site.register(ManualQueue, ManualQueueAdmin)
admin.site.register(AccountAPI, AccountAPIAdmin)
admin.site.register(Niche, NicheAdmin)
admin.site.register(LeadSource)
admin.site.register(CSVFile, CSVFileAdmin)
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

