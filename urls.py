from django.conf.urls.defaults import *
#from staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin


admin.autodiscover()
import settings


urlpatterns = patterns('',
                       # Example:
                       # (r'^leap/', include('leap.foo.urls')),
                       (r'^$', 'rotator.views.index'),
                       (r'^(static|media)/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': settings.MEDIA_ROOT}),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       (r'^accounts/login/$', 'django.contrib.auth.views.login'),
                       url(r'^next/?$', 'rotator.views.next_workitem', name='next_workitem'),
                       (r'^submit/?$', 'rotator.views.submit_workitem'),
                       (r'^logout/?$', 'rotator.views.click_logout'),
                       (r'^dailycap/?$', 'rotator.views.admin_manage_dailycap'),
                       (r'^release/?$', 'rotator.views.admin_release_lead'),
                       (r'^locked_leads/?$', 'rotator.views.admin_show_locked_leads'),
                       (r'^delete_file$', 'rotator.views.admin_delete_csvfile_raw'),
                       (r'^files/?$', 'rotator.views.admin_show_csvfiles'),
                       (r'^th/(?P<owner>.+)/?$', 'rotator.views.trafficholder_callback'),
                       (r'^revenue/month/$', 'rotator.views.month_revenue'),
                       (r'^manualqueue/create/$', 'rotator.views.manualQueueCreate'),
                       (r'^manualqueue/go/$', 'rotator.views.manualQueueGo'),
                       (r'^showqueue/$', 'rotator.views.showQueue'),
                       (r'^azoogle/accounts/$', 'rotator.views.azoogleAccounts'),
                       (r'^azoogle/earnings/save/$', 'rotator.views.azoogleEarningsSave'),

                       (r'^spyder/(?P<site>.+)?$', 'rotator.views.spyder'),

                       url(r'^offer/(?P<offer_id>\d+)/changestatus/', 'rotator.views.offer_changestatus', name="changeOfferStatus"),
                       # Uncomment the next line to enable the admin:
                       (r'^admin/', include(admin.site.urls)),
                       (r'^ajax/admin/', include('locking.urls')),


)

#urlpatterns += staticfiles_urlpatterns()
