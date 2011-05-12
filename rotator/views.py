from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.template import RequestContext

from datetime import timedelta, date

import logging
import simplejson
from models import *
from rotator.trafficholder import TrafficHolder
from trafficholder import UnknownOrderException
from spyderhandler import AzoogleHandler
from displayers import *
import random


#@login_required
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


def randomMessage():
    x = random.random()
    if x <= 0.04:
        message = "do NOT click thank you page"
    elif x <= 0.24:
        message = "Fill out the lead on the thank you page"
    else:
        message = "Click on the thank you page"
         
    return message

        
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
                if not wm.validateWorkItem(wi):
                    wi = wm.nextWorkItem(request.user)
                    request.session['workitem']=wi
                    request.session['msg']='Your previous work item was cancelled by administrator. Start with next.'
            logging.info('User %s: Found offers in views: %d' % (request.user, len(wi.offers)))
            TrafficHolder().processOffers ( wi.offers )
            msg = None
            if 'msg' in request.session:
                msg = request.session['msg']
                del request.session['msg']
            
            
                    
            return render_to_response('worker/showlead.html',
                    {
                        'randomMessage': randomMessage(),
                        'user':request.user,'wi':wi, 
                        'message':msg, 
                        'remaining_leads': wi.get_remaining_leads()
                    }, context_instance=RequestContext(request))
        except NoWorkException as exception:
            return render_to_response('worker/worker_goodbye.html', 
                                      {'user':request.user,
                                       'message': str(exception) 
                                       })
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
def admin_manage_dailycap(request):
    if request.method=='POST':
        for offer in Offer.objects.all():
            offer.restoreDailyCapCapacity()

    for offer in Offer.objects.all():
        offer.checkCapacity()

    return render_to_response("daily_capacity.html",
                              {'capacity':Capacity.objects.filter(date=datetime.date.today()).all()},
                              context_instance=RequestContext(request))


@permission_required('rotator.change_lead')
def admin_show_locked_leads(request):
    return render_to_response("locked_leads.html",
                              {'leads':Lead.locked.all().order_by('-_locked_at')},
                              context_instance=RequestContext(request))


@permission_required('rotator.change_lead')
def admin_release_lead(request):
    if request.method=='POST':
        lead_id = int(request.POST['lead_id'])
        wm = WorkManager.instance()
        wm.unlockLead(lead_id, request.user)
        return HttpResponseRedirect('/locked_leads')
    else:
        logging.warning('GET /release_lead when POST is expected' )


@permission_required('rotator.change_lead')
def admin_show_csvfiles(request):
    return render_to_response("csvfiles.html",
                              {'files':CSVFile.objects.all()},
                              context_instance=RequestContext(request))


@permission_required('rotator.change_lead')
def admin_delete_csvfile(request):
    print 'delete csv file', request.POST
    if request.method=='POST':
        try:
            csv_id = int(request.POST['csvfile_id'])
            print 'Delete csv', csv_id
            CSVFile.objects.only("id")
            print 'reducing selcetion to id'
            csv=CSVFile.objects.get(id=csv_id)
            print 'get csv', csv
            csv.delete()
            print 'deleted, remove defer'
            CSVFile.objects.defer(None)
            data={'code':'OK'}
        except Exception, msg:
            print 'Exception', msg
            data={'code':'NOK','message':msg}
        return HttpResponse(simplejson.dumps(data),mimetype='application/json')
    else:
        logging.warning('GET /delete_file when POST is expected' )


@permission_required('rotator.change_lead')
def admin_delete_csvfile_raw(request):
    print 'delete csv file', request.POST
    if request.method=='POST':
        try:
            csv_id = int(request.POST['csvfile_id'])
            from django.db import connection, transaction
            cursor = connection.cursor()

            # Data modifying operation - commit required
            cursor.execute("DELETE FROM rotator_lead WHERE csv_id = %s", [csv_id])
            cursor.execute("DELETE FROM rotator_csvfile_workers WHERE csvfile_id = %s", [csv_id])
            cursor.execute("DELETE FROM rotator_csvfile WHERE id = %s", [csv_id])
            transaction.commit_unless_managed()
            data={'code':'OK'}
        except Exception, msg:
            print 'Exception', msg
            data={'code':'NOK','message':msg}
        return HttpResponse(simplejson.dumps(data),mimetype='application/json')
    else:
        logging.warning('GET /delete_file when POST is expected' )


def trafficholder_callback(request, owner):
    if request.method=='GET':
        try:
            url = TrafficHolder().popOfferQueueUrl ( owner )
            if url:
                return HttpResponseRedirect ( url )
            else:
                logging.debug('Owner [%s] queue size is zero but url requested' % owner)
                return render_to_response('empty_queue.html')
        except UnknownOrderException:
            raise Http404


def azoogleAccounts(request):
    
    result = [ {'id': account.id, 'username': account.user_id, 'password': account.password} 
              for account in Account.objects.filter(
                        network__url='http://www.epicdirectnetwork.com/')]
    
    return HttpResponse(str(result))


def azoogleEarningsSave(request):
    return HttpResponse(str(AzoogleHandler(request.GET).run()))

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


def manualQueueCreate(request, template='manualQueueCreate.html'):
    message = ''
    if request.method == 'POST' and 'urls' in request.POST:
        urls = request.POST['urls'].split()
        if urls:
            for url in urls:
                existManualQueue = ManualQueue.objects.filter(url=url)
                if existManualQueue:
                    existManualQueue[0].size += 10
                    existManualQueue[0].save()
                else:    
                    ManualQueue(url=url).save()
            message = "URLs were saved successfully"
            
    return render_to_response(template, {'message': message },
        context_instance=RequestContext(request))


def manualQueueGo(request):
    mq = ManualQueue.objects.filter(size__gt=0).order_by('createdDate')
    if mq:
        mq[0].decreaseSize()
        return HttpResponseRedirect(mq[0].url)
    return HttpResponse('No url with size > 0')
    
def month_revenue(request, template="month_revenue.html"):
    d = date.today() - timedelta(days=31)
    totals = []
    days = []
    for i in range(0, 30):
        d += timedelta(days=1)
        total = Earnings.objects.filter(date__day=d.day, date__month=d.month, date__year=d.year).extra(
            select={'total': 'sum(revenue)'})[0].total            
        totals.append(float(total) if total else 0)
        days.append(d.strftime("%b'%d") if len(days) % 2 == 0 else " ")   

    return render_to_response(template, { 'datax': simplejson.dumps(totals), 'datay': simplejson.dumps(days) },
        context_instance=RequestContext(request))


def offer_changestatus(request, offer_id):
    try:
        offer = Offer.objects.get(id=offer_id)
        offer.status = request.POST['status']
        offer.save()
        return HttpResponse('1')
    except:
        return HttpResponse('0')


def spyder(request, site):    
    SITES = {
        'jumptap.com': JumptapDisplayer,
        'admob.com': AdmobDisplayer,
        'inmobi.com': InmobiDisplayer,
        'moolah-media.com': MoolahDisplayer, 
    }
    
    if site not in SITES:
        return Http404
    
    return HttpResponse(str(SITES[site](site).run()))
    
    
    
    
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

