from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.template import RequestContext
from django.views.decorators.http import require_http_methods


import urllib


import datetime
start = datetime.datetime.today().strftime('%m-%d-%y')
end = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%m-%d-%y')

post_data = {}
post_data['api_key'] = 'j46Yso7u60'
post_data['affiliate_id'] = '5111'

#Get daily summary
url = 'http://getoffersdirectnetwork.com/affiliates/api/4/reports.asmx/CampaignSummary'
post_data['start_date'] = start
post_data['end_date'] = end
post_data['sub_affiliate'] = ''
post_data['start_at_row'] = '1'
post_data['row_limit'] = '0'
post_data['sort_field'] = 'offer_id'
post_data['sort_descending'] = 'False'


def show_daily_summary(request):
    encoded_post_data = urllib.urlencode(post_data)
    data = urllib.urlopen(url, encoded_post_data).read()
    return HttpResponse(data)