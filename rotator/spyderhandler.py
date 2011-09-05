import mechanize
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from rotator.models import Earnings, Offer, UnknownOffer, Account, ProxyServer
import urllib2
import urllib
from cookielib import CookieJar
import decimal
import datetime


"""
proxy:
http://tools.rosinstrument.com/proxy/
"""

  
class Handler:    
    def __init__(self, account):
        self.today_revenue = 0
        self.account = account
        self.now = datetime.datetime.now()
        self.loginurl = self.account.network.url
        self.chance = 0
        self.url = 'set url'
        self.loginform = False
        self.proxies = False
        
        self.username_field = 'username'
        self.password_field = 'password'
        self.br = mechanize.Browser()
        self.br.set_debug_responses(True)
        self.br.set_debug_redirects(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]
        
    @property    
    def revenue(self):
        return self.today_revenue
      
    def getOffer(self, offer_num):
        offers = Offer.objects.filter(offer_num=offer_num,
                    account=self.account, network=self.account.network)
        if not offers.count():
            existUnknown = UnknownOffer.objects.filter(offer_num=offer_num,
                account=self.account, network=self.account.network) 
            if existUnknown.count():
                existUnknown.delete()
            UnknownOffer(offer_num=offer_num,
                account=self.account, network=self.account.network).save()
            print "WARNING: Please add offer with offer_num=%s" % offer_num
            return False
        
        return offers[0]
    
    def checkEarnings(self, offer):
        exist_earnings = Earnings.objects.filter(offer=offer,
            date__month=self.now.month, date__year=self.now.year, 
            date__day=self.now.day)
        if exist_earnings.count():
            exist_earnings.delete()
        
        print "save offer %s .." % offer.offer_num    

    def changeProxy(self):
        print "<-Exception"
        self.proxies[self.chance].catchException()
        self.chance += 1
        if self.chance < len(self.proxies):
            print "Set proxy: %s" % self.proxies[self.chance].host
            self.br.set_proxies({"http": self.proxies[self.chance].host})
            return self.getSoup()
        
        return False
        
    def getSoup(self):
        print "opening %s ..." % self.loginurl
        try:
            self.br.open(self.loginurl)      
        except:
            return self.changeProxy() if self.proxies else False
        
        if self.loginform:  
            self.br.select_form(name=self.loginform)
        else:
            self.br.select_form(nr=0)
        self.br[self.username_field] = self.account.user_id
        self.br[self.password_field] = self.account.password
                
        print "login %s %s ... " % (self.account.user_id, self.account.password)
        try:
            self.br.submit()
        except:
            return self.changeProxy() if self.proxies else False
        print "opening %s ..." % self.url
        
        try:
            response = self.br.open(self.url)
        except:
            return self.changeProxy() if self.proxies else False  
          
        return BeautifulSoup(response.read())


class CXDigitalHandler(Handler):
    def __init__(self, account):
        Handler.__init__(self, account)
        self.username_field = 'login'
        self.password_field = 'pwd'
        self.url = "http://www.cxdigitalmedia.com/agents/reports/trafficresults?type=traffic&freshData=1"

    def run(self):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar()))
        print "opening %s " % self.loginurl
        print "login %s %s ... " % (self.account.user_id, self.account.password)
        response = opener.open(self.loginurl, urllib.urlencode({
            self.username_field: self.account.user_id, 
            self.password_field: self.account.password
        })) 
        
        today = "%s/%s/%s" % (self.now.year, self.now.month, self.now.day)
        print "opening %s ..." % self.url
        print "params: %s " % "sRange=%s&eRange=%s&cRange=&groupBy=campaign" % (today, today)
        
        data = "sRange=%s&eRange=%s&cRange=&groupBy=campaign" % (today, today)
        soup = BeautifulSoup(opener.open(self.url, data).read())
        table = soup.find('table', {'id': 'table_mytraffic'})
        if not table:
            return True
        records = []
        for tr in table.tbody.findAll('tr'):
            offer = self.getOffer(tr.find('td', {'class': 'td_camp_id'}).string)
            if not offer:
                continue
            
            self.checkEarnings(offer)
            earnings = Earnings(
                offer=offer, 
                network=self.account.network,
                niche=offer.niche,
                campaign=tr.find('td', {'class': 'td_camp_title'}).a.string,
                clicks=tr.find('td', {'class': 'td_clicks cl'}).string,
                payout=decimal.Decimal(str(offer.payout)),
                EPC= tr.find('td', {'class': 'td_ECPC'}).string[1:],
                revenue=decimal.Decimal(tr.find('td', {'class': 'td_revenue'}).string[1:]),
            )
            earnings.save()
            self.today_revenue += earnings.revenue        
        return True
        
    
