from django_extensions.management.jobs import BaseJob
import mechanize
import datetime
from BeautifulSoup import BeautifulSoup
from rotator.models import Earnings, Offer, Network


class Job(BaseJob):
    help = "Save earning from getads.com"
  
    def extract(self, username, password, network):  
        url = 'http://publisher.getads.com/Welcome/LogInAndSignUp.aspx'
        url2 = 'http://publisher.getads.com/RptCampaignPerformance.aspx'
        
        br = mechanize.Browser()
        br.set_debug_responses(True)
        br.set_debug_redirects(True)
        print "opening %s ..." % url
        response = br.open(url)        
        br.select_form(name='aspnetForm')
        
        br['ctl00$ContentPlaceHolder1$lcLogin$txtUserName'] = username
        br['ctl00$ContentPlaceHolder1$lcLogin$txtPassword'] = password
        
        print "login..."
        response = br.submit()
        
        print "opening %s ..." % url2
        response = br.open(url2)
        
        html = response.read()
        
        soup = BeautifulSoup(html)
        
        table = soup.find('div', {'id': 'ctl00_ContentPlaceHolder1_divReportData'}).findAll('table')[1]
                                 
        data = []
        for tr in table.findAll('tr'):
            td = tr.findAll('td')
            #print td
            if len(td) == 1 or not td[2].find('img', {'title': 'Daily Breakout'}):
                continue

            if td[4].span:
                span = td[4].span['onmouseover']
                campaign = span[5:span.find("'")]
            else:
                campaign = td[4].string
                 
            record = {
                'offer_num': td[3].string,
                'campaign': campaign,
                'status': td[5].span.string,
                'revenue': "%.2f" % float(td[6].string[1:]),
                'impressions_for_affiliates': int(td[7].string),
                'clicks': int(td[8].string),
                'qualified_transactions': int(td[9].string),
                'aproved': int(td[10].string),
                'CTR': td[11].string[:-2],
                'aprovedCTR': td[12].string[:-2],
                'eCPM': td[13].string[1:],
                'EPC': td[14].string[1:],
                'commision': td[15].string[1:],
            }   
            data.append(record)
            try:
                offer = Offer.objects.get(offer_num=record['offer_num'], network=network)
            except:
                print "WARNING: Please add offer with offer_num=%s" % record['offer_num']
                continue
                
            exist_earnings = Earnings.objects.filter(offer=offer, date=datetime.date.today())
            if exist_earnings.count():
                exist_earnings.delete()
            
            Earnings(
                offer=offer, 
                campaign=record['campaign'],
                status=record['status'],
                revenue=record['revenue'],
                impressions_for_affiliates=record['impressions_for_affiliates'],
                clicks=record['clicks'],
                qualified_transactions=record['qualified_transactions'],
                aproved=record['aproved'],
                CTR=record['CTR'],
                aprovedCTR=record['aprovedCTR'],
                eCPM=record['eCPM'],
                EPC=record['EPC'],
                commision=record['commision'],
            ).save()
            
       
        #print data     
    
    def execute(self):
        getads_params =[
            {'username': '165091', 'password': 'cpacf123' },
            {'username': '106390', 'password': 'admin123' }
        ]
        
        network = Network.objects.get(url="http://getads.com/")        
        for p in getads_params:            
            self.extract(p['username'], p['password'], network)
