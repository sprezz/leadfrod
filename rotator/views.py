from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404


from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext

import logging

from models import *

@login_required
def index(request):
    return HttpResponseRedirect('/next')

@login_required
def submit_workitem(request):
    print 'submit_workitem'
    if request.method=='POST':
        wm = WorkManager.instance()
        print request.POST['user_action']
        wi = request.session['workitem']
        del request.session['workitem']
        if request.POST['user_action']=='Next':
            try:
                wm.completeCurrentWorkItem(wi)
            except WorkInterceptedException, msg:
                logging.warning(msg)
            return HttpResponseRedirect('/next') 
        else:
            print 'Cancel job!'
            logging.info('User %s has canceled work item %s' % (request.user, wi))
            request.session['msg']='Work item %s was canceled by %s'% (wi, request.user)
            wm.releaseCurrentWorkItem(wi)
            
            return HttpResponseRedirect('/next')

@login_required
def next_workitem(request):
    "Responds with lead and appropriate offers"
    wm = WorkManager.instance()
    print 'wm instance', wm
    wm.checkOrCreateUserProfile(request.user)
    if not request.user.get_profile().now_online:
        print 'setting ',request.user,' online'
        wm.signIn(request.user)
    wi = None    
    for attempt in range(1,3):    
        try:    
            print 'Getting work item'
            if 'workitem' not in request.session: 
                wi = wm.nextWorkItem(request.user)
                request.session['workitem']=wi
            else:
                wi = request.session['workitem']
            msg = None    
            if 'msg' in request.session:
                msg = request.session['msg']
                del request.session['msg']   
            return render_to_response('worker/showlead.html', 
                                      {'user':request.user,'wi':wi, 'message':msg},
                                      context_instance=RequestContext(request))
        except NoWorkException:
            return render_to_response('worker/worker_goodbye.html', {'user':request.user})
        except WorkInterceptedException:
            logging.warning('User %s got intercepted work exception' % request.user)
            continue
        except WorkerProfileDoesNotExistException:
            logging.error('User %s got unrecoverable error in getting next work item' % request.user)
            raise Http404
    

def click_logout(request):
    wm = WorkManager.instance()
    if 'workitem' in request.session:
        wi = request.session['workitem']
        del request.session['workitem']
        wm.releaseCurrentWorkItem(wi)
    try:    
        wm.signOut(request.user)
    except Exception, msg:
        logging.error(msg)    
    logout( request )
    return HttpResponseRedirect('/')

@permission_required('rotator.change_offer')
def manage_dailycap(request):
    if request.method=='POST':
        for offer in Offer.objects.all():
            offer.restoreDailyCapCapacity()

    for offer in Offer.objects.all():
        offer.checkCapacity()
        
    return render_to_response("daily_capacity.html", 
                              {'capacity':Capacity.objects.filter(date=datetime.date.today()).all()},
                              context_instance=RequestContext(request))    


# Original functions
def show_login():
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

