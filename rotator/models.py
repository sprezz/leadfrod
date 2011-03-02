from django.db import models
import datetime
from django.db.models import Sum
from locking import models as locking
from django.contrib.auth.models import User
from django.db.models import F    

#VERSION 2

STATUS_LIST = (
               ('active','active'),
               ('banned','banned'),
               ('paused','paused'), 
               ('suspicious','suspicious'), 
               ('deleted','deleted'),
               )
    
PAYMENT_TYPE_LIST = (
                     ('CHECK','CHECK'),
                     ('WIRE/ACH','WIRE/ACH'),
                     ('PAYPAL','PAYPAL'),
                     )

class IPSolution(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255, null = True, blank=True)

    class Meta:
        verbose_name='IP Solution'
        verbose_name_plural='IP Solutions'

class WorkerProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    odesk_id = models.CharField(max_length=30)
    ip_solution = models.ForeignKey(IPSolution)
    now_online = models.BooleanField(default=False, editable=False)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255, null = True, blank=True)
    
    class Meta:
        verbose_name='Worker profile'
        verbose_name_plural='Workers profiles'
        
    def __unicode__ (self):
        return u'%s %s @ odesk as %s' % (self.user.first_name, self.user.last_name, self.odesk_id) 

class NoWorkException(Exception):
    pass
class WorkInterceptedException(Exception):
    pass

class Capacity(models.Model):
    "Capacity of remaining daily cap values of corresponding objects. "
    date = models.DateField()
    offer = models.ForeignKey('Offer', related_name='dailycap_capacity')
    advertiser = models.ForeignKey('Advertiser', related_name='dailycap_capacity', null=True, blank=True)
    account = models.ForeignKey('Account', related_name='dailycap_capacity')
    owner = models.ForeignKey('Owner', related_name='dailycap_capacity')
    company = models.ForeignKey('Company', related_name='dailycap_capacity')
    
    def checkOfferCapacity(self, payout):
        if not self.offer.is_active():return False
        return payout<=self.offer.capacity
    def checkAdvertiserCapacity(self, payout):
        if not self.advertiser: return True
        if not self.advertiser.is_active():return False
        
        adv_account_cap = self.advertiser.getAccountCapacity(self.offer.account)
        return payout <= adv_account_cap.capacity
    def checkAccountCapacity(self, payout):
        if not self.account.is_active():return False
        return payout<=self.account.capacity
    def checkCompanyCapacity(self, payout):
        if not self.company.is_active():return False
        return payout<=self.company.capacity
    def checkOwnerCapacity(self, payout):
        if not self.owner.is_active():return False
        return payout<=self.owner.capacity
    
    def updateOfferCapacity(self, payout):
        self.offer.capacity -= self.offer.payout
        self.offer.save()
    def updateAdvertiserCapacity(self, payout):
        if not self.offer.hasAdvertiser(): return
        adv_account_cap = self.advertiser.getAccountCapacity(self.offer.account)
        adv_account_cap.capacity -= self.offer.payout
        adv_account_cap.save()
    def updateAccountCapacity(self, payout):
        self.account.capacity -= self.offer.payout
        self.account.save()
    def updateCompanyCapacity(self, payout):
        self.company.capacity -= self.offer.payout
        self.company.save()
    def updateOwnerCapacity(self, payout):
        self.owner.capacity -= self.offer.payout
        self.owner.save()
    
    def clearOfferCapacity(self, payout):
        self.offer.capacity = self.offer.daily_cap
        self.offer.save()
    def clearAdvertiserCapacity(self, payout):
        if not self.offer.hasAdvertiser(): return
        self.advertiser.clearCapacityOfAllAccounts()
    def clearAccountCapacity(self, payout):
        self.account.capacity = self.account.daily_cap
        self.account.save()
    def clearCompanyCapacity(self, payout):
        self.company.capacity = self.company.daily_cap
        self.company.save()
    def clearOwnerCapacity(self, payout):
        self.owner.capacity = self.owner.daily_cap
        self.owner.save()
    
    class Meta:
        verbose_name='Capacity'
        verbose_name_plural='Capacity instances'
        
    def __unicode__ (self):
        return u'%s %s %s %s %s %s %s' % (self.date, 
                                         self.offer, 
                                         self.offer.capacity,
                                         self.advertiser.capacity,
                                         self.account.capacity,
                                         self.owner.capacity,
                                         self.company.capacity) 

