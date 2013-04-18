# -*- coding:utf-8 -*-
import logging
from django.db import models
from rotator.models import ACTIVE


class OfferQueue(models.Model):
    offer = models.ForeignKey('rotator.Offer', related_name='queues')
    order = models.ForeignKey('rotator.TrafficHolderOrder', related_name='queues')
    size = models.SmallIntegerField(default=0)

    def checkStatusIsActive(self):
        return self.order.status == ACTIVE

    def getApprovalUrl(self):
        return self.order.approval_url

    def popUrl(self):
        "Gets offer url from queue and decrease the queue length"
        if self.size == 0:
            logging.warning("Attempt to get url from empty queue %s/%s" % (
                self.order.owner.name, self.order.order_id))
            return None
        self.size -= 1
        self.order.clicks_received += 1
        self.save()
        return self.offer.url

    def network(self):
        return self.offer.network.name

    def account(self):
        return self.offer.account.username

    def offerName(self):
        return self.offer.name

    def offerNum(self):
        return self.offer.offer_num

    def __unicode__(self):
        return '%s %s %s %s' % (self.offer.name, self.offer.network.name,
                                self.offer.account.username, self.size)

    class Meta:
        app_label = 'rotator'