class HydraHandler(Handler):    
    def __init__(self, account):
        Handler.__init__(self, account)
        self.url = "https://network.hydranetwork.com/load_component/MyCampaigns/sort_by-Campaign/sort_order-asc/date_range-Today"
        self.username_field = 'email_address'
        self.loginform = 'login_form'
                      
    def run(self):   
        try:    
            soup =  self.getSoup() 
        except:
            return False
        if not soup:
            return False       
        div = soup.find('div', {'class': 'table-data-div'})
        if not div:
            return False
        
        for tr in div.findAll('tr'):
            td = tr.findAll('td')
            
            offer = self.getOffer(td[0].a.string)
            if not offer:
                continue            
            
            self.checkEarnings(offer)
            earnings = Earnings(
                offer=offer, 
                network=self.account.network,
                niche=offer.niche,
                campaign=td[1].a.string,
                payout=td[5].string.strip()[1:],
                clicks=td[2].string,
                EPC=td[6].string.strip()[1:],
                revenue=decimal.Decimal(td[7].string.strip()[1:])
            )
            earnings.save()
            self.today_revenue += earnings.revenue
        return True
  

"""
    APIHandler: Convert2media, EncoreAds
"""
class APIHandler(Handler):
    
    def run(self):
        if not hasattr(self.account, 'api'):
            print "Warning! Add api for account %s" % self.account
            return False

        yesterday = self.now - datetime.timedelta(days=1)
        yesterday = "%s/%s/%s" % (yesterday.month, yesterday.day, yesterday.year)
        
        self.url = "%saffiliates/api/1/reports.asmx/CampaignSummary?affiliate_id=%s&api_key=%s&start_date=%s&end_date=%s" \
            % (self.account.network.url, self.account.api.affiliate_id, self.account.api.api_key, 
               yesterday, "%s/%s/%s" % (self.now.month, self.now.day, self.now.year))
        
        print 'extracting from ' + self.url
        try:
            soup = BeautifulStoneSoup(urllib2.urlopen(self.url))
        except:
            return False
        if not soup:
            return False
        for i in soup.findAll('campaign'):
            offer = self.getOffer(i.offer_id.string)
            if not offer:
                continue
            
            self.checkEarnings(offer)
            earnings = Earnings(
                offer=offer, 
                network=self.account.network,
                niche=offer.niche,
                campaign=i.vertical_name.string,
                payout=i.price.string,
                clicks=i.clicks.string,
                impressions=i.impressions.string,
                revenue=decimal.Decimal(i.revenue.string),
                EPC=i.epc.string
            )
            earnings.save()
            self.today_revenue += earnings.revenue
        return True
               

class AdscendHandler(Handler):    
    def __init__(self, account):
        Handler.__init__(self, account)
        self.url = "https://adscendmedia.com/campstats.php"
        #self.url += "?start_m=1&start_d=13&start_y=2011&end_m=4&end_d=13&end_y=2011&country=&camps[]="
        self.username_field = 'email'
        
    def run(self):    
        soup = self.getSoup()
        if not soup:
            return False
        for tr in soup.find('div', {'id': 'content'}).find('table', {'class': 'bordered'}).findAll('tr'):
            td = tr.findAll('td')
            if not td[0].a: 
                continue
        
            campaign = td[0].a.string
            try:    
                offer = Offer.objects.get(name=campaign, account=self.account, network=self.account.network)  
            except:
                continue            

            self.checkEarnings(offer)
            earnings = Earnings(
                offer=offer, 
                network=self.account.network,
                niche=offer.niche,
                campaign=campaign,
                payout=td[5].a.string[1:],
                EPC=td[3].string[1:],
                clicks=td[1].string,
                revenue=decimal.Decimal(td[6].string[1:])
            )
            earnings.save()
            self.today_revenue += earnings.revenue
        return True


