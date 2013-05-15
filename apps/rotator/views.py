from datetime import date, timedelta
import logging
from json import dumps
from django.conf import settings

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.db.models import Sum
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from rotator.displayers import InmobiDisplayer, MoolahDisplayer, AdmobDisplayer, JumptapDisplayer
from rotator.models import WorkInterceptedException, NoWorkException, WorkerProfileDoesNotExistException
from rotator.models.account import Account
from rotator.models.capacity import Capacity
from rotator.models.csv_file import CSVFile
from rotator.models.earnings import Earnings
from rotator.models.lead import Lead
from rotator.models.manual_queue import ManualQueue
from rotator.models.offer import Offer
from rotator.models.offer_queue import OfferQueue
from rotator.models.work_manager import WorkManager
from rotator.trafficholder import TrafficHolder, UnknownOrderException
from spyderhandler import AzoogleHandler


#@login_required
def index(request):
    return redirect('/next/')


@login_required
@require_http_methods(['POST'])
def submit_workitem(request):
    print 'submit_workitem'
    if request.method == 'POST':
        wm = WorkManager.instance()
        print request.POST['user_action']
        wi = request.session['workitem']
        del request.session['workitem']
        if request.POST['user_action'] == 'Next':
            try:
                wm.completeCurrentWorkItem(wi)
            except WorkInterceptedException, msg:
                logging.warning(msg)
            return redirect('/next')
        else:
            print 'Cancel job!'
            logging.info('User %s has canceled work item %s' % (request.user, wi))
            request.session['msg'] = 'Work item %s was canceled by %s' % (wi, request.user)
            wm.releaseCurrentWorkItem(wi)

            return redirect('/next')


@login_required
def next_workitem(request):
    """Responds with lead and appropriate offers"""
    logger = logging.getLogger('rotator.views.next_workitem')
    
    wm = WorkManager.instance()
    logger.info('wm instance %s' % wm)
    wi = None
    for attempt in range(1, 3):
        try:
            logger.info('Getting work item')
            if 'workitem' not in request.session:
                wi = wm.nextWorkItem(request.user)
                request.session['workitem'] = wi
            else:
                wi = request.session['workitem']
                if not wm.validateWorkItem(wi):
                    wi = wm.nextWorkItem(request.user)
                    request.session['workitem'] = wi
                    request.session['msg'] = 'Your previous work item was cancelled by administrator. Start with next.'
            logger.info('User %s: Found offers in views: %d' % (request.user, len(wi.offers)))
            if not settings.DEBUG:
                TrafficHolder().processOffers(wi.offers)
            msg = None
            if 'msg' in request.session:
                msg = request.session['msg']
                del request.session['msg']

            return render(request, 'worker/showlead.html',
                                      {
                                          'randomMessage': '',
                                          'user': request.user, 'wi': wi,
                                          'message': msg,
                                          'remaining_leads': wi.get_remaining_leads()
                                      })
        except NoWorkException as exception:
            return render(request, 'worker/worker_goodbye.html',
                                      {'user': request.user,
                                       'message': str(exception)
                                      })
        except WorkInterceptedException:
            logger.warning('User %s got intercepted work exception' % request.user)
            continue
        except WorkerProfileDoesNotExistException:
            logger.error('User %s got unrecoverable error in getting next work item' % request.user)
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
    logout(request)
    return redirect('/')


@permission_required('rotator.change_offer')
def admin_manage_dailycap(request, offerid=None):
    if request.method == 'POST':
        for offer in Offer.objects.all():
            offer.restoreDailyCapCapacity()
    elif offerid:  # Requested method was GET
        Offer.objects.get(id=offerid).restoreDailyCapCapacity()

    for offer in Offer.objects.all():
        offer.checkCapacity()

    return render(request, "daily_capacity.html",
                              {'capacity': Capacity.objects.filter(date=date.today()).all()})


@permission_required('rotator.change_lead')
def admin_show_locked_leads(request):
    return render(request, "locked_leads.html",
                              {'leads': Lead.locked.all().order_by('-_locked_at')})


