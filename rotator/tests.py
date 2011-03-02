from datetime import datetime, timedelta
import simplejson

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import User

from rotator import models, views
from rotator.utils import TestCase

class AppTestCase(TestCase):
    fixtures = ['twooffers',]
    apps=('rotator','locking',)

    def setUp(self):
        self.adv_offer, self.noadv_offer = models.Offer.objects.all()
        users = User.objects.all()
        self.user, self.alt_user = users
        self.today = datetime.today()
        self.adv_offer.initCapacity()
        self.adv_offer.clearCapacity()
        
        self.noadv_offer.initCapacity()
        self.noadv_offer.clearCapacity()
    def test_offer_has_advertiser(self):
        print self.adv_offer, self.noadv_offer
        self.assertTrue(self.adv_offer.hasAdvertiser())
        self.assertFalse(self.noadv_offer.hasAdvertiser())
    
    def test_checkOfferCapacity(self):
        daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
        print 'test_checkOfferCapacity', self.adv_offer.capacity, self.adv_offer.payout
        self.assertTrue(daily_capacity.checkOfferCapacity(self.adv_offer.payout))
    def test_checkAdvertiserCapacity(self):
        daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
        self.assertTrue(daily_capacity.checkAdvertiserCapacity(self.adv_offer.payout))
    def test_checkAccountCapacity(self):
        daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
        self.assertTrue(daily_capacity.checkAccountCapacity(self.adv_offer.payout))
    def test_checkCompanyCapacity(self):
        daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
        self.assertTrue(daily_capacity.checkCompanyCapacity(self.adv_offer.payout))
    def test_checkOwnerCapacity(self):
        daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
        self.assertTrue(daily_capacity.checkOwnerCapacity(self.adv_offer.payout))                 
        
    def test_has_offer_capacity_with_advertiser(self):
        self.assertTrue(self.adv_offer.checkCapacity())    
    def test_has_offer_capacity_without_advertiser(self):
        self.assertTrue(self.noadv_offer.checkCapacity())
        
    def test_update_two_offer_nocapacity (self):
        daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
        daily_capacity.offer.daily_cap = 10
        daily_capacity.offer.payout = 10
        daily_capacity.offer.save()
        daily_capacity.advertiser.daily_cap = 11
        daily_capacity.advertiser.save() 
        daily_capacity.account.daily_cap = 12
        daily_capacity.account.save()
        daily_capacity.company.daily_cap = 13
        daily_capacity.company.save()
        
        daily_capacity.owner.daily_cap = 14
        daily_capacity.owner.save()
        
        noadv_daily_capacity = self.noadv_offer.dailycap_capacity.get(date=self.today)
        noadv_daily_capacity.offer.daily_cap = 10
        noadv_daily_capacity.offer.payout = 10
        noadv_daily_capacity.offer.save()
        
        self.adv_offer.clearCapacity()
        self.noadv_offer.clearCapacity()
        
        self.assertTrue(self.adv_offer.checkCapacity())
        self.adv_offer.updateCapacity()
        
        daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
        
        print daily_capacity.account, daily_capacity.account.capacity
        print daily_capacity.company, daily_capacity.company.capacity
        print daily_capacity.owner, daily_capacity.owner.capacity
        
        self.assertEquals(daily_capacity.account.capacity, 2)
        self.assertEquals(daily_capacity.company.capacity, 3)
        self.assertEquals(daily_capacity.owner.capacity, 4)
        
        self.assertFalse(self.adv_offer.checkCapacity())
        self.assertFalse(self.noadv_offer.checkCapacity())
        
    def test_update_two_offer_capacity (self):
        daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
        daily_capacity.offer.daily_cap = 10
        daily_capacity.offer.payout = 10
        daily_capacity.offer.save()
        daily_capacity.advertiser.daily_cap = 11
        daily_capacity.advertiser.save() 
        daily_capacity.account.daily_cap = 120
        daily_capacity.account.save()
        daily_capacity.company.daily_cap = 130
        daily_capacity.company.save()
        daily_capacity.owner.daily_cap = 140
        daily_capacity.owner.save()
        
        noadv_daily_capacity = self.noadv_offer.dailycap_capacity.get(date=self.today)
        noadv_daily_capacity.offer.daily_cap = 10
        noadv_daily_capacity.offer.payout = 10
        noadv_daily_capacity.offer.save()
        
        self.adv_offer.clearCapacity()
        self.noadv_offer.clearCapacity()
        
        self.assertTrue(self.adv_offer.checkCapacity())
        self.adv_offer.updateCapacity()
        
        daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
        
        print daily_capacity.account, daily_capacity.account.capacity
        print daily_capacity.company, daily_capacity.company.capacity
        print daily_capacity.owner, daily_capacity.owner.capacity
        
        self.assertEquals(daily_capacity.account.capacity, 110)
        self.assertEquals(daily_capacity.company.capacity, 120)
        self.assertEquals(daily_capacity.owner.capacity, 130)
        
        self.assertFalse(self.adv_offer.checkCapacity())
        self.assertTrue(self.noadv_offer.checkCapacity())    
