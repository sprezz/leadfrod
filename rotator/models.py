from django.db import models
import datetime
from django.db.models import Sum
from locking import models as locking
from django.contrib.auth.models import User
from rotator.rules import check_offer_advertiser_capacity,\
    check_account_capacity, NoCapacityException
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
            self.offers.append(anOffer) 
               
    class WorkStrategy(object):
        def __init__ (self):
            pass
        def nextLead(self, csvFile):
            try:
                csvLeads = Lead.unlocked.filter(csv=csvFile).order_by('?')
                return csvLeads[0]
            except Lead.DoesNotExist:
                return None    
            
        def getOffersForLead(self, lead):
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
            leadNiche = lead.getNiche()
            suggestions = []
            offers = Offer.objects.filter(niche=leadNiche, status='active', daily_cap__gt=F('payout'))
            for offer in offers:
                try:
                    if offer.hasAdvertiser():
                        check_offer_advertiser_capacity(offer)
                    check_account_capacity(offer.advertiser)
                    check_account_capacity(offer.advertiser)
                except NoCapacityException:
                    continue    
            
        
    work_strategy = WorkStrategy()    
    def signIn(self, worker):
        worker.now_online = True
        worker.save()
        self.workers_online.add(worker)
        self.save()
    
    def nextWorkItem(self, worker):
        csv_file = CSVFile.objects.filter(workers=worker).order_by('?')[0]
        lead = self.work_strategy.nextLead(csv_file)
        if not lead:
            raise NoWorkException
        if not lead.is_locked():
            lead.lock_for(worker)
            lead.worker = worker
            lead.save()
        else:
            raise WorkInterceptedException    
        offers = self.work_strategy.getOffersForLead(lead)
        return WorkManager.WorkItem(lead, offers) 
       
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
    
    def getRevenue(self):
        return self.leads.aggregate(Sum('offers_completed__payout'))['offers_completed__payout__sum']  
      
    def getPercentOfCompleted(self):
        if self.leads.count()==0: return 0 
        return self.leads.offers_completed.count()/self.leads.count()*100   
     
    def __unicode__ (self):
        return u'%s' % (self.filename) 

class Advertiser(models.Model):
    name = models.CharField(max_length=30)
    daily_cap = models.FloatField(default = 25)
    status = models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255)
    
    class Meta:
        verbose_name='Advertiser'
        verbose_name_plural='Advertisers'
        
    def __unicode__ (self):
        return u'%s' % (self.name)
        
class Lead(locking.LockableModel):
    csv = models.ForeignKey(CSVFile, related_name='leads')
    worker = models.ForeignKey(User, null=True, blank=True, related_name='leads_in_work')
    
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
    account = models.ForeignKey('Account', related_name='offers')
    niche = models.ForeignKey(Niche, related_name='offers')
    # Each offer may have an advertiser associated with it.
    advertiser = models.ForeignKey(Advertiser, related_name='offers', null=True, blank=True)
    offer_num = models.CharField(max_length=10)
    daily_cap = models.FloatField(default = 10)
    url = models.URLField(max_length=2000)
    payout = models.FloatField()
    min_epc = models.FloatField()
    max_epc = models.FloatField()
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255, null = True, blank=True)
    
    def hasAdvertiser(self):
        "Checks if this offer already has an advertiser"
        return self.advertiser is not None
    
    def getAdvertiser(self):
        if not self.hasAdvertiser(): return None
        return self.advertiser        
    
    class Meta:
        verbose_name='Offer'
        verbose_name_plural='Offers'
        
    def __unicode__ (self):
        return u'Offer #%s at %s' % (self.offer_num, self.url)  
    
class Owner(models.Model):
    name = models.CharField(max_length=30)
    daily_cap = models.FloatField(default = 0)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True, blank=True)
    
    class Meta:
        verbose_name='Owner'
        verbose_name_plural='Owners'
        
    def __unicode__ (self):
        return u'%s' % (self.name)
    
class Company(models.Model):
    owner = models.ForeignKey(Owner)
    name_list = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=10)
    county= models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    w9_file = models.CharField(max_length=100)
    im_list = models.CharField(max_length=100)
    email_list = models.CharField(max_length=100)
    phone_list = models.CharField(max_length=100)
    daily_cap = models.FloatField(default = 0)
    websites = models.CharField(max_length=100)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255)
    
    class Meta:
        verbose_name='Company'
        verbose_name_plural='Companies'
        
    def __unicode__ (self):
        return u'%s' % (self.name_list)
    
class Account(models.Model):
    network = models.ForeignKey('Network')
    username = models.CharField(max_length = 30)
    password = models.CharField(max_length = 30, null=True)
    user_id = models.CharField(max_length = 30, null=True)
    AM = models.CharField(max_length = 30)
    phone = models.CharField(max_length = 30, null=True)
    AM_phone_list = models.CharField(max_length = 30, null=True)
    AM_email_list = models.CharField(max_length = 30, null=True)
    AM_IM_list = models.CharField(max_length = 30, null=True)
    recieved_check_once = models.BooleanField(default=False)
    stats_configured = models.BooleanField(default=False)
    payments_via = models.CharField(max_length = 30, choices=PAYMENT_TYPE_LIST)
    last_payment_date = models.DateTimeField(null=True)
    payment_frequency = models.CharField(max_length = 30, null=True)
    daily_cap = models.FloatField(default = 100)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 255, null=True)
    
    class Meta:
        verbose_name='Account'
        verbose_name_plural='Accounts'
        
    def __unicode__ (self):
        return u'%s' % (self.username)
    
class Network(models.Model):
    name = models.CharField(max_length = 30)
    url = models.CharField(max_length = 100)
    description = models.CharField(max_length = 30, null=True, blank=True)
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
    