"""
    AzoogleHandler - handler running with selenium
"""
class AzoogleHandler(Handler):
    
    def __init__(self, data):
        self.now = datetime.datetime.now()
        try:
            self.account = Account.objects.get(id=data['account'])
        except:
            print "no such account"
            self.account = None    
        self.data = data
        
    def run(self):
        if not self.account:
            return False
        
        self.account.checked()
        if 'offer_num' not in self.data:
             return False
        offer = self.getOffer(self.data['offer_num'])
        if not offer:
            print "no offer %s" % self.data['offer_num']
            return False
        
        self.checkEarnings(offer)
        earnings = Earnings(
            offer=offer, 
            network=self.account.network,
            niche=offer.niche,
            campaign=str(self.data['campaign']),
            clicks=int(self.data['clicks']),
            payout=decimal.Decimal(str(offer.payout)),
            revenue=decimal.Decimal(self.data['revenue'])
        )
        earnings.save()

        if 'today_revenue' in self.data['today_revenue']:
            self.account.setRevenue(self.data['today_revenue'])
        return True
   
            
class CopeacHandler(Handler):    
    def __init__(self, account):
        Handler.__init__(self, account)
        self.username_field = 'txtUserName'
        self.password_field = 'txtPassword'
        self.loginform = 'form1'
        
    def getSoup(self):
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        
        self.br.open(self.loginurl)     
        print "login to copeac..."   
        print self.loginurl
        self.br.select_form(name=self.loginform)
        self.br.form.find_control('password').__dict__['name'] = 'txtPassword'
        self.br.form.find_control('submit').__dict__['name'] = 'btnSubmit'
        self.br.form.new_control('hidden', '__EVENTARGUMENT', {'value': u''})
        self.br.form.new_control('hidden', '__EVENTTARGET', {'value': u''})
        self.br.form[self.username_field] = self.account.user_id
        self.br.form[self.password_field] = self.account.password
        print "%s %s" % (self.account.user_id, self.account.password)
        return BeautifulSoup(self.br.submit(coord=[21, 4]).read())
        
    def run(self):
        soup = self.getSoup()
        if not soup:
            return False
        table = soup.find('table', {'id': 'itemPlaceholderContainer'})
        if not table:
            return False
        for tr in table.findAll('tr', {'valign': 'top'}):
            td = tr.findAll('td')
            offer = self.getOffer(td[0].a.string)
            if not offer:
                continue            

            self.checkEarnings(offer)
            earnings = Earnings(
                offer=offer, 
                network=self.account.network,
                niche=offer.niche,
                campaign=td[1].a.string,
                clicks=td[2].a.string,
                payout=decimal.Decimal(str(offer.payout)),
                EPC=td[6].a.string[1:],
                revenue=decimal.Decimal(td[5].a.string[1:])
            )
            earnings.save()
            self.today_revenue += earnings.revenue
        return True


""" 
    TrackerHandler: Ads4Dough, Globalizer, TrouveMedia
"""
class TrackerHandler(Handler):
    def __init__(self, account, domain):
        Handler.__init__(self, account)
        self.url = "https://%s/logged.php?pgid=22&smonth=%d&sday=%d&syear=%d&emonth=%d&eday=%d&eyear=%d" % \
            (domain, self.now.month, self.now.day, self.now.year, self.now.month, self.now.day, self.now.year) 
    
    def run(self):        
        def saveEarnings(trs):
            for tr in trs:               
                td = tr.findAll('td')
                if not td[1].nobr:
                    continue
                name = td[1].nobr.string
                offer = self.getOffer(name[1:name.find(')')])
                if not offer:
                    continue
                
                self.checkEarnings(offer)               
                earnings = Earnings(
                    offer=offer, 
                    network=self.account.network,
                    niche=offer.niche,
                    campaign=name[name.find(')')+1:],
                    payout=decimal.Decimal(str(offer.payout)),
                    clicks=int(td[3].a.string),
                    revenue=decimal.Decimal(td[7].div.string[1:]),
                    EPC=decimal.Decimal(td[6].string[1:])
                )
                earnings.save()
                self.today_revenue += earnings.revenue                  
                
        soup = self.getSoup()
        if not soup:
            return False
        table = soup.find('table', {'class': 'reportinner'})
        if not table:
            return False
        saveEarnings(table.findAll('tr', {'class': 'regularTextSmallCopy  rpt1'}))
        saveEarnings(table.findAll('tr', {'class': 'regularTextSmallCopy  rpt2'}))
        return True


