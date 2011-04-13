import mechanize
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from rotator.models import Earnings, Offer, UnknownOffer
import urllib2
import decimal

class Handler:
    
    def __init__(self, now, account):
        self.account = account
        self.now = now
        self.loginurl = self.account.network.url
        self.url = 'set url'
        self.loginform = False
        self.username_field = 'username'
        self.password_field = 'password'
        self.br = mechanize.Browser()
        self.br.set_debug_responses(True)
        self.br.set_debug_redirects(True)
        self.br.set_handle_robots(False)
        
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

    def getSoup(self):
        print "opening %s ..." % self.loginurl
        self.br.open(self.loginurl)      
        if self.loginform:  
            self.br.select_form(name=self.loginform)
        else:
            self.br.select_form(nr=0)
        self.br[self.username_field] = self.account.user_id
        self.br[self.password_field] = self.account.password
        print "login ... "
        self.br.submit()
        
        print "opening %s ..." % self.url
        return BeautifulSoup(self.br.open(self.url).read())


class GetAdsHandler(Handler): 
  
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.loginurl = 'http://publisher.getads.com/Welcome/LogInAndSignUp.aspx'
        self.url = 'http://publisher.getads.com/RptCampaignPerformance.aspx'
        self.username_field = 'ctl00$ContentPlaceHolder1$lcLogin$txtUserName'
        self.password_field = 'ctl00$ContentPlaceHolder1$lcLogin$txtPassword'
        self.loginform = 'aspnetForm'
           
    def run(self):        
        soup = self.getSoup()
        
        div = soup.find('div', {'id': 'ctl00_ContentPlaceHolder1_divReportData'})
        if not div:
            return False                      
         
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
            Earnings(
                offer=offer, 
                network=self.account.network,
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
                revenue=td[15].string[1:]
            ).save()


class AffiliateComHandler(Handler):
    
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.url = "https://login.tracking101.com/partners/monthly_affiliate_stats.html?program_id=0&affiliate_stats_start_month=%d&affiliate_stats_start_day=%d&affiliate_stats_start_year=%d&affiliate_stats_end_month=%d&affiliate_stats_end_day=%d&affiliate_stats_end_year=%d&breakdown=cumulative" \
            % (int(self.now.month), int(self.now.day), int(self.now.year), int(self.now.month), 
               int(self.now.day), int(self.now.year))
        self.username_field = 'DL_AUTH_USERNAME'
        self.password_field = 'DL_AUTH_PASSWORD'    
   
    def run(self):       
        soup = self.getSoup()

        for tr in soup.find('table', {'class': 'recordTable'}).findAll('tr'):
            td = tr.findAll('td')
            if not td[1].b:
                continue
            link = td[1].b.a
            if not link or not link.string:
                continue
            
            offer_num = link['href'][ link['href'].find('=') + 1 : link['href'].find('&') ]
            offer = self.getOffer(offer_num)
            if not offer:
                continue
            
            block = str(td[12].b)
        
            self.checkEarnings(offer)
            Earnings(
                offer=offer, 
                network=self.account.network,
                campaign=link.string,
                status=td[13].string.lower(),
                payout=td[11].a.string[1:-5],
                impressions=td[2].string,
                clicks=td[3].string,
                CTR=td[5].string[:-1],
                EPC=0 if td[10].string == 'N/A' else td[10].string[1:],
                revenue=block[block.find('$') + 1 : block.find('a') - 1]
            ).save()


class HydraHandler(Handler):
    
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.url = "https://network.hydranetwork.com/load_component/MyCampaigns/sort_by-Campaign/sort_order-asc/date_range-Today"
        self.username_field = 'email_address'
        self.loginform = 'login_form'
                      
    def run(self):       
        soup =  self.getSoup()        
               
        for tr in soup.find('div', {'class': 'table-data-div'}).findAll('tr'):
            td = tr.findAll('td')
            
            offer = self.getOffer(td[0].a.string)
            if not offer:
                continue            
            
            self.checkEarnings(offer)
            Earnings(
                offer=offer, 
                network=self.account.network,
                campaign=td[1].a.string,
                payout=td[5].string.strip()[1:],
                clicks=td[2].string,
                EPC=td[6].string.strip()[1:],
                revenue=td[7].string.strip()[1:]
            ).save()
  

class ACPAffiliatesHandler(Handler):
    
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.loginurl = "http://www.acpaffiliates.com/"
        self.url = "http://publisher.affiliatecashpile.com/stats/index/offers" 
        self.username_field = 'data[User][email]'
        self.password_field = 'data[User][password]'
        self.loginform = 'loginform'        
    
    def run(self):
        soup = self.getSoup()

        block = soup.find('tbody', {'id': 'pagingBody'})
        if not block:
            return
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
            Earnings(
                offer=offer, 
                network=self.account.network,
                campaign=link[link.find('-') + 2 : len(link) if b == -1 else b - 1 ],
                payout=td[4].string[1:],
                clicks=clicks,
                impressions=td[1].string,
                revenue=float(td[5].string[1:]) * clicks
            ).save()
       

class APIHandler(Handler):
    
    def run(self):
        if not hasattr(self.account, 'api'):
            print "Warning! Add api for account %s" % self.account
            return False

        date = "%s/%s/%s" % (self.now.month, self.now.day, self.now.year)
        self.url = "%saffiliates/api/1/reports.asmx/CampaignSummary?affiliate_id=%s&api_key=%s&start_date=%s&end_date=%s" \
            % (self.account.network.url, self.account.api.affiliate_id, self.account.api.api_key, date, date)
        
        print 'extracting from ' + self.url
        
        soup = BeautifulStoneSoup(urllib2.urlopen(self.url))
        
        for i in soup.findAll('campaign'):
            offer = self.getOffer(i.offer_id.string)
            if not offer:
                continue
            
            self.checkEarnings(offer)
            Earnings(
                offer=offer, 
                network=self.account.network,
                campaign=i.vertical_name.string,
                payout=i.price.string,
                clicks=i.clicks.string,
                impressions=i.impressions.string,
                revenue=i.revenue.string,
                EPC=i.epc.string
            ).save()
            

class Ads4DoughHandler(Handler):
    
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.url = "https://affiliate.a4dtracker.com/logged.php?pgid=22" 
        self.loginform = 'login' 

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
                Earnings(
                    offer=offer, 
                    network=self.account.network,
                    campaign=name[name.find(')')+1:],
                    payout=offer.payout,
                    clicks=int(td[3].a.string),
                    revenue=decimal.Decimal(td[7].div.string[1:]),
                    EPC=decimal.Decimal(td[6].string[1:])
                ).save()
                
                
                
                
        soup = self.getSoup()
        table = soup.find('table', {'class': 'reportinner'})
        saveEarnings(table.findAll('tr', {'class': 'regularTextSmallCopy  rpt1'}))
        saveEarnings(table.findAll('tr', {'class': 'regularTextSmallCopy  rpt2'}))
            

class AdscendHandler(Handler):
    
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.url = "https://adscendmedia.com/campstats.php"
        #self.url += "?start_m=1&start_d=13&start_y=2011&end_m=4&end_d=13&end_y=2011&country=&camps[]="
        self.username_field = 'email'
        
    def run(self):    
        soup = self.getSoup()
       
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
            Earnings(
                offer=offer, 
                network=self.account.network,
                campaign=campaign,
                payout=td[5].a.string[1:],
                EPC=td[3].string[1:],
                clicks=td[1].string,
                revenue=td[6].string[1:]
            ).save()