class WorkManager(models.Model):
    "Manages work of workers through work strategy"
    workers_online = models.ManyToManyField(User, null=True, blank=True)
    
    class WorkItem(object):
        def __init__ (self, workLead=None, workOffers=None):
            self.lead = workLead
            if workOffers is None:
                self.offers = []
            else:
                self.offers = workOffers
                
        def addOffer(self, anOffer):
            self.lead.offers_requested.add(anOffer)
            self.lead.save()
            self.offers.append(anOffer) 
               
    class WorkStrategy(object):
        def __init__ (self):
            pass
        def nextLead(self, csvFile):
            try:
                csvLeads = Lead.unlocked.filter(csv=csvFile, 
                                                status='active', 
                                                worker__isnull=True, 
                                                deleted=False).order_by('?')
                if csvLeads.count()==0: return None
                return csvLeads[0]
            except Lead.DoesNotExist:
                return None    
            
        def getOffersForLead(self, wi):
            """
                abudarevsky: how I understood (mayy be wrong) - each Lead goes to advertiser sooner or later but untill it is accepted by an Advertiser it can proposed for different Offers. So once we give the Lead to Advertiser we have to lock Lead not to show for others Offers
                [3:28:48 MSD] rovin.v: so an offer may have an advertiser, at most 1 advertiser
                [3:28:59 MSD] rovin.v: an offer may have 0 or 1 advertisers
                [3:29:04 MSD] abudarevsky: exactly
                [3:29:06 MSD] rovin.v: an advertiser may have 0 or more offers
                [3:29:12 MSD] abudarevsky: exactly
                [3:29:14 MSD] rovin.v: 1 lead can go into X offers
                [3:29:19 MSD] rovin.v: like 5
                [3:29:19 MSD] abudarevsky: true
                [3:29:34 MSD] rovin.v: each of those offers advertisers have to be unique or should be non existent
                [3:29:52 MSD] rovin.v: so like Advertiser A,B,C,no advertiser, no advertiser
                [3:30:04 MSD] rovin.v: it does not have to use every advertiser
                [3:30:13 MSD] rovin.v: it randomly picks 5 offers based on these rules
            """
            """
                Algo:
                    1. Lead.getNiche
                    2. Get Offers per Niche
                    3.1 Filter out by DailyCap and Status
                    3.2 Filter out by unique assigned advertisers and no advertiser 
                    4. Get 5 random from the rest
                    5. Return the list 
                    
            """
            leadNiche = wi.lead.getNiche()
            offers = Offer.objects.filter(niche=leadNiche, status='active', capacity__gt=F('payout')).order_by('?')
            for offer in offers:
                if offer.checkCapacity():
                    if offer.hasAdvertiser() and wi.lead.checkAdvertiser(offer.advertiser):
                        continue
                    wi.lead.add(offer.advertiser)
                    wi.lead.save()
                    
                    wi.addOffer(offer)
                    if len(wi.offers)==5: break
        
    work_strategy = WorkStrategy()    
    def signIn(self, worker):
        worker.now_online = True
        worker.save()
        self.workers_online.add(worker)
        self.save()
    
    def nextWorkItem(self, worker):
        for csv_file in CSVFile.objects.filter(workers=worker).order_by('?'):
            lead = self.work_strategy.nextLead(csv_file)
            if lead is not None: break
        
        if not lead: raise NoWorkException()
        
        if not lead.is_locked():
            lead.lock_for(worker)
            lead.worker = worker
            lead.save()
        else:
            raise WorkInterceptedException()
        
        wi = WorkManager.WorkItem(lead)    
        self.work_strategy.getOffersForLead( wi )
        
        if len(wi.offers)==0:
            lead.unlock_for(worker)
            lead.worker = None
            lead.save()
            raise NoWorkException()
        return wi 
       
    def signOut(self, worker):
        worker.now_online = False
        worker.save()
        self.workers_online.remove(worker)
        self.save()
        
    class Meta:
        verbose_name='WorkManager'
        verbose_name_plural='WorkManagers'
        
    def __unicode__ (self):
        return u'WorkManager: %s workers online' % self.workers_online.count()

