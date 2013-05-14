import urllib, urllib2
from xml import sax
from xml.sax import parseString
import logging
import random
from rotator.models.offer_queue import OfferQueue
from rotator.models.trafficholder_order import TrafficHolderOrder


referer_hiding_url = ''


class ResponseHandler(sax.handler.ContentHandler):
    def __init__(self):
        self.mapping = {}

    def startElement(self, name, attributes):
        if name.lower() == "xxx":
            return
        self.buffer = ""

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        if name.lower() == "xxx":
            return
        self.mapping[name.lower()] = self.buffer
        self.buffer = ""


class UnknownOrderException(Exception):
    pass


class TrafficHolder(object):
    url = "http://trafficholder.com/api/api.php"

    def __init__(self):
        self.data = {}
        self.data['user'] = 'sprezzatura'
        self.data['pwd'] = '6f3136f35dc03884783e048d80e05fa9'

    def set_user(self, user, password):
        if user and password:
            self.data['user'] = user
            self.data['pwd'] = password

    def _send(self, mdata):
        send_data = {}
        send_data.update(self.data)
        send_data.update(mdata)

        send_data = urllib.urlencode(send_data)
        print send_data
        for attempt in range(0, 10):
            try:
                response = urllib2.urlopen('%s?%s' % (self.url, send_data)).read()
                if response:
                    logging.error(response)
                break
            #                handler = ResponseHandler()
            #                parseString ( response_xml, handler )
            except urllib2.URLError, msg:
                logging.error('Error %s, attempt %d of 10' % (msg, attempt))

    def start(self, order):
        cmd = {'do': 'start', 'order': order}
        self._send(cmd)

    def stop(self, order):
        cmd = {'do': 'stop', 'order': order}
        self._send(cmd)

    def editOrderId(self, order, total, hour):
        # DO NOT USE changing hour
        return
        # cmd = {'do': 'edit', 'order': order, 'total': total, 'hour': hour}
        # self._send(cmd)

    def processOffers(self, offers):
        for offer in offers:
            logging.debug('processing %s' % offer)
            random_clicks = random.randint(offer.min_clicks, offer.max_clicks)
            logging.debug('queue size %d' % random_clicks)
            order = offer.account.company.owner.orders.all()[0]
            #self.set_user(order.username, order.password)
            offer_q = OfferQueue.objects.filter(offer=offer, order=order)

            if not offer_q.exists():
                logging.debug('Created new queue')
                offerQueue = OfferQueue.objects.create(offer=offer, order=order, size=random_clicks)
                self.editOrderId(order.order_id, order.clicks_total, offerQueue.size * 4)
                logging.debug('Start traffic holder ')
                self.start(offerQueue.order.order_id)
            else:
                offerQueue = offer_q[0]
                offerQueue.size += random_clicks
                logging.debug('Updating queue. New size is %d ' % offerQueue.size)
                offerQueue.save()

                for q in offer_q:
                    if q.size > 0:
                        logging.debug('Start traffic holder ')
                        self.start(q.order.order_id)
                        break

                logging.debug('Updating traffic holder clicks %d' % offerQueue.size * 4)
                self.editOrderId(order.order_id, order.clicks_total, offerQueue.size * 4)

    def popOfferQueueUrl(self, owner_name):
        logging.debug('Traffic holder request %s' % owner_name)
        try:
            order = TrafficHolderOrder.objects.get(owner__name=owner_name)
            self.set_user(order.username, order.password)
            if not order.status == 'active':
                logging.debug('Redirect to approval url %s' % order.approval_url)
                return order.approval_url
        except TrafficHolderOrder.DoesNotExist:
            logging.error('There is no order for owner %s.' % owner_name)
            raise UnknownOrderException()

        offerQueue_q = OfferQueue.objects.filter(order=order, size__gt=0)
        if offerQueue_q.exists():
            offerQueue = offerQueue_q.order_by('?')[0]
            logging.debug('Redirect to %s' % (referer_hiding_url+offerQueue.offer.url))
            return '%s' % referer_hiding_url+offerQueue.popUrl()
        else:
            logging.debug('Queue %s is empty. Stopping traffic holder!' % owner_name)
            self.stop(order.order_id)
        return None
    
