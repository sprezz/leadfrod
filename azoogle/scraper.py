# -*- coding: utf-8 -*-

import sys
import os
import multiprocessing
from selenium import selenium
from time import sleep
from BeautifulSoup import BeautifulSoup
import urllib2
import urllib
import decimal

HOST = 'http://leadfrod.billsforless.net/'

class SeleniumServer(multiprocessing.Process):
    def run(self):
        os.system('java -jar ./selenium-server-standalone-2.0b2.jar')
        
class Scraper:    
    def __init__(self, account):
        self.account = account
        self.loginurl = 'https://login.azoogleads.com/affiliate/'
        self.dataurl = 'https://login.azoogleads.com/affiliate/affiliatestats/OfferReport?rst=1#'
        self.saveurl = HOST + 'azoogle/earnings/save/?'
        self.selenium = selenium("localhost", 4444, "*firefox", self.loginurl)
        self.server = SeleniumServer()      
        
    def __del__(self):
        self.server.terminate()
    
    def sleep(self, seconds):        
        print "Wait %d seconds ..." % seconds
        sleep(seconds)
           
    def extract(self):
        sel = self.selenium
        sel.open(self.loginurl)  
        self.sleep(3)      
        sel.type('login_name', self.account['username'])
        sel.type('login_password', self.account['password'])
        sel.click("submit")
        self.sleep(3)    
        sel.open(self.dataurl)
        
        soup = BeautifulSoup(sel.get_html_source())
        table = soup.find('table', {'id': 'query_result_table'})
        if not table:
            return False       
        
        today_revenue = 0
        data = []
        for tr in table.findAll('tr'):
            td = tr.findAll('td')
            if not td:
                continue
            if not td[0].div:
                continue
            
            revenue = td[7].a.string[1:]
            data.append({
                'account': self.account['id'],
                'offer_num': td[0].div.a.string,                
                'clicks': td[3].a.string,
                'revenue': revenue,
                'campaign': td[2].div.a.string,
            })
            today_revenue += decimal.Decimal(revenue)
        
        for key, value in enumerate(data):
            print key
            if key == 0:
                print "set today revenue"
                value['today_revenue'] = today_revenue
            print self.saveurl + urllib.urlencode(value) 
            response = urllib2.urlopen(self.saveurl + urllib.urlencode(value))
            print "result %s" % str(response.read())
        return True 
                                   
    def run(self):
        self.server.start()
        print "run selenium server"
        self.sleep(4)
        print "run selenium client"
        self.selenium.start()
        result = self.extract()               
        self.selenium.stop()
        return result      

                 
def main():
    url = HOST + 'azoogle/accounts/'
    response = urllib2.urlopen(url)
    if not response:
        print "No connetion with url: % " % url
    accounts = eval(response.read())

    for account in accounts:
        Scraper(account).run()
        break


if __name__ == '__main__':
    sys.exit(main())
         

