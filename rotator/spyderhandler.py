import mechanize
from BeautifulSoup import BeautifulSoup
from rotator.models import Earnings, Offer, UnknownOffer


class Handler:
    
    def __init__(self, now, account):
        self.account = account
        self.now = now
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


class GetAdsHandler(Handler): 
  
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.loginurl = 'http://publisher.getads.com/Welcome/LogInAndSignUp.aspx'
        self.url = 'http://publisher.getads.com/RptCampaignPerformance.aspx'
        
    def getSoup(self):
        self.br.open(self.loginurl)        
        self.br.select_form(name='aspnetForm')
        
        self.br['ctl00$ContentPlaceHolder1$lcLogin$txtUserName'] = self.account.user_id
        self.br['ctl00$ContentPlaceHolder1$lcLogin$txtPassword'] = self.account.password
        print "submit ..." 
        self.br.submit()
        
        print "opening %s ..." % self.url
       
        return BeautifulSoup(self.br.open(self.url).read())
    
    def run(self):        
        soup = self.getSoup()
        
        div = soup.find('div', {'id': 'ctl00_ContentPlaceHolder1_divReportData'})
        if not div:
            return False                      
         
        for tr in div.findAll('table')[1].findAll('tr'):
            td = tr.findAll('td')

            if len(td) == 1 or not td[2].find('img', {'title': 'Daily Breakout'}):
                continue
    
            offer_num = td[3].string            
           
            offer = self.getOffer(offer_num)
            if not offer:
                continue
            
            if td[4].span:
                span = td[4].span['onmouseover'][5:]
                campaign = span[:span.find("'")]
            else:
                campaign = td[4].string
            
            aprovedCTRblock = td[12].span if td[12].span else td[12]
                
            record = {
                'offer_num': offer_num,
                'campaign': campaign,
                'status': td[5].span.string,
                'payout': "%.2f" % float(td[6].string[1:]),
                'impressions': int(td[7].string),
                'clicks': int(td[8].string),
                'qualified_transactions': int(td[9].string),
                'aproved': int(td[10].string),
                'CTR': td[11].string[:-2],
                'aprovedCTR': aprovedCTRblock.string[:-2],
                'eCPM': td[13].string[1:],
                'EPC': td[14].string[1:],
                'revenue': td[15].string[1:],
            }               
            
            self.checkEarnings(offer)    
               
            Earnings(
                offer=offer, 
                network=self.account.network,
                campaign=record['campaign'],
                status=record['status'],
                payout=record['payout'],
                impressions=record['impressions'],
                clicks=record['clicks'],
                qualified_transactions=record['qualified_transactions'],
                aproved=record['aproved'],
                CTR=record['CTR'],
                aprovedCTR=record['aprovedCTR'],
                eCPM=record['eCPM'],
                EPC=record['EPC'],
                revenue=record['revenue']
            ).save()


class AffiliateComHandler(Handler):
    
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.loginurl = "http://affiliate.com/"
        self.url = "https://login.tracking101.com/partners/monthly_affiliate_stats.html?program_id=0&affiliate_stats_start_month=%d&affiliate_stats_start_day=%d&affiliate_stats_start_year=%d&affiliate_stats_end_month=%d&affiliate_stats_end_day=%d&affiliate_stats_end_year=%d&breakdown=cumulative" \
            % (int(self.now.month), int(self.now.day), int(self.now.year), int(self.now.month), 
               int(self.now.day), int(self.now.year))
    
    def getSoup(self):
        self.br.open(self.loginurl)          
        self.br.select_form(nr=0)
        self.br['DL_AUTH_USERNAME'] = self.account.user_id
        self.br['DL_AUTH_PASSWORD'] = self.account.password
        print "submit login form ..."
        self.br.submit()
        
        print "opening %s ..." % self.url        
        return BeautifulSoup(self.br.open(self.url).read())
    
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
            record = {
                'campaign': link.string,
                'offer_num': offer_num,
                'impressions': td[2].string,
                'clicks': td[3].string,
                'CTR': td[5].string[:-1],
                'EPC': 0 if td[10].string == 'N/A' else td[10].string[1:],
                'status': td[13].string.lower(),
                'payout': td[11].a.string[1:-5],
                'revenue':  block[block.find('$') + 1 : block.find('a') - 1]        
            }
        
            self.checkEarnings(offer)
            Earnings(
                offer=offer, 
                network=self.account.network,
                campaign=record['campaign'],
                status=record['status'],
                payout=record['payout'],
                impressions=record['impressions'],
                clicks=record['clicks'],
                CTR=record['CTR'],
                EPC=record['EPC'],
                revenue=record['revenue']
            ).save()


