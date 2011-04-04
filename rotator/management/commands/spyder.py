from django.core.management.base import BaseCommand, CommandError
import mechanize
import datetime
from BeautifulSoup import BeautifulSoup
from rotator.models import Earnings, Offer, Network, Account, UnknownOffer


class Command(BaseCommand):
    
    def getOffer(self, offer_num, account):
        offers = Offer.objects.filter(offer_num=offer_num, account=account, network=account.network)
        if not offers.count():
            existUnknown = UnknownOffer.objects.filter(offer_num=offer_num,
                    account=account, network=account.network) 
            if existUnknown.count():
                existUnknown.delete()
            UnknownOffer(offer_num=offer_num, account=account, network=account.network).save()
            print "WARNING: Please add offer with offer_num=%s" % offer_num
            return False
        
        return offers[0]
    
    def checkEarnings(self, offer):
        exist_earnings = Earnings.objects.filter(offer=offer, date__month=self.now.month, 
                    date__year=self.now.year, date__day=self.now.day)
        if exist_earnings.count():
            exist_earnings.delete()
                
    def getads(self, account): 
        url = 'http://publisher.getads.com/Welcome/LogInAndSignUp.aspx'
        url2 = 'http://publisher.getads.com/RptCampaignPerformance.aspx'
        
        br = mechanize.Browser()
        br.set_debug_responses(True)
        br.set_debug_redirects(True)
        print "opening %s ..." % url
        response = br.open(url)        
        br.select_form(name='aspnetForm')
        
        br['ctl00$ContentPlaceHolder1$lcLogin$txtUserName'] = account.user_id
        br['ctl00$ContentPlaceHolder1$lcLogin$txtPassword'] = account.password
        
        print "login..."
        response = br.submit()
        
        print "opening %s ..." % url2
        response = br.open(url2)
        
        html = response.read()
        
        soup = BeautifulSoup(html)
        
        table = soup.find('div', {'id': 'ctl00_ContentPlaceHolder1_divReportData'}).findAll('table')[1]                           
         
        for tr in table.findAll('tr'):
            td = tr.findAll('td')

            if len(td) == 1 or not td[2].find('img', {'title': 'Daily Breakout'}):
                continue
    
            offer_num = td[3].string            
           
            offer = self.getOffer(offer_num, account)
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
                'impressions_for_affiliates': int(td[7].string),
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
                network=account.network,
                campaign=record['campaign'],
                status=record['status'],
                payout=record['payout'],
                impressions_for_affiliates=record['impressions_for_affiliates'],
                clicks=record['clicks'],
                qualified_transactions=record['qualified_transactions'],
                aproved=record['aproved'],
                CTR=record['CTR'],
                aprovedCTR=record['aprovedCTR'],
                eCPM=record['eCPM'],
                EPC=record['EPC'],
                revenue=record['revenue']
            ).save()
    
    def encoreads(self, account):
        pass
    
    def affiliate(self, account):
        url = "http://affiliate.com/"

        url2 = "https://login.tracking101.com/partners/monthly_affiliate_stats.html?program_id=0&affiliate_stats_start_month=%d&affiliate_stats_start_day=%d&affiliate_stats_start_year=%d&affiliate_stats_end_month=%d&affiliate_stats_end_day=%d&affiliate_stats_end_year=%d&breakdown=cumulative" \
            % (int(self.now.month), int(self.now.day), int(self.now.year), int(self.now.month), 
               int(self.now.day), int(self.now.year)) 
             
        br = mechanize.Browser()
        br.set_debug_responses(True)
        br.set_debug_redirects(True)
        print "opening %s ..." % url
        br.open(url)  
        
        br.select_form(nr=0)

        br['DL_AUTH_USERNAME'] = account.user_id
        br['DL_AUTH_PASSWORD'] = account.password
        print "submit login form ..."
        response = br.submit()
        
        print "opening %s ..." % url2
        response = br.open(url2)
        
        html = response.read()
        
        soup = BeautifulSoup(html)
        
        data = []
        for tr in soup.find('table', {'class': 'recordTable'}).findAll('tr'):
            td = tr.findAll('td')
            if not td[1].b:
                continue
            link = td[1].b.a
            if not link or not link.string:
                continue
            
            offer_num = link['href'][ link['href'].find('=') + 1 : link['href'].find('&') ]
            offer = self.getOffer(offer_num, account)
            if not offer:
                continue
            
            block = str(td[12].b)
            record = {
                'campaign': link.string,
                'offer_num': offer_num,
                'impressions_for_affiliates': td[2].string,
                'clicks': td[3].string,
                #'leads': td[4].string,
                'CTR': td[5].string[:-1],
                'EPC': 0 if td[10].string == 'N/A' else td[10].string[1:],
                'status': td[13].string.lower(),
                'payout': td[11].a.string[1:-5],
                'revenue':  block[block.find('$') + 1 : block.find('a') - 1]        
            }
        
            self.checkEarnings(offer)
            Earnings(
                offer=offer, 
                network=account.network,
                campaign=record['campaign'],
                status=record['status'],
                payout=record['payout'],
                impressions_for_affiliates=record['impressions_for_affiliates'],
                clicks=record['clicks'],
                CTR=record['CTR'],
                EPC=record['EPC'],
                revenue=record['revenue']
            ).save()

    
    def handle(self, *args, **options):   
        self.now = datetime.datetime.now()   
        print self.now 
        print
        networks = ["http://getads.com/", "http://affiliate.com/"]
        
        for account in Account.objects.all():
            if account.network.url in networks:
                account.checked()
                if account.network.url == "http://getads.com/":    
                    self.getads(account)
                elif account.network.url == "http://affiliate.com/":
                    self.affiliate(account)
        print "Finished."    
            