@permission_required('rotator.change_lead')
@require_http_methods(['POST'])
def admin_release_lead(request):
    if request.method == 'POST':
        lead_id = int(request.POST['lead_id'])
        wm = WorkManager.instance()
        wm.unlockLead(lead_id, request.user)
        return redirect('/locked_leads')
    else:
        logging.warning('GET /release_lead when POST is expected')


@permission_required('rotator.change_lead')
def admin_show_csvfiles(request):
    return render(request, "csvfiles.html",
                              {'files': CSVFile.objects.all()})


@permission_required('rotator.change_lead')
def admin_delete_csvfile(request):
    if request.method == 'POST':
        csvfile_id = request.POST['csvfile_id']
        try:
            CSVFile.objects.get(id=csvfile_id).delete()
            data = {'code': 'OK'}
        except KeyError:
            data = {'code': 'NOK', 'message': 'csvfile_id is empty'}
        except (CSVFile.DoesNotExist, ValueError):
            data = {'code': 'NOK', 'message': 'CSV with id %s not found' % csvfile_id}
        return HttpResponse(dumps(data), mimetype='application/json')
    else:
        logging.warning('GET /delete_file when POST is expected')


@permission_required('rotator.change_lead')
@require_http_methods(['POST'])
def admin_delete_csvfile_raw(request):
    if request.method == 'POST':
        try:
            csv_id = int(request.POST['csvfile_id'])
            from django.db import connection, transaction

            cursor = connection.cursor()

            # Data modifying operation - commit required
            cursor.execute("DELETE FROM rotator_lead WHERE csv_id = %s", [csv_id])
            cursor.execute("DELETE FROM rotator_csvfile_workers WHERE csvfile_id = %s", [csv_id])
            cursor.execute("DELETE FROM rotator_csvfile WHERE id = %s", [csv_id])
            transaction.commit_unless_managed()
            data = {'code': 'OK'}
        except Exception, msg:
            print 'Exception', msg
            data = {'code': 'NOK', 'message': msg}
        return HttpResponse(dumps(data), mimetype='application/json')
    else:
        logging.warning('GET /delete_file when POST is expected')


def trafficholder_callback(request, owner):
    if request.method == 'GET':
        try:
            url = TrafficHolder().popOfferQueueUrl(owner)
            if url:
                return redirect(url)
            else:
                logging.debug('Owner [%s] queue size is zero but url requested' % owner)
                return render(request, 'empty_queue.html')
        except UnknownOrderException:
            raise Http404


def azoogleAccounts(request):
    result = [{'id': account.id, 'username': account.user_id, 'password': account.password}
              for account in Account.objects.filter(
            network__url='http://www.epicdirectnetwork.com/')]

    return HttpResponse(str(result))


def azoogleEarningsSave(request):
    return HttpResponse(str(AzoogleHandler(request.GET).run()))


def manualQueueCreate(request, template='manualQueueCreate.html'):
    message = ''
    urls = ''
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
    #urls = ''.join(ManualQueue.objects.all())
    #Force all objects to __unicode__ format with str()

    return render(request, template, {'message': message, 'urls':urls})


def manualQueueGo(request):
    mq = ManualQueue.objects.filter(size__gt=0).order_by('createdDate')
    if mq:
        mq[0].decreaseSize()
        return redirect(mq[0].url)
    return HttpResponse('No url with size > 0')


def showQueue(request):
    offer_queue_clicks = OfferQueue.objects.filter(size__gt=0)
    queue = [str(o) for o in offer_queue_clicks]
    offer_queue_clicks_count = offer_queue_clicks.aggregate(s=Sum('size'))['s']

    manual_queue_clicks = ManualQueue.objects.filter(size__gt=0)
    manual_queue = [str(o) for o in manual_queue_clicks]
    manual_queue_clicks_count = offer_queue_clicks.aggregate(s=Sum('size'))['s']
    return render(request, 'showqueue.html', {'queue': queue,
                                              'manual_queue': manual_queue,
                                              'offer_queue_clicks_count': offer_queue_clicks_count,
                                              'manual_queue_clicks_count': manual_queue_clicks_count})


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

    return render(request, template, {'datax': dumps(totals), 'datay': dumps(days)})


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

