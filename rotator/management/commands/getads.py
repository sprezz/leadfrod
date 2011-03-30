from django.core.management.base import BaseCommand, CommandError
import mechanize
import datetime
from BeautifulSoup import BeautifulSoup
from rotator.models import Earnings, Offer, Network, Account, UnknownOffer


class Command(BaseCommand):
    
    def getads(self, account): 
        account.checked()
        url = 'http://publisher.getads.com/Welcome/LogInAndSignUp.aspx'
        url2 = 'http://publisher.getads.com/RptCampaignPerformance.aspx'
        
        br = mechanize.Browser()
        br.set_debug_responses(True)
        br.set_debug_redirects(True)
        print "opening %s ..." % url
        response = br.open(url)        
        br.select_form(name='aspnetForm')
        
        br['ctl00$ContentPlaceHolder1$lcLogin$txtUserName'] = account.username
        br['ctl00$ContentPlaceHolder1$lcLogin$txtPassword'] = account.password
        
        print "login..."
        response = br.submit()
        
        print "opening %s ..." % url2
        response = br.open(url2)
        
        html = response.read()
        
        soup = BeautifulSoup(html)
        
        table = soup.find('div', {'id': 'ctl00_ContentPlaceHolder1_divReportData'}).findAll('table')[1]
                                 
        now = datetime.datetime.now()
        
        for tr in table.findAll('tr'):
            td = tr.findAll('td')

            if len(td) == 1 or not td[2].find('img', {'title': 'Daily Breakout'}):
                continue
    
            offer_num = td[3].string
            
            offers = Offer.objects.filter(offer_num=offer_num, account=account, network=account.network)
            if not offers.count():
                existUnknown = UnknownOffer.objects.filter(offer_num=record['offer_num'],
                        account=account, network=account.network) 
                if existUnknown.count():
                    existUnknown.delete()
                UnknownOffer(offer_num=record['offer_num'], account=account, network=account.network).save()
                print "WARNING: Please add offer with offer_num=%s" % record['offer_num']
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
            
            offer = offers[0]
                
            exist_earnings = Earnings.objects.filter(offer=offer, date__month=now.month, 
                        date__year=now.year, date__day=now.day)
            if exist_earnings.count():
                exist_earnings.delete()
            print "save %s" % record['offer_num']
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
                revenue=record['revenue'],
            ).save()
            
    def handle(self, *args, **options):       
        for account in Account.objects.filter(network=Network.objects.get(url="http://getads.com/")):            
            self.getads(account)
        print "Finished."    
            
