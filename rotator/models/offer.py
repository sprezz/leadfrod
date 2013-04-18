# -*- coding:utf-8 -*-
import datetime

from django.db import models

from rotator.models import STATUS_LIST, ACTIVE


class OfferManager(models.Manager):
    def clear_submits_today(self):
        print "clear submits today"
        self.filter(submits_today__gte=0).update(submits_today=0)


class Offer(models.Model):
    objects = OfferManager()

    name = models.CharField(max_length=255, null=True, blank=True)
    advertiser = models.ForeignKey('rotator.Advertiser', related_name='offers', null=True, blank=True)
    network = models.ForeignKey('rotator.Network', related_name='offers')
    account = models.ForeignKey('rotator.Account', related_name='offers')
    niche = models.ForeignKey('rotator.Niche', related_name='offers')

    # Each offer may have an advertiser associated with it.
    offer_num = models.CharField(max_length=10, null=True, blank=True)
    daily_cap = models.FloatField(default=10)
    capacity = models.FloatField(default=10)
    url = models.URLField(max_length=2000, verify_exists=False)
    payout = models.FloatField()
    min_clicks = models.FloatField(null=True, blank=True, default=5.0)
    max_clicks = models.FloatField(null=True, blank=True, default=15.0)
    status = models.CharField(max_length=30, choices=STATUS_LIST,
                              default=ACTIVE)
    description = models.CharField(max_length=255, null=True, blank=True)
    submits_today = models.IntegerField(default=0)
    submits_total = models.IntegerField(default=0)

    def conv(self):
        from rotator.models.earnings import Earnings
        today = datetime.date.today()
        earnings = Earnings.objects.filter(offer=self, date__month=today.month,
                                           date__day=today.day, date__year=today.year)
        if not earnings:
            return 0
        return earnings[0].conv()

    def size(self):
        queues = self.queues.all()
        return queues[0].size if queues else 0

    def asd(self):
        print self.description
        print self.id, self.offer_num
        return self.description

    def reduce_capacity(self):
        self.capacity -= self.payout
        if self.capacity < 0:
            self.capacity = 0
        self.save()

    def increase_submits(self):
        self.submits_today += 1
        self.submits_total += 1
        self.save()

    def is_active(self):
        return self.status == ACTIVE

    def hasAdvertiser(self):
        "Checks if this offer already has an advertiser"
        return self.advertiser is not None

    def owner_name(self):
        return self.account.company.owner.name

    owner_name.short_description = 'owner'

    def getAdvertiserCapacity(self):
        if not self.hasAdvertiser():
            return None
        return self.getAdvertiser().getAccountCapacity(self.account)

    def getAdvertiser(self):
        if not self.hasAdvertiser():
            return None
        if not self.advertiser.getAccountCapacity(self.account):
            from rotator.models.advertiser_account_capacity import AdvertiserAccountCapacity

            AdvertiserAccountCapacity.objects.create(
                advertiser=self.advertiser,
                account=self.account,
                capacity=self.advertiser.daily_cap)
        return self.advertiser

    def _checkOfferAdvertiserCapacity(self):
        if not self.hasAdvertiser():
            return
        if not self.advertiser.getAccountCapacity(self.account):
            from rotator.models.advertiser_account_capacity import AdvertiserAccountCapacity

            AdvertiserAccountCapacity.objects.create(
                advertiser=self.advertiser,
                account=self.account,
                capacity=self.advertiser.daily_cap)

    def initCapacity(self):
    #        print 'Create new capacity for ', self
        today = datetime.date.today()

        from rotator.models.capacity import Capacity

        if Capacity.objects.filter(date=today, offer=self).count() > 0:
            return
        capacity = Capacity(date=today, offer=self)
        capacity.account = self.account
        if self.hasAdvertiser():
            capacity.advertiser = self.advertiser
        capacity.company = self.account.company
        capacity.owner = self.account.company.owner
        capacity.save()

    @property
    def get_capacity_today(self):
        "Gets capacity object for today. If one does not exists, creates it"
        today = datetime.date.today()
        if not self.dailycap_capacity.filter(date=today).exists():
            self.initCapacity()
        return self.dailycap_capacity.filter(date=today)[0]

    def checkCapacity(self):
        "Checks if offer have enough budget to be selected"
        daily_capacity = self.get_capacity_today
        if not daily_capacity.checkOfferCapacity(self.payout):
        #            print 'run out of offer capacity', daily_capacity.offer
            return False
        if self.hasAdvertiser():
            if not daily_capacity.checkAdvertiserCapacity(self.payout):
            #                print "run out of advertiser's offer capacity with ", self.account
                return False
        if not daily_capacity.checkAccountCapacity(self.payout):
        #            print 'run out of account capacity', daily_capacity.account
            return False
        if not daily_capacity.checkCompanyCapacity(self.payout):
        #            print 'run out of company capacity', daily_capacity.company
            return False
        if not daily_capacity.checkOwnerCapacity(self.payout):
        #            print 'run out of owner capacity', daily_capacity.owner
            return False

        return True

    def reduceCapacityOnShow(self):
        "Reduces capacity capacity = capacity - self.payout"
        daily_capacity = self.get_capacity_today
        daily_capacity.updateOfferCapacity(self.payout)
        if self.hasAdvertiser():
            daily_capacity.updateAdvertiserCapacity(self.payout)
        daily_capacity.updateAccountCapacity(self.payout)
        daily_capacity.updateCompanyCapacity(self.payout)
        daily_capacity.updateOwnerCapacity(self.payout)
        daily_capacity.save()

    def restoreDailyCapCapacity(self):
        "Reset capacity to dailycap value"
        now = datetime.datetime.now()
        print "%s: Reset capacity for offer num = %s" % (now, self.offer_num)
        daily_capacity = self.get_capacity_today
        daily_capacity.restoreOfferDailyCapCapacity()
        if self.hasAdvertiser():
            daily_capacity.restoreAdvertiserDailyCapCapacity()
        daily_capacity.restoreAccountDailyCapCapacity()
        daily_capacity.restoreCompanyDailyCapCapacity()
        daily_capacity.restoreOwnerDailyCapCapacity()
        daily_capacity.save()

    def save(self, *args, **kwargs):
        super(Offer, self).save(*args, **kwargs)
        self._checkOfferAdvertiserCapacity()

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'
        unique_together = ("offer_num", "account")
        app_label = 'rotator'

    def __unicode__(self):
        name = self.offer_num
        if self.name:
            name = '%s %s' % (self.name, self.offer_num)
        return u'Offer %s at %s payout: %s capacity: %s/%s' % (name, self.url, self.payout, self.capacity, self.daily_cap)
