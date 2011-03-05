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
    (r'^(static|media)/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    # Uncomment the admin/doc line below to enable admin documentation:
     (r'^admin/doc/', include('django.contrib.admindocs.urls')),
     (r'^accounts/login/$', 'django.contrib.auth.views.login'),
     (r'^next/?$', 'rotator.views.next_workitem'),
     (r'^submit/?$', 'rotator.views.submit_workitem'),
     (r'^logout/?$', 'rotator.views.click_logout'),
     (r'^dailycap/?$', 'rotator.views.manage_dailycap'),
     (r'^sentry/', include('sentry.urls')),
     
    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
     (r'^ajax/admin/', include('locking.urls')),
     
     (r'^csv/','view_csvs'),
     (r'^account/','view_csvs'),
     (r'^offer/','view_csvs'),
     (r'^advertiser/','view_csvs'),
     (r'^worker/','view_csvs'),
     (r'^showlead','show_lead'),
#     (r'', include('staticfiles.urls')),
     
)

#urlpatterns += staticfiles_urlpatterns()
