import datetime
import time

from django.core.management.base import BaseCommand, CommandError

from rotator.models.account import Account
from rotator.spyderhandler import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_time = time.time()
        now = datetime.datetime.now()
        print now
        networks = {
            "http://publisher.getads.com/Welcome/LogInAndSignUp.aspx": GetAdsHandler,
            "http://affiliate.com/": AffiliateComHandler,
            "https://network.hydranetwork.com/login": HydraHandler,
            'http://acpaffiliates.com/Publishers': ACPAffiliatesHandler, #
            'http://www.c2mtrax.com/': APIHandler,
            'http://www.ecoretrax.com/': APIHandler, #
            'http://www.freshadsaffiliates.com/': APIHandler,
            'http://www.ads4dough.com/': Ads4DoughHandler,
            'https://adscendmedia.com/': AdscendHandler, #
            'http://emt.copeac.com/forms/login.aspx': CopeacHandler, #
            'http://affiliate.cpaflash.com/Welcome/LogInAndSignUp.aspx': CPAFlashHandler,
            'http://affiliate.triadmedia.com/Welcome/LogInAndSignUp.aspx': TriadMediahandler,
            'http://affiliate.glbtracker.com/index.php?pgid=': GlobalizerHandler,
            'http://www.adangler.com/login.php': AdAnglerHandler, #
            'https://publishers.clickbooth.com/': ClickBoothHandler,
            'http://affiliates.3cpa.com/': ThreeCPAHandler, #
            'http://affiliates.theedunetwork.com/': EduHandler,
            'http://www.cxdigitalmedia.com/agents/login/sign_in': CXDigitalHandler,
            'http://yeahcpa.hasoffers.com/': YeahCPAHandler,
            'http://publishers.vancead.com/': VanceadHandler, #
            'http://affiliate.gooffers.net/': GoOffersHandler, #
            'http://affiliate.tvmtracker.com/index.php': TrouveMediaHandler,
        }

        #networks = { "https://network.hydranetwork.com/login": HydraHandler, }

        for account in Account.objects.all():
            if account.network.url in networks:
                current_spyder = networks[account.network.url](account)
                if (current_spyder.run()):
                    account.checked()
                    account.setRevenue(current_spyder.revenue)
                else:
                    account.setRevenue(None)
        print "Finished. Done in %d seconds" % (time.time() - start_time)
