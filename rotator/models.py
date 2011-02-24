from django.db import models
import datetime

# Create your models here.
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
    
class LeadSource(models.Model):
    name = models.CharField(max_length = 30)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True)
    
class Niche(models.Model):
    name = models.CharField(max_length = 30)
    min_epc = models.FloatField()
    max_epc = models.FloatField()
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True)
    
class CSV(models.Model):
    lead_source = models.ForeignKey(LeadSource)
    niche = models.ForeignKey(Niche)
    filename = models.CharField(max_length=30)
    date_time = models.DateTimeField(default = datetime.datetime.now())
    uploaded_by  = models.CharField(max_length=30)
    cost = models.FloatField(default = 0)
    revenue = models.FloatField(default = 0)
    percent_completed = models.FloatField(default = 0)
    worker_list = models.CharField(max_length=30, null = True)
    max_offers = models.FloatField(default = 5)
    csv_headers = models.CharField(max_length=2000, null = False)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True)


#Should I have a WorkerCSV table? Will that be able to show checkboxes on both
#a worker's page and a csv's page?
#How do I make object names in django admin plural form?
#What does null=True really mean if I still have to add something to the admin field?

    
class Owner(models.Model):
    name = models.CharField(max_length=30)
    daily_cap = models.FloatField(default = 0)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True)
    
    
    
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
    description = models.CharField(max_length = 100)


class Network(models.Model):
    name = models.CharField(max_length = 30)
    url = models.CharField(max_length = 100)
    description = models.CharField(max_length = 30)

 
class Advertiser(models.Model):
    name = models.CharField(max_length=30)
    daily_cap = models.FloatField(default = 25)
    status = models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30)
       
     
class LeadSourceOfferExclusion(models.Model):
    leadsource = models.ForeignKey(LeadSource)
    advertiser = models.ForeignKey(Advertiser)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null=True)


class Account(models.Model):
    network = models.ForeignKey(Network)
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
    description = models.CharField(max_length = 30, null=True)
   
    


    
class Offer(models.Model):
    Account = models.ForeignKey(Account)
    advertiser = models.ForeignKey(Advertiser)
    offer_num = models.CharField(max_length=10)
    daily_cap = models.FloatField(default = 10)
    url = models.CharField(max_length=200)
    payout = models.FloatField()
    min_epc = models.FloatField()
    max_epc = models.FloatField()
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null = True)
    
class IPSolution(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100, null = True)
    
class Worker(models.Model):
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    odesk_id = models.CharField(max_length=30)
    ip_solution = models.ForeignKey(IPSolution)
    now_online = models.BooleanField(default=False)
    status= models.CharField(max_length = 30, choices = STATUS_LIST)
    description = models.CharField(max_length = 30, null = True)
    


    
class Lead(models.Model):
    niche = models.ForeignKey(Niche)
    csv = models.ForeignKey(CSV)
    locked = models.BooleanField(default=False)
    started_on = models.DateTimeField(null = True)
    ended_on = models.DateTimeField(null = True)
    deleted = models.BooleanField(default=False)
    offers_requested = models.CharField(max_length=200, null = True)
    offers_completed = models.CharField(max_length=200, null = True)
    worker_id = models.CharField(max_length=10,null=True)
    lead_data = models.CharField(max_length=2000)
    ip_address = models.CharField(max_length=30, null = True)
    user_agent = models.CharField(max_length=100, null = True)
    subid = models.CharField(max_length=100, null = True)
    status= models.CharField(max_length = 30, choices = STATUS_LIST, null = True)
    description = models.CharField(max_length = 30, null = True)


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
    