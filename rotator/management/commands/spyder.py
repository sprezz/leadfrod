
from django.core.management.base import BaseCommand, CommandError
import datetime
from BeautifulSoup import BeautifulSoup
from rotator.models import Account
from rotator.spyderhandler import *

from rotator.models import Network
from rotator import spyder_objects
from string import capitalize

class Command(BaseCommand):

    def handle(self, *args, **options):   
        now = datetime.datetime.now()   
        print now 
        networks = {            
            "http://getads.com/": GetAdsHandler, 
            "http://affiliate.com/": AffiliateComHandler, 
            "https://network.hydranetwork.com/login": HydraHandler,
            'http://acpaffiliates.com/Publishers': ACPAffiliatesHandler,
            'http://www.c2mtrax.com/': APIHandler,
            'http://www.ecoretrax.com/': APIHandler,
            #'http://www.ads4dough.com/': Ads4DoughHandler,
            'https://adscendmedia.com/': AdscendHandler,
            'http://www.epicdirectnetwork.com/': AzoogleHandler,
            'http://emt.copeac.com/forms/login.aspx': CopeacHandler,
        }
        
        for account in Account.objects.all():
            if account.network.url in networks:                
                if(networks[account.network.url](now, account).run()):
                    account.checked()
  
        print "Finished."