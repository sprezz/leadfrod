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

class RegistrationClickException(Exception):
    pass

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
                urllib2.urlopen('%s?%s' % (self.url,send_data)).read()
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
            clicks = random.randint(offer.min_clicks, offer.max_clicks)
            offer_q = OfferQueue.objects.filter(offer=offer)
            order = offer.company.owner.orders.all()[0]
            if not offer_q.exists():
                offerQueue = OfferQueue.objects.create(offer = offer, order=order, size=clicks)
                self.editOrderId(order.order_id, order.total_clicks, offerQueue.size*4)
                self.start(offerQueue.order.order_id)
            else:
                offerQueue = OfferQueue.objects.get(offer = offer, order=order)
                offerQueue.size += clicks
                offerQueue.save()
                self.editOrderId(order.order_id, order.total_clicks, offerQueue.size*4)
                
    def getQueueUrl(self, owner):
        try:
            owner = Owner.objects.get(name=owner)
            offerQueue_q = OfferQueue.objects.filter(order=owner.orders.all()[0])
            if offerQueue_q.exists():
                offerQueue = offerQueue_q.order_by('?')[0]
                offerQueue.size -= 1
                offerQueue.save()
                if offerQueue.size == 0:
                    self.stop(offerQueue.order.order_id)
                return offerQueue.offer.url 
            else:
                return None
                
        except Owner.DoesNotExist, msg:
            raise RegistrationClickException(msg)                
    
