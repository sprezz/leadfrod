from django.db import models
import datetime

# Create your models here.
#VERSION 2

status_list = ['active','banned','paused']


class Status:
    status
    
class Owner:
    name
    status = 'ok'
    daily_cap
    
class LLC:
    name_list
    address
    city
    state
    zip
    county
    country
    type = 'corporation'
    w9_file
    im_list
    email_list
    phone_list
    status
    daily_cap
    
class Tracker:
    name
    
class Network:
    name
    url
    tracker
    
class Account:
    network
    username
    password
    display_name
    user_id
    AM
    phone
    AM_email
    status
    recieved_check_once
    payments_via
    last_payment_date
    payment_frequency
    daily_cap

class Advertiser:
    name = 'None'
    daily_cap
    status
    
class Offer:
    status
    network
    advertiser
    offer_num
    daily_cap
    url
    payout
    min_epc
    max_epc
    conv_p
    
class IPSolution:
    name
    
class Worker:
    name
    odesk_id
    ip_solution
    status
    now_online

class Niche:
    name
    min_epc
    max_epc
    conv_p
    status

class CSV:
    filename
    date_time
    num_leads
    uploaded_by
    niche
    cost
    revenue
    percent_completed
    worker_list = []
    status
    max_offers
    csv_headers = []

class Lead:
    niche
    csv
    locked
    started_on
    started_by
    ended_on
    deleted
    offers_requested = []
    offers_completed = []
    max_offers
    worker_id
    offer_list
    lead_data = []

class EPCStats:
    Account
    Offer
    date_time
    clicks
    leads
    conversion
    epc
    revenue
    status = ['ok','capped']
    action = ['less clicks', 'more clicks']

class Alert:
    Owner
    LLC
    Account
    Offer
    message = '5 submits sent but no stats yet!'
    messgage2='5 submits and PPL < 0.20'
    status = ['unread','fixed','ignored']