from django.core.management.base import BaseCommand, CommandError
from rotator.models import Account
from rotator.spyderhandler import *

import datetime
import time

class Command(BaseCommand):

    def handle(self, *args, **options): 
        start_time = time.time()  
        now = datetime.datetime.now()   
        print now 
        networks = {                   
            "http://getads.com/": GetAdsHandler, 
            "http://affiliate.com/": AffiliateComHandler, 
            "https://network.hydranetwork.com/login": HydraHandler,
            'http://acpaffiliates.com/Publishers': ACPAffiliatesHandler,
            'http://www.c2mtrax.com/': APIHandler,
            'http://www.ecoretrax.com/': APIHandler,
            'http://www.ads4dough.com/': Ads4DoughHandler,
            'https://adscendmedia.com/': AdscendHandler,
            'http://emt.copeac.com/forms/login.aspx': CopeacHandler,
            'http://affiliate.cpaflash.com/Welcome/LogInAndSignUp.aspx': CPAFlashHandler,
            'http://affiliate.triadmedia.com/Welcome/LogInAndSignUp.aspx': TriadMediahandler,
            'http://www.globalizernetwork.com': GlobalizerHandler,
        }
        #networks = {'http://www.globalizernetwork.com': GlobalizerHandler, }
        for account in Account.objects.all():
            if account.network.url in networks:  
                current_spyder = networks[account.network.url](now, account)              
                if(current_spyder.run()):
                    account.checked()
                    account.setRevenue(current_spyder.revenue)
                else:
                    account.setRevenue(None)
        print "Finished. Done in %d seconds" % (time.time() - start_time)