class HydraHandler(Handler):
    
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.loginurl = "https://network.hydranetwork.com/login"
        self.url = "https://network.hydranetwork.com/load_component/MyCampaigns/sort_by-Campaign/sort_order-asc/date_range-Today"

    def getSoup(self):
        self.br.open(self.loginurl)          
        self.br.select_form(name='login_form')
        self.br['email_address'] = self.account.user_id
        self.br['password'] = self.account.password
        print "login ... "
        self.br.submit()
        
        print "opening %s ..." % self.url
        
        return BeautifulSoup(self.br.open(self.url).read())
               
    def run(self):       
        soup =  self.getSoup()        
               
        for tr in soup.find('div', {'class': 'table-data-div'}).findAll('tr'):
            td = tr.findAll('td')
            
            offer_num = td[0].a.string
            offer = self.getOffer(offer_num)
            if not offer:
                continue
            
            record = {
                'offer_num': offer_num,
                'campaign': td[1].a.string,
                'clicks': td[2].string,
                'payout': td[5].string.strip()[1:],
                'EPC': td[6].string.strip()[1:],
                'revenue': td[7].string.strip()[1:]
            }
            
            self.checkEarnings(offer)
            Earnings(
                offer=offer, 
                network=self.account.network,
                campaign=record['campaign'],
                payout=record['payout'],
                clicks=record['clicks'],
                EPC=record['EPC'],
                revenue=record['revenue']
            ).save()


class EncoreAds(Handler):
    
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.loginurl = "http://www.ecoretrax.com/"
        self.url = ""

    def getSoup(self):
        return BeautifulSoup('')
    
    def run(self):
        pass
    

class ACPAffiliatesHandler(Handler):
    
    def __init__(self, now, account):
        Handler.__init__(self, now, account)
        self.loginurl = "http://www.acpaffiliates.com/"
        self.url = "http://publisher.affiliatecashpile.com/stats/index/offers" 
    
    def getSoup(self):
        self.br.open(self.loginurl)          
        self.br.select_form(name='loginform')
        self.br['data[User][email]'] = self.account.user_id
        self.br['data[User][password]'] = self.account.password
        print "login ... "
        self.br.submit()
        
        print "opening %s ..." % self.url
        return BeautifulSoup(self.br.open(self.url).read())
    
    def run(self):
        soup = self.getSoup()

        for tr in soup.find('tbody', {'id': 'pagingBody'}).findAll('tr'):
            td = tr.findAll('td')
            
            href = td[0].a['href']
            offer_num = href[ href.rfind('/') + 1 : ]
    
            offer = self.getOffer(offer_num)
            if not offer:
                continue
            
            link = td[0].a.string
            b = link.find('(')    
            record = {
                'offer_num': offer_num,
                'campaign': link[link.find('-') + 2 : len(link) if b == -1 else b - 1 ],
                'impressions': td[1].string,
                'clicks': td[2].string,
                'payout': td[4].string[1:],
                'revenue': td[5].string[1:]
            }

            self.checkEarnings(offer)
            Earnings(
                offer=offer, 
                network=self.account.network,
                campaign=record['campaign'],
                payout=record['payout'],
                clicks=record['clicks'],
                impressions=record['impressions'],
                revenue=record['revenue']
            ).save()
            