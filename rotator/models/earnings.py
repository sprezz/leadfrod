# -*- coding:utf-8 -*-
import datetime
from django.db import models


class Earnings(models.Model):
    offer = models.ForeignKey('rotator.Offer')
    network = models.ForeignKey('rotator.Network')
    niche = models.ForeignKey('rotator.Niche')
    date = models.DateTimeField(default=datetime.datetime.now())
    campaign = models.CharField(max_length=255)
    status = models.CharField(max_length=255, null=True)
    payout = models.DecimalField(max_digits=5, decimal_places=2)
    impressions = models.IntegerField(null=True)
    clicks = models.IntegerField(null=True)
    qualified_transactions = models.IntegerField(null=True)
    aproved = models.IntegerField(null=True)
    CTR = models.FloatField(null=True)
    aprovedCTR = models.FloatField(null=True)
    eCPM = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    EPC = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    revenue = models.DecimalField(max_digits=5, decimal_places=2)

    def pps(self):
        return 0 if self.offer.submits_today == 0 else "%.2f" % (self.revenue / self.offer.submits_today)

    def mpps(self):
        return "%.2f" % ((self.revenue + self.payout) / (self.offer.submits_today + 1))

    def conv(self):
        if not self.payout or not self.clicks:
            return 0
        return "%.2f" % ((self.revenue / self.payout) / self.clicks)

    def account(self):
        return self.offer.account.username

    def offer_name(self):
        return self.offer.name

    def offer_num(self):
        return self.offer.offer_num

    def __unicode__(self):
        return '%s / %s / %s / %s' % (self.offer.name, self.offer.offer_num,
                                      self.offer.account.username, self.offer.network.name)
