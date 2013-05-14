from datetime import datetime, timedelta

from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from rotator.models import NoWorkException
from rotator.models.account import Account
from rotator.models.advertiser import Advertiser
from rotator.models.advertiser_account_capacity import AdvertiserAccountCapacity
from rotator.models.company import Company
from rotator.models.csv_file import CSVFile
from rotator.models.lead import Lead
from rotator.models.lead_source import LeadSource
from rotator.models.network import Network
from rotator.models.niche import Niche
from rotator.models.offer import Offer
from rotator.models.owner import Owner
from rotator.models.work_manager import WorkManager

from rotator.utils import TestCase


class AppTestCase(TestCase):
    fixtures = ['twooffers', ]
    apps = ('rotator', 'locking',)

    POT = 10
    OFR = 50
    ADV = 100
    ACC = 30
    COM = 500
    OWN = 1000

    def setUp(self):
        self.adv_offer, self.noadv_offer = Offer.objects.all()
        users = User.objects.all()
        self.user, self.alt_user = users
        self.today = datetime.today()
        self.adv_offer.initCapacity()
        self.adv_offer.restoreDailyCapCapacity()

        self.noadv_offer.initCapacity()
        self.noadv_offer.restoreDailyCapCapacity()
        self.niche = Niche.objects.get(pk=1)
        self.network = Network.objects.get(pk=1)
        self.account1 = Account.objects.get(pk=1)

        if self._testMethodName.startswith('test_WorkStrategy'):
            self.w1 = User.objects.get(username='w1')
            self.test_niche = Niche.objects.create(name='test', status='active')

            self.test_owner = Owner.objects.create(name='test_owner', status='active')

            self.test_company1 = Company.objects.create(name_list='test_com1', status='active', owner=self.test_owner)
            self.test_network1 = Network.objects.create(name='testnet1', status='active', url='www.testnetwork1.com')
            self.test_account_net11 = Account.objects.create(username='testnet1', network=self.test_network1, company=self.test_company1, status='active')
            self.test_account_net12 = Account.objects.create(username='testnet1_second', network=self.test_network1, company=self.test_company1, status='active', primary=False)

            self.test_company2 = Company.objects.create(name_list='test_com2', status='active', owner=self.test_owner)
            self.test_network2 = Network.objects.create(name='testnet2', status='active', url='www.testnetwork2.com')
            self.test_account_net21 = Account.objects.create(username='testnet2', network=self.test_network2, company=self.test_company2, status='active')
            self.test_account_net22 = Account.objects.create(username='testnet2_second', network=self.test_network2, company=self.test_company2, status='active', primary=False)

    # def test_offer_has_advertiser(self):
    #     print self.adv_offer, self.noadv_offer
    #     self.assertTrue(self.adv_offer.hasAdvertiser())
    #     self.assertFalse(self.noadv_offer.hasAdvertiser())
    #
    # def test_checkOfferCapacity(self):
    #     daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
    #     print 'test_checkOfferCapacity', self.adv_offer.capacity, self.adv_offer.payout
    #     self.assertTrue(daily_capacity.checkOfferCapacity(self.adv_offer.payout))
    # def test_checkAdvertiserCapacity(self):
    #     daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
    #     self.assertTrue(daily_capacity.checkAdvertiserCapacity(self.adv_offer.payout))
    # def test_checkAccountCapacity(self):
    #     daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
    #     self.assertTrue(daily_capacity.checkAccountCapacity(self.adv_offer.payout))
    # def test_checkCompanyCapacity(self):
    #     daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
    #     self.assertTrue(daily_capacity.checkCompanyCapacity(self.adv_offer.payout))
    # def test_checkOwnerCapacity(self):
    #     daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
    #     self.assertTrue(daily_capacity.checkOwnerCapacity(self.adv_offer.payout))
    #
    # def test_has_offer_capacity_with_advertiser(self):
    #     self.assertTrue(self.adv_offer.checkCapacity())
    # def test_has_offer_capacity_without_advertiser(self):
    #     self.assertTrue(self.noadv_offer.checkCapacity())
    #
    # def test_update_two_offer_nocapacity (self):
    #     daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
    #     daily_capacity.offer.daily_cap = 10
    #     daily_capacity.offer.payout = 10
    #     daily_capacity.offer.save()
    #     daily_capacity.advertiser.daily_cap = 11
    #     daily_capacity.advertiser.save()
    #     daily_capacity.account.daily_cap = 12
    #     daily_capacity.account.save()
    #     daily_capacity.company.daily_cap = 13
    #     daily_capacity.company.save()
    #
    #     daily_capacity.owner.daily_cap = 14
    #     daily_capacity.owner.save()
    #
    #     noadv_daily_capacity = self.noadv_offer.dailycap_capacity.get(date=self.today)
    #     noadv_daily_capacity.offer.daily_cap = 10
    #     noadv_daily_capacity.offer.payout = 10
    #     noadv_daily_capacity.offer.save()
    #
    #     self.adv_offer.restoreDailyCapCapacity()
    #     self.noadv_offer.restoreDailyCapCapacity()
    #
    #     self.assertTrue(self.adv_offer.checkCapacity())
    #     self.adv_offer.updateCapacity()
    #
    #     daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
    #
    #     print daily_capacity.account, daily_capacity.account.capacity
    #     print daily_capacity.company, daily_capacity.company.capacity
    #     print daily_capacity.owner, daily_capacity.owner.capacity
    #
    #     self.assertEquals(daily_capacity.account.capacity, 2)
    #     self.assertEquals(daily_capacity.company.capacity, 3)
    #     self.assertEquals(daily_capacity.owner.capacity, 4)
    #
    #     self.assertFalse(self.adv_offer.checkCapacity())
    #     self.assertFalse(self.noadv_offer.checkCapacity())
    #
    # def test_update_two_offer_capacity (self):
    #     daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
    #     daily_capacity.offer.daily_cap = 10
    #     daily_capacity.offer.payout = 10
    #     daily_capacity.offer.save()
    #     daily_capacity.advertiser.daily_cap = 11
    #     daily_capacity.advertiser.save()
    #     daily_capacity.account.daily_cap = 120
    #     daily_capacity.account.save()
    #     daily_capacity.company.daily_cap = 130
    #     daily_capacity.company.save()
    #     daily_capacity.owner.daily_cap = 140
    #     daily_capacity.owner.save()
    #
    #     noadv_daily_capacity = self.noadv_offer.dailycap_capacity.get(date=self.today)
    #     noadv_daily_capacity.offer.daily_cap = 10
    #     noadv_daily_capacity.offer.payout = 10
    #     noadv_daily_capacity.offer.save()
    #
    #     self.adv_offer.restoreDailyCapCapacity()
    #     self.noadv_offer.restoreDailyCapCapacity()
    #
    #     self.assertTrue(self.adv_offer.checkCapacity())
    #     self.adv_offer.updateCapacity()
    #
    #     daily_capacity = self.adv_offer.dailycap_capacity.get(date=self.today)
    #
    #     print daily_capacity.account, daily_capacity.account.capacity
    #     print daily_capacity.company, daily_capacity.company.capacity
    #     print daily_capacity.owner, daily_capacity.owner.capacity
    #
    #     self.assertEquals(daily_capacity.account.capacity, 110)
    #     self.assertEquals(daily_capacity.company.capacity, 120)
    #     self.assertEquals(daily_capacity.owner.capacity, 130)
    #
    #     self.assertFalse(self.adv_offer.checkCapacity())
    #     self.assertTrue(self.noadv_offer.checkCapacity())

    def createTestOffer(self, payout, offdc, account, network, adv=None):
        offer_num = '%d' % Offer.objects.count()
        offer = Offer(offer_num=offer_num,
                             network=network,
                             payout=payout,
                             url='www.offer%s.com' % offer_num,
                             daily_cap=offdc,
                             capacity=offdc,
                             status='active')
        if adv:
            offer.advertiser = adv

        offer.niche = self.test_niche
        offer.account = account
        offer.save()
        return offer

    def createTestCapacity(self, accdc, comdc, owndc):
        self.test_account_net11.daily_cap = accdc
        self.test_account_net11.capacity = accdc
        self.test_account_net11.save()

        self.test_account_net12.daily_cap = accdc
        self.test_account_net12.capacity = accdc
        self.test_account_net12.save()

        self.test_account_net21.daily_cap = accdc
        self.test_account_net21.capacity = accdc
        self.test_account_net21.save()

        self.test_account_net22.daily_cap = accdc
        self.test_account_net22.capacity = accdc
        self.test_account_net22.save()

        self.test_company1.daily_cap = comdc
        self.test_company1.capacity = comdc
        self.test_company1.save()

        self.test_company2.daily_cap = comdc
        self.test_company2.capacity = comdc
        self.test_company2.save()

        self.test_owner.daily_cap = owndc
        self.test_owner.capacity = owndc
        self.test_owner.save()

    def createAdvertiser(self, name, cap, account, adv=None):
        if not adv:
            adv = Advertiser.objects.create(name=name, daily_cap=cap, status='active')
        AdvertiserAccountCapacity.objects.create(advertiser=adv, account=account, capacity=cap)
        return adv

    def test_WorkStrategy(self):

        user_test1 = User.objects.create_user('test1', 'test1@test.com', 'test1')
        user_test2 = User.objects.create_user('test2', 'test2@test.com', 'test2')

        advA = self.createAdvertiser('AdvertiserA', self.ADV, self.test_account_net11)

        advB = self.createAdvertiser('AdvertiserB', self.ADV, self.test_account_net21)

        advC = self.createAdvertiser('AdvertiserC', self.ADV, self.test_account_net11)
        self.createAdvertiser('AdvertiserC', self.ADV, self.test_account_net21, advC)

        self.createTestCapacity(self.ACC, self.COM, self.OWN)

        # create offers for network1
        net1_offers = []
        for n in range(1, 10):
            if n % 2:
                offer = self.createTestOffer(self.POT, self.OFR, self.test_account_net11, self.test_network1)
                if n in (1, 5, 9):
                    offer.advertiser = advA
                elif n == 3:
                    offer.advertiser = advC
            else:
                offer = self.createTestOffer(self.POT, self.OFR, self.test_account_net12, self.test_network1)
            offer.save()
            net1_offers.append(offer)

            # create offers for network2
        net2_offers = []
        for n in range(1, 10):
            if n % 2:
                offer = self.createTestOffer(self.POT, self.OFR, self.test_account_net21, self.test_network2)
                if n in (1, 5, 9):
                    offer.advertiser = advB
                elif n == 3:
                    offer.advertiser = advC
            else:
                offer = self.createTestOffer(self.POT, self.OFR, self.test_account_net22, self.test_network2)
            offer.save()
            net2_offers.append(offer)

        ls = LeadSource.objects.get(pk=1)
        test_csv1 = CSVFile.objects.create(niche=self.test_niche, csv_headers="a,b,c", lead_source=ls, filename='test1.csv', uploaded_by='test_user', status='active')
        for n in range(1, 10):
            lead = Lead(csv=test_csv1, status='active', lead_data='a%d,b%d,c%s' % (n, n, n))
            lead.save()

        test_csv2 = CSVFile.objects.create(niche=self.test_niche, csv_headers="x,y,z", lead_source=ls, filename='test1.csv', uploaded_by='test_user', status='active')
        for n in range(1, 10):
            lead = Lead(csv=test_csv2, status='active', lead_data='x%d,y%d,z%s' % (n, n, n))
            lead.save()

        print 'DATA POPULATED'
        wm = WorkManager.instance()
        wm.workers_online.remove(self.w1) # hack: w1 was inherited from initiaL FIXTURE. we don't need it for this test
        wm.save()

        wm.checkOrCreateUserProfile(user_test1)
        wm.checkOrCreateUserProfile(user_test2)
        wm.signIn(user_test1)
        wm.signIn(user_test2)

        self.assertTrue(user_test1.get_profile().now_online)
        self.assertTrue(user_test2.get_profile().now_online)
        self.assertEquals(wm.getNumberOfOnlineWorkers, 2)

        try:
            # user_test1 is not added to CSV file, so expected NoWorkException
            workItem1 = wm.nextWorkItem(user_test1)
            self.assertTrue(False)
        except NoWorkException:
            test_csv1.workers.add(user_test1)
            test_csv1.workers.add(user_test2)
            test_csv1.save()
            test_csv2.workers.add(user_test1)
            test_csv2.save()
            test_csv1.status = 'disabled'
            test_csv1.save()
            workItem1 = wm.nextWorkItem(user_test1)

        self.assertEquals(len(workItem1.offers), 5)
        self.assertTrue(workItem1.lead.is_locked)
        self.assertEquals(workItem1.lead.locked_by, user_test1)

        try:
            # user_test2 is not added to test_csv2 file, but it is added to test_csv1 so we DONT  expect NoWorkException
            workItem2 = wm.nextWorkItem(user_test2)
            test_csv2.workers.add(user_test2)
            test_csv2.save()
            workItem2 = wm.nextWorkItem(user_test2)
        except NoWorkException:
            self.assertTrue(False)

        #        self.assertEquals(len(workItem2.offers), 5)
        self.assertTrue(workItem2.lead.is_locked)
        self.assertEquals(workItem2.lead.locked_by, user_test2)

        # Cancel work on items
        wm.releaseCurrentWorkItem(workItem1)
        print workItem1.lead.locked_by, workItem1.lead.locked_at
        self.assertFalse(workItem1.lead.is_locked)
        self.assertEquals(workItem1.lead.locked_by, None)
        self.assertEquals(workItem1.lead.worker, None)

        wm.releaseCurrentWorkItem(workItem2)
        self.assertFalse(workItem2.lead.is_locked)
        self.assertEquals(workItem2.lead.locked_by, None)
        self.assertEquals(workItem2.lead.worker, None)

        test_csv1.status = 'enabled'
        test_csv1.save()

        # Disable second CSV 
        test_csv2.status = 'disabled'
        test_csv2.save()

        # Two users get next lead and 5 offers and complete them
        # one account have 100 cap, so it can afford 10 offer shows (for payout 10)
        print 'Two users pick up work from one file'
        self.createTestCapacity(self.ACC, self.COM, self.OWN)
        acc_hash = {}
        while True:
            try:
                user1_wi = wm.nextWorkItem(user_test1)
                requested = user1_wi.lead.offers_requested.count()
                for offer in user1_wi.offers:
                    if offer.account not in acc_hash:
                        acc_hash[offer.account] = []
                    acc_hash[offer.account].append(offer)

                wm.completeCurrentWorkItem(user1_wi)
                self.assertEquals(user1_wi.lead.offers_completed.count(), requested)

                user2_wi = wm.nextWorkItem(user_test2)
                requested = user2_wi.lead.offers_requested.count()

                for offer in user2_wi.offers:
                    if offer.account not in acc_hash:
                        acc_hash[offer.account] = []
                    acc_hash[offer.account].append(offer)
                wm.completeCurrentWorkItem(user2_wi)
                self.assertEquals(user2_wi.lead.offers_completed.count(), requested)

            except NoWorkException:
                break

        for account, offers in acc_hash.items():
            account = Account.objects.get(pk=account.pk)
            print account
            for offer in offers:
                print '** ', offer.get_capacity_today
