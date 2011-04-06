from django.core.management.base import BaseCommand, CommandError
import datetime
from BeautifulSoup import BeautifulSoup
from rotator.models import Account
from rotator.spyderhandler import GetAdsHandler, HydraHandler, \
    AffiliateComHandler, ACPAffiliatesHandler


class Command(BaseCommand):

    def handle(self, *args, **options):   
        now = datetime.datetime.now()   
        print now 
        networks = {
            "http://getads.com/": 'GetAdsHandler', 
            "http://affiliate.com/": 'AffiliateComHandler', 
            "https://network.hydranetwork.com/login": "HydraHandler",
            'http://acpaffiliates.com/Publishers': 'ACPAffiliatesHandler'
        }
        
        for account in Account.objects.all():
            if account.network.url in networks:
                account.checked()
                globals()[ networks[account.network.url] ](now, account).run()
  
        print "Finished."    
            
