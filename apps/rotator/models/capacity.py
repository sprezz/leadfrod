# -*- coding:utf-8 -*-
from django.db import models


class Capacity(models.Model):
    "Capacity of remaining daily cap values of corresponding objects. "
    date = models.DateField()
    offer = models.ForeignKey('rotator.Offer', related_name='dailycap_capacity')
    advertiser = models.ForeignKey('rotator.Advertiser', null=True, blank=True,
                                   related_name='dailycap_capacity')
    account = models.ForeignKey('rotator.Account', related_name='dailycap_capacity')
    owner = models.ForeignKey('rotator.Owner', related_name='dailycap_capacity')
    company = models.ForeignKey('rotator.Company', related_name='dailycap_capacity')

    def checkOfferCapacity(self, payout):
        if not self.offer.is_active():
            return False
        return payout <= self.offer.capacity

    def checkAdvertiserCapacity(self, payout):
        if not self.advertiser:
            return True
        if not self.advertiser.is_active():
            return False
        adv_account_cap = self.offer.getAdvertiserCapacity()
        return payout <= adv_account_cap.capacity

    def checkAccountCapacity(self, payout):
        if not self.account.is_active():
            return False
        return payout <= self.account.capacity

    def checkCompanyCapacity(self, payout):
        if not self.company.is_active():
            return False
        return payout <= self.company.capacity

    def checkOwnerCapacity(self, payout):
        if not self.owner.is_active():
            return False
        return payout <= self.owner.capacity

    def updateOfferCapacity(self, payout):
        self.offer.capacity -= payout
        self.offer.save()

    def updateAdvertiserCapacity(self, payout):
        if not self.offer.hasAdvertiser():
            return
        adv_account_cap = self.offer.getAdvertiserCapacity()
        adv_account_cap.capacity -= payout
        adv_account_cap.save()

    def updateAccountCapacity(self, payout):
        self.account.capacity -= payout
        self.account.save()

    def updateCompanyCapacity(self, payout):
        self.company.capacity -= payout
        self.company.save()

    def updateOwnerCapacity(self, payout):
        self.owner.capacity -= payout
        self.owner.save()

    def restoreOfferDailyCapCapacity(self):
        self.offer.capacity = self.offer.daily_cap
        self.offer.save()

    def restoreAdvertiserDailyCapCapacity(self):
        if not self.offer.hasAdvertiser():
            return
        self.advertiser.clearCapacityOfAllAccounts()

    def restoreAccountDailyCapCapacity(self):
        self.account.capacity = self.account.daily_cap
        self.account.save()

    def restoreCompanyDailyCapCapacity(self):
        self.company.capacity = self.company.daily_cap
        self.company.save()

    def restoreOwnerDailyCapCapacity(self):
        self.owner.capacity = self.owner.daily_cap
        self.owner.save()

    class Meta:
        verbose_name = 'Capacity'
        verbose_name_plural = 'Capacity instances'
        app_label = 'rotator'

    def __unicode__(self):
        if self.advertiser:
            advCapacity = self.advertiser.getAccountCapacity(self.offer.account)
            return u'%s %s OFR: %s ADV: %s ACC: %s OWN: %s COM: %s' % (self.date,
                                                                       self.offer,
                                                                       self.offer.capacity,
                                                                       advCapacity.capacity if advCapacity else 0,
                                                                       self.account.capacity,
                                                                       self.owner.capacity,
                                                                       self.company.capacity)
        else:
            return u'%s %s OFR: %s ACC: %s OWN: %s COM: %s' % (self.date,
                                                               self.offer,
                                                               self.offer.capacity,
                                                               self.account.capacity,
                                                               self.owner.capacity,
                                                               self.company.capacity)
