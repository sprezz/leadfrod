# Create your views here.


def show_login():
    pass
def click_logout():
    pass

def dashboard():
    ''' The dashboard which gives a quick summary of important details '''
    pass


def show_lead():
    ''' This shows workers a lead along with some offers '''
    pass


def get_offers_for_lead():
    ''' This method pulls the right number of offers for each lead.
    It also calls each of the filtering functions in turn
    and returns just the filtered list of offers '''

#Pick next Lead
def get_lead(worker_id):
    ''' Use the worker's id to determine which lead to get.
    Returns a lead id and tuple list of headers and values'''
    #Select csvs that are allowed by this worker
    #select leads where active=true, completed=false locked=false, deleted=false from the csv ids above
    #set lock=true
    pass

def release_lead():
    #set completed = true
    #set lock=false
    pass


#FILTERS
def filter_active_offers():
    pass

def filter_daily_caps():
    pass

def filter_advertiser_exclusion():
    pass

def filter_duplicate_titles():
    pass

def filter_distinct_advertisers():
    pass




#something else

#Filter Order for Leads:
#SELECT LEADS WHERE 
#LEAD=ACTIVE
#UNLOCK = FALSE
#COMPLETED = FALSE
#CSV = ACTIVE
#LEADSOURCE = ACTIVE
#CSV.WORKER_LIST CONTAINS WORKER_ID



#Filter Order for Offers:
#REMOVE INACTIVE OFFERS [ OWNER, LLC, CSV, ACCOUNT, ADVERTISER, OFFER]
#REMOVE CAPPED [OWNER, LLC, ACCOUNT, ADVERTISER, OFFER]
#REMOVE LEADSOURCE-ADVERTISER EXCLUSION OFFERS
#SHOW DISTINCT TITLES
#SHOW DISTINCT ADVERTISERS
#LEADMAX LIMIT

