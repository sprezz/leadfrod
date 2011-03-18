import urllib, urllib2
from xml import sax
from xml.sax import parseString
import logging
import random
from rotator.models import OfferQueue, Owner

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

class TrafficHolder(object):
    url = "http://trafficholder.com/api/api.php"
    
    def __init__ (self):
        self.data = {}
        self.data['user']='sprezzatura'
        self.data['pwd']='6f3136f35dc03884783e048d80e05fa9'
        
    def _send(self, mdata):
        send_data = {}
        send_data.update(self.data)
        send_data.update(mdata)
        
        send_data=urllib.urlencode(send_data)
        print send_data
        for attempt in range(0,10):
            try:
                response = urllib2.urlopen('%s?%s' % (self.url,send_data)).read()
                if response:
                    logging.error(response) 
                break
#                handler = ResponseHandler()
#                parseString ( response_xml, handler )
            except urllib2.URLError, msg:
                logging.error('Error %s, attempt %d of 10' % (msg,attempt))
             
    def start(self, order):
        cmd = {'do':'start', 'order':order}
        self._send(cmd)
    def stop(self, order):
        cmd = {'do':'stop', 'order':order}
        self._send(cmd)
    def editOrderId(self, order, total, hour):
        cmd = {'do':'edit', 'order':order, 'total':total, 'hour':hour}
        self._send(cmd)
        
    def processOffers(self, offers):
        for offer in offers:
            logging.debug('processing %s' % offer)
            random_clicks = random.randint(offer.min_clicks, offer.max_clicks)
            logging.debug('queue size %d' % random_clicks)
            offer_q = OfferQueue.objects.filter(offer=offer)
            order = offer.account.company.owner.orders.all()[0]
            if not offer_q.exists():
                logging.debug('Created new queue')
                offerQueue = OfferQueue.objects.create(offer = offer, order=order, size=random_clicks)
                self.editOrderId(order.order_id, order.clicks_total, offerQueue.size*4)
                logging.debug('Start traffic holder ')
                self.start ( offerQueue.order.order_id )
            else:
                offerQueue = OfferQueue.objects.get(offer = offer, order=order)
                offerQueue.size += random_clicks
                logging.debug('Updating queue. New size is %d ' % offerQueue.size)
                offerQueue.save()
                logging.debug('Updating traffic holder clicks %d' % offerQueue.size*4)
                self.editOrderId(order.order_id, order.clicks_total, offerQueue.size*4)
                
    def popOfferQueueUrl(self, owner_name):
        logging.debug('Traffic holder request %s' % owner_name)
        offerQueue_q = OfferQueue.objects.filter(order__owner__name=owner_name, size__gt=0)
        if offerQueue_q.exists():
            offerQueue = offerQueue_q.order_by('?')[0]
            if not offerQueue.checkStatusIsActive():
                logging.debug('Redirect to approval url %s' % offerQueue.getApprovalUrl())
                return offerQueue.getApprovalUrl()
            logging.debug('Redirect to %s' % offerQueue.offer.url)
            return offerQueue.popUrl()
        else:
            logging.debug('Queue %s is empty. Stopping traffic holder!' % owner_name)
            self.stop ( offerQueue.order.order_id )
            return None
    