class Ads4DoughHandler(TrackerHandler):    
    def __init__(self, account):
        TrackerHandler.__init__(self, account, "affiliate.a4dtracker.com")
        self.loginform = 'login' 


class GlobalizerHandler(TrackerHandler):  
    def __init__(self, account):
        TrackerHandler.__init__(self, account, "affiliate.glbtracker.com")
  

class TrouveMediaHandler(TrackerHandler):
    def __init__(self, account):
        TrackerHandler.__init__(self, account, "affiliate.tvmtracker.com")
        
        
"""
    ReportHandler: GetAds, CPAFlash, TriadMedia
"""
class ReportHandler(Handler):
    def __init__(self, account, domain):
        Handler.__init__(self, account)
        self.url = "http://%s/RptCampaignPerformance.aspx" % domain
        self.username_field = 'ctl00$ContentPlaceHolder1$lcLogin$txtUserName'
        self.password_field = 'ctl00$ContentPlaceHolder1$lcLogin$txtPassword'
        self.loginform = 'aspnetForm'
        self.proxies = ProxyServer.objects.order_by('exceptions')
        print self.proxies[self.chance].host
        
        self.br.set_proxies({"http": self.proxies[self.chance].host})  
        
    def run(self):        
        soup = self.getSoup()
        if not soup:
            return False
        div = soup.find('div', {'id': 'ctl00_ContentPlaceHolder1_divReportData'})
        if not div:
            return True                      
         
        for tr in div.findAll('table')[1].findAll('tr'):
            td = tr.findAll('td')

            if len(td) == 1 or not td[2].find('img', {'title': 'Daily Breakout'}):
                continue         
           
            offer = self.getOffer(td[3].string)
            if not offer:
                continue
            
            if td[4].span:
                span = td[4].span['onmouseover'][5:]
                campaign = span[:span.find("'")]
            else:
                campaign = td[4].string
            
            aprovedCTRblock = td[12].span if td[12].span else td[12]             
            
            self.checkEarnings(offer)            
            earnings = Earnings(
                offer=offer, 
                network=self.account.network,
                niche=offer.niche,
                campaign=campaign,
                status=td[5].span.string,
                payout="%.2f" % float(td[6].string[1:]),
                impressions=int(td[7].string),
                clicks=int(td[8].string),
                qualified_transactions=int(td[9].string),
                aproved=int(td[10].string),
                CTR=td[11].string[:-2],
                aprovedCTR=aprovedCTRblock.string[:-2],
                eCPM=td[13].string[1:],
                EPC=td[14].string[1:],
                revenue=decimal.Decimal(td[15].string[1:])
            )
            earnings.save()
            self.today_revenue +=  earnings.revenue
        return True


class GetAdsHandler(ReportHandler):  
    def __init__(self, account):
        ReportHandler.__init__(self, account, "publisher.getads.com")    
        
        
class CPAFlashHandler(ReportHandler):
    def __init__(self, account):
        ReportHandler.__init__(self, account, "affiliate.cpaflash.com")
        
        
class TriadMediahandler(ReportHandler):
    def __init__(self, account):
        ReportHandler.__init__(self, account, "affiliate.triadmedia.com")


"""
    StatsHadler: AdAngels, ACPAffiliates, 3CPA, TheEdu, YeahCPA, Vancead, GoOffers
"""
class StatsHandler(Handler):
    def __init__(self, account, domain):
        Handler.__init__(self, account)
        self.url = "http://%s/stats/index/offers" % domain
        self.username_field = 'data[User][email]'
        self.password_field = 'data[User][password]'
        
    def run(self):
        try:
            soup = self.getSoup()
        except:
            return False
            
        if not soup:
            return False
        block = soup.find('tbody', {'id': 'pagingBody'})
        if not block:
            return True
        for tr in block.findAll('tr'):
            td = tr.findAll('td')
            
            href = td[0].a['href']
            offer_num = href[ href.rfind('/') + 1 : ]
    
            offer = self.getOffer(offer_num)
            if not offer:
                continue
            
            link = td[0].a.string
            b = link.find('(')
            clicks = int(td[2].string)

            self.checkEarnings(offer)
            earnings = Earnings(
                offer=offer, 
                network=self.account.network,
                niche=offer.niche,
                campaign=link[link.find('-') + 2 : len(link) if b == -1 else b - 1 ],
                payout=td[4].string[1:],
                clicks=clicks,
                impressions=td[1].string,
                revenue=float(td[5].string[1:]) * clicks
            )
            earnings.save()
            self.today_revenue += earnings.revenue
        return True


