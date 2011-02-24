from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^leap/', include('leap.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
     (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
     (r'^$','dashboard')
     (r'^csv/','view_csvs')
     (r'^account/','view_csvs')
     (r'^offer/','view_csvs')
     (r'^advertiser/','view_csvs')
     (r'^worker/','view_csvs')
     (r'^showlead','show_lead')
     
)