class LeadSource(models.Model):
    name = models.CharField(max_length = 255)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255, null=True, blank=True)
    
    class Meta:
        verbose_name='Lead Source'
        verbose_name_plural='Lead Sources'
        
    def __unicode__ (self):
        return u'%s' % (self.name)
    
class Niche(models.Model):
    name = models.CharField(max_length = 30)
    min_epc = models.FloatField()
    max_epc = models.FloatField()
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True, blank=True)
    
    class Meta:
        verbose_name='Niche'
        verbose_name_plural='Niches'
    
    def is_active(self):
        return self.status=='active'
        
    def __unicode__ (self):
        return u'%s' % (self.name) 
    
class CSVFile(models.Model):
    lead_source = models.ForeignKey(LeadSource)
    niche = models.ForeignKey(Niche)
    filename = models.CharField(max_length=30)
    date_time = models.DateTimeField(default = datetime.datetime.now())
    uploaded_by  = models.CharField(max_length=30)
    cost = models.FloatField(default = 0)
#    revenue = models.FloatField(default = 0) to be calculated
#    percent_completed = models.FloatField(default = 0) to be calculated
    workers = models.ManyToManyField(User, null = True, blank=True, related_name='assignments')
    max_offers = models.FloatField(default = 5)
    csv_headers = models.TextField(null = False, blank=True)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255, null=True, blank=True)
  
    class Meta:
        verbose_name='CSV File'
        verbose_name_plural='CSV Files'
    
    def is_active(self):
        return self.status=='active'
    
    def getRevenue(self):
        return self.leads.aggregate(Sum('offers_completed__payout'))['offers_completed__payout__sum']  
      
    def getPercentOfCompleted(self):
        if self.leads.count()==0: return 0 
        return self.leads.offers_completed.count()/self.leads.count()*100   
     
    def __unicode__ (self):
        return u'%s' % (self.filename)
    
class AdvertiserAccountCapacity(models.Model):
    advertiser = models.ForeignKey('Advertiser', related_name='account_capacity')
    account = models.ForeignKey('Account', related_name='advertiser_capacity')
    capacity = models.FloatField(default=25)
    
    class Meta:
        verbose_name="Advertiser's Account Capacity"
        verbose_name_plural="Advertiser's Account Capacity instances"
        
    def __unicode__ (self):
        return u'%s/%s' % (self.advertiser, self.account)
     
class Advertiser(models.Model):
    name = models.CharField(max_length=30)
    daily_cap = models.FloatField(default=25)
    status = models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255, null = True, blank=True)
    
    def is_active(self):
        return self.status=='active'
    
    def numberOfAccounts(self):
        return self.account_capacity.count()
    numberOfAccounts.short_description=u"Account qty"
    
    def clearCapacityOfAllAccounts(self):
        self.account_capacity.all().update(capacity=self.daily_cap)
    def getAccountCapacity(self, adv_account):
        if  AdvertiserAccountCapacity.objects.filter(advertiser=self, account = adv_account).exists():
            return self.account_capacity.get(account = adv_account)
        return None
                
    class Meta:
        verbose_name='Advertiser'
        verbose_name_plural='Advertisers'
        
    def __unicode__ (self):
        return u'%s' % (self.name)
    
        
class Lead(locking.LockableModel):
    csv = models.ForeignKey(CSVFile, related_name='leads')
    worker = models.ForeignKey(User, null=True, blank=True, related_name='leads_in_work')
    advertisers = models.ManyToManyField(Advertiser, related_name='leads', null=True, blank=True)
    
    started_on = models.DateTimeField(null = True, blank=True)
    ended_on = models.DateTimeField(null = True, blank=True)
    deleted = models.BooleanField(default=False) # Should be accessible after?
#    offers_requested = models.CharField(max_length=200, null = True, blank=True)
#    offers_completed = models.CharField(max_length=200, null = True, blank=True)
    offers_requested = models.ManyToManyField('Offer', related_name='proposed_leads', null = True, blank=True)
    offers_completed = models.ManyToManyField('Offer', related_name='completed_leads', null = True, blank=True)
    
    lead_data = models.TextField()
    ip_address = models.CharField(max_length=30, null = True, blank=True)
    user_agent = models.CharField(max_length=100, null = True, blank=True)
    subid = models.CharField(max_length=100, null = True, blank=True)
    status= models.CharField(max_length = 30, choices = STATUS_LIST, null = True, blank=True)
    description = models.CharField(max_length = 30, null = True, blank=True)

