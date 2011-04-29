from django.core.management.base import BaseCommand, CommandError
from rotator.models import Account
from rotator.spyderhandler import *

import datetime


class Command(BaseCommand):
    
    def parse(self, account):
        loginurl = 'https://login.azoogleads.com/affiliate/'
        print "%s %s" % (account.user_id, account.password)
        
        
    def handle(self, *args, **options):   
        now = datetime.datetime.now()   
        print now 
        
        for account in Account.objects.filter(network__url='http://www.epicdirectnetwork.com/'):
            self.parse(account)            
  
        print "Finished."