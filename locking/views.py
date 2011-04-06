import simplejson

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from locking.decorators import user_may_change_model, is_lockable, log
from locking import utils, LOCK_TIMEOUT, logger, models
from rotator.models import Account, Network
"""
These views are called from javascript to open and close assets (objects), in order
to prevent concurrent editing.
"""

@login_required
def offer_save(request):
    try:
        request.session['account'] = request.GET['account']
        request.session['network'] = request.GET['network']
        request.session['advertiser'] = request.GET['advertiser']
        request.session['niche'] = request.GET['niche']
        return HttpResponse('1')
    except:
        return HttpResponse('0')
         

@login_required
def get_saved_offer(request):
    if 'account' not in request.session or 'network' not in request.session \
        or 'advertiser' not in request.session or 'niche' not in request.session:
        return HttpResponse('0')
    return HttpResponse(simplejson.dumps({
            'account': request.session['account'],
            'network': request.session['network'],
            'niche': request.session['niche'],
            'advertiser': request.session['advertiser']
        }), mimetype="application/json")

@login_required
def account_list(request):
    data = {}
    for network in Network.objects.all():        
        data[network.id] = []
        for account in network.accounts.all():
            data[network.id].append(account.id)
             
    return HttpResponse(simplejson.dumps(data), mimetype="application/json")
    
@log
@user_may_change_model
@is_lockable
def lock(request, app, model, id):
    obj = utils.gather_lockable_models()[app][model].objects.get(pk=id)

    try:
        obj.lock_for(request.user)
        obj.save()
        return HttpResponse(status=200)
    except models.ObjectLockedError:
        # The user tried to overwrite an existing lock by another user.
        # No can do, pal!
        return HttpResponse(status=403)

@log
@user_may_change_model
@is_lockable
def unlock(request, app, model, id):
    obj = utils.gather_lockable_models()[app][model].objects.get(pk=id)

    # Users who don't have exclusive access to an object anymore may still
    # request we unlock an object. This happens e.g. when a user navigates
    # away from an edit screen that's been open for very long.
    # When this happens, LockableModel.unlock_for will throw an exception, 
    # and we just ignore the request.
    # That way, any new lock that may since have been put in place by another 
    # user won't get accidentally overwritten.
    try:
        obj.unlock_for(request.user)
        obj.save()    
        return HttpResponse(status=200)
    except models.ObjectLockedError:
        return HttpResponse(status=403)

@log
@user_may_change_model
@is_lockable
def is_locked(request, app, model, id):    
    obj = utils.gather_lockable_models()[app][model].objects.get(pk=id)

    response = simplejson.dumps({
        "is_active": obj.is_locked,
        "for_user": getattr(obj.locked_by, 'username', None),
        "applies": obj.lock_applies_to(request.user),
        })
    return HttpResponse(response)

@log
def js_variables(request):
    response = "var locking = " + simplejson.dumps({
        'base_url': "/".join(request.path.split('/')[:-1]),
        'timeout': LOCK_TIMEOUT,
        })
    return HttpResponse(response)