#    def isLocked(self):
#        return self.worker is not None
    
    class Meta:
        verbose_name='Lead'
        verbose_name_plural='Leads'
    
    def is_active(self):
        return self.status=='active'
    
    def checkAdvertiser(self, anAdvertiser):
        return self.advertisers.filter(pk=anAdvertiser.pk).count()>0 
    
    def getNiche(self):
        return self.csv.niche
    
#    def __unicode__ (self):
#        str = '%s %s'(self.description,self.csv)
#        if self.isLocked():
#            str+=' in work %s' % self.worker
#        return str
    

#Should I have a WorkerCSV table? Will that be able to show checkboxes on both
#a worker's page and a csv's page?
#How do I make object names in django admin plural form?
#What does null=True really mean if I still have to add something to the admin field?

class Offer(models.Model):
    network = models.ForeignKey('Network', related_name='offers')
    account = models.ForeignKey('Account', related_name='offers')
    niche = models.ForeignKey(Niche, related_name='offers')
    # Each offer may have an advertiser associated with it.
    advertiser = models.ForeignKey(Advertiser, related_name='offers', null=True, blank=True)
    offer_num = models.CharField(max_length=10, null=True, blank=True)
    daily_cap = models.FloatField(default = 10)
    capacity = models.FloatField(default = 10, editable=False)
    url = models.URLField(max_length=2000)
    payout = models.FloatField()
    min_epc = models.FloatField( null=True, blank=True)
    max_epc = models.FloatField( null=True, blank=True)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255, null = True, blank=True)
    
    def is_active(self):
        return self.status=='active'
    
    def hasAdvertiser(self):
        "Checks if this offer already has an advertiser"
        return self.advertiser is not None
    
    def getAdvertiser(self):
        if not self.hasAdvertiser(): return None
        return self.advertiser
    def initCapacity(self):
        today = datetime.datetime.today()
        if Capacity.objects.filter(date = today, offer=self).count()>0:
            return
        capacity = Capacity(date = today, offer = self)
        capacity.account = self.account
        if self.hasAdvertiser():
            capacity.advertiser = self.advertiser
        capacity.company = self.account.company    
        capacity.owner = self.account.company.owner    
        capacity.save()    
        
    def checkCapacity(self):
        today = datetime.datetime.today()
        if not self.dailycap_capacity.filter(date=today).exists(): self.initCapacity()
        daily_capacity = self.dailycap_capacity.get(date=today)
        if not daily_capacity.checkOfferCapacity(self.payout): return False
        if self.hasAdvertiser():
            if not daily_capacity.checkAdvertiserCapacity(self.payout): return False
        if not daily_capacity.checkAccountCapacity(self.payout): return False    
        if not daily_capacity.checkCompanyCapacity(self.payout): return False
        if not daily_capacity.checkOwnerCapacity(self.payout): return False
        
        return True  
    
    def updateCapacity(self):  
        today = datetime.datetime.today()
        if not self.dailycap_capacity.filter(date=today).exists(): self.initCapacity()
        daily_capacity = self.dailycap_capacity.get(date=today)
        daily_capacity.updateOfferCapacity(self.payout)
        if self.hasAdvertiser():
            daily_capacity.updateAdvertiserCapacity(self.payout)
        daily_capacity.updateAccountCapacity(self.payout)    
        daily_capacity.updateCompanyCapacity(self.payout)
        daily_capacity.updateOwnerCapacity(self.payout)
        daily_capacity.save()
    def clearCapacity(self):
        today = datetime.datetime.today()
        if not self.dailycap_capacity.filter(date=today).exists(): self.initCapacity()
        daily_capacity = self.dailycap_capacity.get(date=today)
        daily_capacity.clearOfferCapacity(self.payout)
        if self.hasAdvertiser():
            daily_capacity.clearAdvertiserCapacity(self.payout)
        daily_capacity.clearAccountCapacity(self.payout)    
        daily_capacity.clearCompanyCapacity(self.payout)
        daily_capacity.clearOwnerCapacity(self.payout)
        daily_capacity.save()    
    class Meta:
        verbose_name='Offer'
        verbose_name_plural='Offers'
        
    def __unicode__ (self):
        return u'Offer #%s at %s' % (self.offer_num, self.url)  
    