class AdAnglerHandler(StatsHandler):
    def __init__(self, account):
        StatsHandler.__init__(self, account, "affiliate.adanglers.com")
        self.username_field = 'username'
        self.password_field = 'password'


class ACPAffiliatesHandler(StatsHandler):    
    def __init__(self, account):
        StatsHandler.__init__(self, account, "publisher.affiliatecashpile.com")
        self.loginform = 'loginform'

  
class ThreeCPAHandler(StatsHandler):
    def __init__(self, account):
        StatsHandler.__init__(self, account, "affiliates.3cpa.com")
        

class YeahCPAHandler(StatsHandler):
    def __init__(self, account):
        StatsHandler.__init__(self, account, "yeahcpa.hasoffers.com")

       
class VanceadHandler(StatsHandler):
    def __init__(self, account):
        StatsHandler.__init__(self, account, "publishers.vancead.com")


class GoOffersHandler(StatsHandler):
    def __init__(self, account):
        StatsHandler.__init__(self, account, "affiliate.gooffers.net")    


class EduHandler(StatsHandler):
    def __init__(self, account):
        StatsHandler.__init__(self, account, "affiliates.theedunetwork.com")


"""
    PartnerHandler: Affiliate, clickbooth
"""
class PartnerHandler(Handler):
    def __init__(self, account, domain):
        Handler.__init__(self, account)
        #https://publishers.clickbooth.com/partners/monthly_affiliate_stats.html?campaign_type=all_campaigns&affiliate_stats_start_month=5&affiliate_stats_start_day=9&affiliate_stats_start_year=2011&affiliate_stats_end_month=5&affiliate_stats_end_day=9&affiliate_stats_end_year=2011&breakdown=cumulative
        self.url = "https://%s/partners/monthly_affiliate_stats.html?program_id=0&affiliate_stats_start_month=%d&affiliate_stats_start_day=%d&affiliate_stats_start_year=%d&affiliate_stats_end_month=%d&affiliate_stats_end_day=%d&affiliate_stats_end_year=%d&breakdown=cumulative" \
            % (domain, int(self.now.month), int(self.now.day), int(self.now.year), int(self.now.month), 
               int(self.now.day), int(self.now.year))
        self.username_field = 'DL_AUTH_USERNAME'
        self.password_field = 'DL_AUTH_PASSWORD'  
        self.inc = 1
        
    def run(self):       
        soup = self.getSoup()
        if not soup:
            return False
        table = soup.find('table', {'class': 'recordTable'})
        if not table:
            return False
        
        for tr in table.findAll('tr'):
            td = tr.findAll('td')
            if not td[1].b:
                continue
            link = td[1].b.a
            if not link or not link.string:
                continue
            
            end = link['href'].find('&')
            if end == -1:
                end = len(link['href'])
            offer_num = link['href'][ link['href'].find('=') + 1 : end]
            offer = self.getOffer(offer_num)
            if not offer:
                continue
            
            block = str(td[12].b)
            self.checkEarnings(offer)
            earnings = Earnings(
                offer=offer, 
                network=self.account.network,
                niche=offer.niche,
                campaign=link.string,
                status=td[12 + self.inc].string.lower(),
                payout=td[10 + self.inc].a.string[1:-5],
                impressions=td[2].string,
                clicks=td[3].string,
                CTR=td[5].string[:-1].replace(',', ''),
                EPC=0 if td[9 + self.inc].string == 'N/A' else td[9 + self.inc].string[1:],
                revenue=decimal.Decimal(block[block.find('$') + 1 : block.find('a') - 1] if self.inc else td[11].b.string[1:])
                #decimal.Decimal((block[block.find('$') + 1 : block.find('a') - 1]))
            )
            earnings.save()
            self.today_revenue += earnings.revenue
        return True

  
class AffiliateComHandler(PartnerHandler):    
    def __init__(self, account):
        PartnerHandler.__init__(self, account, 'login.tracking101.com')  
        

class ClickBoothHandler(PartnerHandler):
    def __init__(self, account):
        PartnerHandler.__init__(self, account, 'publishers.clickbooth.com')
        self.inc = 0 