class Owner(models.Model):
    name = models.CharField(max_length=30)
    daily_cap = models.FloatField(default = 0)
    capacity = models.FloatField(default = 0)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True, blank=True)
    def is_active(self):
        return self.status=='active'
    class Meta:
        verbose_name='Owner'
        verbose_name_plural='Owners'
        
    def __unicode__ (self):
        return u'%s' % (self.name)
    
class Company(models.Model):
    owner = models.ForeignKey(Owner, related_name='companies')
    name_list = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    county= models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    w9_file = models.CharField(max_length=100, null=True, blank=True)
    im_list = models.CharField(max_length=100, null=True, blank=True)
    email_list = models.CharField(max_length=100, null=True, blank=True)
    phone_list = models.CharField(max_length=100, null=True, blank=True)
    daily_cap = models.FloatField(default = 0)
    capacity = models.FloatField(default = 0)
    websites = models.CharField(max_length=100, null=True, blank=True)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255, null=True, blank=True)
    def is_active(self):
        return self.status=='active'
    class Meta:
        verbose_name='Company'
        verbose_name_plural='Companies'
        
    def __unicode__ (self):
        return u'%s' % (self.name_list)
    
class Account(models.Model):
    network = models.ForeignKey('Network', related_name='accounts')
    company = models.ForeignKey(Company, related_name='accounts')
    
    username = models.CharField(max_length = 30)
    password = models.CharField(max_length = 30, null=True, blank=True)
    user_id = models.CharField(max_length = 30, null=True, blank=True)
    AM = models.CharField(max_length = 30)
    phone = models.CharField(max_length = 30, null=True, blank=True)
    AM_phone_list = models.CharField(max_length = 30, null=True, blank=True)
    AM_email_list = models.CharField(max_length = 30, null=True, blank=True)
    AM_IM_list = models.CharField(max_length = 30, null=True, blank=True)
    recieved_check_once = models.BooleanField(default=False, blank=True)
    stats_configured = models.BooleanField(default=False, blank=True)
    payments_via = models.CharField(max_length = 30, choices=PAYMENT_TYPE_LIST)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    payment_frequency = models.CharField(max_length = 30, null=True, blank=True)
    daily_cap = models.FloatField(default = 100)
    capacity = models.FloatField(default = 100)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255, null=True, blank=True)
    
    primary = models.BooleanField(default=True)
    
    def is_active(self):
        return self.status=='active'
    
    class Meta:
        verbose_name='Account'
        verbose_name_plural='Accounts'
        
    def __unicode__ (self):
        return u'%s' % (self.username)
    
class Network(models.Model):
    name = models.CharField(max_length = 30)
    url = models.CharField(max_length = 100)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True, blank=True)
    
    def is_active(self):
        return self.status=='active'
    
    class Meta:
        verbose_name='Network'
        verbose_name_plural='Networks'
        
    def __unicode__ (self):
        return u'%s' % (self.name)
    
class LeadSourceOfferExclusion(models.Model):
    leadsource = models.ForeignKey(LeadSource)
    advertiser = models.ForeignKey(Advertiser)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True)

           
    
TRAFFIC_HOLDER_STATUS_LIST = (
               ('awaiting approval','awaiting approval'),
               ('active','active'),
               ('paused','paused'), 
               ('deleted','deleted'), 
               ('depleted','depleted'),
               )

class TrafficHolder(models.Model):
    order_id = models.CharField(max_length=30)
    hourly_rate = models.IntegerField(null = True)
    clicks_received = models.IntegerField(null = True)
    clicks_total = models.IntegerField(null = True)
    internal_url = models.CharField(max_length=200)
    approval_url = models.CharField(max_length=200, null = True)
    status = models.CharField(max_length = 30, choices = TRAFFIC_HOLDER_STATUS_LIST)
    description = models.CharField(max_length = 30)
    
class OfferClicks(models.Model):
    offer_id = models.ForeignKey(Offer)
    clicks_remaining = models.IntegerField(null = True)
    last_click_date_time = models.DateTimeField(null = True)
    priority = models.IntegerField(default = 1)

class DailyCap(models.Model):
    date = models.DateTimeField(datetime.date.today())
    offer = models.ForeignKey(Offer)
    submits = models.IntegerField(default = 0)
    lead_list = models.CharField(max_length = 30)
    worker_list = models.CharField(max_length = 30)
    