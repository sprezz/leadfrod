""" This module should consist of BaseSpyder object and other Spyder objects 
    based on that should be used in rotator.managmet.commands.spuder module for
    getting data from external sites with ads and offers """

import mechanize
import re

from BeautifulSoup import BeautifulSoup
from datetime import datetime
from rotator.models import Earnings, Account, Offer, UnknownOffer


"""
                "http://getads.com/":{
                    "login_url":'http://publisher.getads.com/Welcome/LogInAndSignUp.aspx',
                    "data_url":'http://publisher.getads.com/RptCampaignPerformance.aspx',
                    "login_key":'ctl00$ContentPlaceHolder1$lcLogin$txtUserName',
                    'password_key':'ctl00$ContentPlaceHolder1$lcLogin$txtPassword',
                    'login_form_selector':{'name':'aspnetForm'},
                  },
                
                "http://affiliate.com/":{
                    "login_url":'http://affiliate.com/',
                    "data_url":'https://login.tracking101.com/partners/monthly_affiliate_stats.html?program_id=0&affiliate_stats_start_month=%d&affiliate_stats_start_day=%d&affiliate_stats_start_year=%d&affiliate_stats_end_month=%d&affiliate_stats_end_day=%d&affiliate_stats_end_year=%d&breakdown=cumulative',
                    "login_key": 'DL_AUTH_USERNAME',
                    'password_key':'DL_AUTH_PASSWORD',
                    'login_form_selector':{'nr':0},
                  },
                  
                "https://network.hydranetwork.com/login":{
                    "login_url":'https://network.hydranetwork.com/login',
                    "data_url":'https://network.hydranetwork.com/reports',
                    "login_key":'email_address',
                    'password_key':'password',
                    'login_form_selector':{'name':'login_form'},
                  },  
              
              "http://emt.copeac.com/forms/login.aspx":{
                    "login_url":'http://emt.copeac.com/forms/login.aspx',
                    "data_url":'http://emt.copeac.com/forms/report.aspx?MenuId=99786',  ## TODO: check menu id for hard code
                    "login_key":'txtUserName',
                    'password_key':'txtPassword',
                    'login_form_selector':{'name':'form1'},
                  },
              
              "http://www.clickbooth.com":{
                    "login_url":'https://publishers.clickbooth.com/',
                    "data_url":'https://publishers.clickbooth.com/partners/reports/performance.html?program_menu_type=0&program_id=0&period=today&start_date_day=%s&end_date_day=%s&report_type=html',
                    "login_key":'DL_AUTH_USERNAME',
                    'password_key':'DL_AUTH_PASSWORD',
                    'login_form_selector':{'nr':0},
                  },
"""
NETWORKS_MAP={
                "http://clickbooth.com/":{
                    "login_url":'https://publishers.clickbooth.com/',
                    "data_url":'https://publishers.clickbooth.com/partners/reports/performance.html?program_menu_type=0&program_id=0&period=today&start_date_day=%s&end_date_day=%s&report_type=html',
                    "login_key":'DL_AUTH_USERNAME',
                    'password_key':'DL_AUTH_PASSWORD',
                    'login_form_selector':{'nr':0},
                  },              
              }

class BaseDataSpyder(object):
    """ This is base class for data parser. It should has 
        login_url - url user for loggin thru the mechanize.Browser
        data_url - urls where data are represented
    """
    now = datetime.today()
    
    def __init__(self, network):
        """ This method should set every network: 
                    self.network = network
                    self.login_url = network_login_url
                    self.data_url = network_data_url
                    self.login_key = network_login_key
                    self.password_key = network_password_key
                    self.login_form_selector = network_login_form_selector
            """
        
        self.network = network
        current_network_map = NETWORKS_MAP[network.url]
        self.login_url = current_network_map.get('login_url')
        self.data_url = current_network_map.get('data_url')
        self.login_key = current_network_map.get('login_key')
        self.password_key = current_network_map.get('password_key')
        self.login_form_selector = current_network_map.get(
                                                        'login_form_selector')
        
    
    def run_spyder(self):
        """ This method should run spyder step by step for all Accounts."""
        
        accounts = Account.objects.filter(network=self.network)
        if accounts.count():
            for account in accounts:
                browser = self.login(account)
                data = self.get_data(browser)
                account.last_checked = datetime.now()
                account.save() 
                self.parse_data(data, account)
        else:
            print "Sorry here are no accounts for %s network in database" % (
                                                                self.network)
        print "%s successfully finished his work" % self.__class__.__name__
            
    def login(self, account):
        """ This method should login to ads site via login_url and get data_html
            from it that should be parsed via parse_data. Taken data will be 
            saved in database via save_earnings"""
        
        br = mechanize.Browser()
        br.set_debug_responses(True)
        br.set_debug_redirects(True)
        br.open(self.login_url)        
        br.select_form(**self.login_form_selector)
        br[self.login_key] = account.user_id
        br[self.password_key] = account.password
        br.submit()
        return br
    
    def get_data(self, br):
        """ This method defined for implementing custom manipulations on page 
            with statistic """
        response = br.open(self.data_url)
        return response.read()
    
    def parse_data(self, html_data, account):
        """ This method should be customized!  
            Here should be placed main magic that get data dict from html_data 
            - catched HTML.
            In the end of this method should be called self.update_earnings(
            self, offer, record) to update existing earnings
            """
        
        raise Exception("This method should be custom for every Spyder class ") 
    
    def get_offer(self, offer_num, account):
        """ This method should get offer from DB or return false to stop adding 
            information for this offer """
        
        offer_num = int(offer_num)
        offers = Offer.objects.filter(offer_num=offer_num, 
                                      account= account, 
                                      network= self.network)
        if not offers.count():
            existUnknown = UnknownOffer.objects.filter(offer_num=offer_num,
                                                       account=account, 
                                                       network=self.network) 
            if existUnknown.count():
                existUnknown.delete()
            UnknownOffer(offer_num=offer_num, 
                         account=account, 
                         network=self.network).save()
            print "WARNING: Please add offer with offer_num=%s" % offer_num
            return False
        
        return offers[0]


    def update_earnings(self, offer, earning_data):
        """ This method should take base args to get existing Earnings ans save 
            Earnings.Here required fields for earning_data dict
            earning_data={
                            campaign: ''
                            status: ""
                            payout: 0.00
                            impressions: 0 
                            clicks: 0
                            CTR: 0.000
                            EPC: 0.00
                            revenue: 0.00
                        }
        """
        exist_earnings = Earnings.objects.filter(offer=offer, 
                                                 date__month=self.now.month, 
                                                 date__year=self.now.year, 
                                                 date__day=self.now.day)
        if exist_earnings.count():
            exist_earnings.delete()

        Earnings(offer=offer, network=self.network, **earning_data).save()

        
class GetAdsSpyder(BaseDataSpyder):
    """ Custom GetAds network parser object """
    
    def parse_data(self, html_data, account):
        """ Custom GetAds network parser 
            Available fields in report :
            CID            3
            Campaign        4
            Status        5    
            Payout        6
            I            7    
            C            8
            Q            9
            A            10
            CTR            11
            Approved %    12   0.00%?
            eCPM        13
            EPC            14
            Commission    15
        """
        
        soup = BeautifulSoup(html_data)
        report_list_block = soup.find('div', {
                                'id': 'ctl00_ContentPlaceHolder1_divReportData'
                                  })
        if not report_list_block:
            return
        
        table = report_list_block.findAll('table')[1]                           
        for tr in table.findAll('tr'):
            td = tr.findAll('td')
            if len(td) == 1 or not td[2].find('img', 
                                              {'title': 'Daily Breakout'}):
                continue
    
            offer_num = td[3].string            
            offer = self.get_offer(offer_num, account)
            if not offer:
                continue
            
            if td[4].span:
                span = td[4].span['onmouseover'][5:]
                campaign = span[:span.find("'")]
            else:
                campaign = td[4].string
            
            aprovedCTRblock = td[12].span if td[12].span else td[12]
            record = {
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
            
            self.update_earnings(offer, record)



class AffiliateSpyder(BaseDataSpyder):
    """ Custom Afilate network parser object """
    
    def __init__(self, network):             
        """ Custom Afilate network init """
        
        super(AffiliateSpyder, self).__init__(network)
        target_date_info = (int(self.now.month), int(self.now.day), 
                                         int(self.now.year), 
                                         int(self.now.month), int(self.now.day),
                                         int(self.now.year))
        
        self.data_url = self.data_url % target_date_info 
        
    
    def parse_data(self, html_data, account):
        """ Custom Afilate network parser 
            Available fields in report :
            Type            0
            Campaign Name    1
            Impressions        2
            Clicks            3
            Leads                4
            Click Thru Ratio    5
            S/U                6
            Number Of Sales    7
            # Sub-Sales        8
            Total Sales        9
            EPC                10
            Payout             11
            Total                12
            Current Status        13
            Banner Stats        14
            SubID                15
        """
        
        soup = BeautifulSoup(html_data)
        for tr in soup.find('table', {'class': 'recordTable'}).findAll('tr'):
            td = tr.findAll('td')
            if not td[1].b:
                continue
            
            link = td[1].b.a
            if not link or not link.string:
                continue
            
            offer_num = re.search('pid=(?P<offer_id>\d+)&', link['href']
                                                            ).group('offer_id')
            offer = self.get_offer(offer_num, account)
            if not offer:
                continue
            
            block = str(td[12].b)
            record = {
                'campaign': link.string,
                'impressions': td[2].string,
                'clicks': td[3].string,
                'CTR': td[5].string[:-1],
                'EPC': 0 if td[10].string == 'N/A' else td[10].string[1:],
                'status': td[13].string.lower(),
                'payout': td[11].a.string[1:-5],
                'revenue':  block[block.find('$') + 1 : block.find('a') - 1]        
            }
            self.update_earnings(offer, record)


class HydraSpyder(BaseDataSpyder):
    """ Custom Hydra network parser object """
    
    def parse_data(self, html_data, account):
        """ Custom Hydra network parser.
            Available fields in report :
            ID -        0
            Campaign-    1
            Clicks -     2
            Actions    3  - ?
            Conversion 4  
            Payout    5
            Revenue    6
            EPC        7
            not represented but required - 
                            status: ""
                            impressions_for_affiliates: 0 
        """

        soup = BeautifulSoup(html_data)
        
        content_block = soup.find('div', {'id': 'report-content'})
        if not content_block:
            return
        table = content_block.findAll('table')[0]                           
        for tr in table.findAll('tr'):
            td = tr.findAll('td')
            if td[0].div:
                continue
            
            offer_num = td[0].a.string            
            offer = self.get_offer(offer_num, account)
            
            if not offer:
                continue
            
            record = {
                        'campaign': td[1].a.string,
                        'payout': td[5].string[1:],
                        'clicks': int(td[2].string),
                        'revenue': td[6].string[1:],
                        'status':'',
                        "impressions": 0, ## TODO: REMOVE HARD CODE
                        'EPC': td[7].string[1:],
                        'CTR': td[4].string[:-1],
                        }               
            self.update_earnings(offer, record)


class ClickBoothSpyder(BaseDataSpyder):
    """ Custom ClickBooth network parser object """
    
    def __init__(self, network):             
        """ Custom ClickBooth network init """
        
        super(ClickBoothSpyder, self).__init__(network)
        target_date_info = (self.now.date().__str__(), 
                            self.now.date().__str__())
        self.data_url = self.data_url % target_date_info
    
    def parse_data(self, html_data, account):
        """ Custom ClickBooth network parser 
            Available fields in report :
            Program Name         0
            Impressions            1
            Clicks                2
            Sales                3
            Leads                4
            Total Orders        5
            Sales                6 - $0.00 
            Commissions            7
            CTR                8
            CR                    9
            EPC                    10
        
        NOTE - Where is payout?
        
        """
        
        soup = BeautifulSoup(html_data)
        report_lines = soup.find('table', {'id': '1001'}).findAll('tbody'
                                                            )[0].findAll('tr')
        for tr in report_lines:
            td = tr.findAll('td')
            if len(td) == 1:
                return
            
            link = td[0].font.a
            if not link or not link.string:
                continue

            offer_num = re.search('program_id=(?P<offer_id>\d+)&', link['href']
                                                            ).group('offer_id')
            offer = self.get_offer(offer_num, account)
            if not offer:
                continue
            
            record = {
                'campaign': link.string,
                'impressions': td[1].font.string,
                'clicks': td[2].font.string,
                'CTR': td[8].font.string[:-1],
                'EPC': 0 if td[10].font.string == 'N/A' else \
                                                        td[10].font.string[1:],
                'payout': 0.00,
                'status':'',
                'revenue': td[7].font.string[1:],        
#                'leads': td[3].font.string[1:], 
            }
            self.update_earnings(offer, record)
            
            
class CopeacSpyder(BaseDataSpyder):
    """ Custom Copeac network parser object """
    """ ANKNOWN PROBLEM WITH LOGIN FORM SUBMIT This Spyder isn't ready yet and 
        it currently don't using """

    def login(self, account):
        """ This method should login to ads site via login_url and get data_html
            from it that should be parsed via parse_data. Taken data will be 
            saved in database via save_earnings"""
        
        br = mechanize.Browser()
        # Browser options
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        
        br.open(self.login_url)        
        br.select_form(**self.login_form_selector)
        br.form.find_control('password').__dict__['name'] = 'txtPassword'
        br.form.find_control('submit').__dict__['name'] = 'btnSubmit'
        br.form.new_control('hidden', '__EVENTARGUMENT', {'value': u''})
        br.form.new_control('hidden', '__EVENTTARGET', {'value': u''})
        br.form[self.login_key] = account.user_id
        br.form['txtPassword'] = account.password
        br.submit(coord=[21, 4])
        return br
    
    def get_data(self, br):
        """ Custom Copeac network get data method """
        
        br.open(self.data_url)
        br.select_form(nr=0)
        br.find_control("ctl00$mainContent$lstAlias").get("2515"
                                                          ).selected = True
        br.find_control("ctl00$mainContent$SelectAlias").get("rdoSelectAlias"
                                                             ).selected = True
        br.form.new_control('hidden', '__EVENTARGUMENT', {'value': u''})
        br.form.new_control('hidden', '__EVENTTARGET', {'value': u''})
        br.find_control("ctl00$mainContent$hfLocalToUTCTimeDiffInMin"
                                                        ).readonly = False 
        br.form.find_control('ctl00$ctrlNavigation$btnSearch'
                        ).__dict__['name'] = 'ctl00$mainContent$imgbtnSearch'

#        br.find_control("ctl00$mainContent$ddlDateRange").get("YD").selected = True  ### LOCAL HACK
#        br.form['ctl00$mainContent$hfLocalToUTCTimeDiffInMin']=u'-180' ## THIS MAY BE NEADED IN POST  

        response = br.submit(coord=[34,13])
        return response.read() 
        
    
    def parse_data(self, html_data, account):
        """ Custom Copeac network parser.
            Available fields in report :
            Offer ID    0
            Offer Name   1 
            Imp.        2
            Clicks    3
            CTR        4
            Conv.        5 ??
            Conv. %    6 ??
            Rev.        7
            EPC        8
            Avg.CPA    9 ??
            
        """

        soup = BeautifulSoup(html_data)
        content_table = soup.find('table', {'id': 'ctl00_mainContent_gvReport'})
        if not content_table:
            return
                                
        for tr in content_table.findAll('tr'):
            td = tr.findAll('td')
            if not td or not td[0].a  :
                continue
            
            offer_num = td[0].a.string            
            offer = self.get_offer(offer_num, account)
            if not offer:
                continue
            
            record = {
                        'campaign': td[1].a.string,
                        'impressions': int(td[2].a.string),
                        'clicks': int(td[3].a.string),
                        'CTR': td[4].a.string[:-1],
                        'EPC': td[8].a.string[1:],
                        'revenue': td[7].a.string[1:],
                        'payout': '0.00', ## ?????
                        'status': '',
#                        'qualified_transactions': int(td[9].string),
#                        'aproved': int(td[10].string),
#                        'aprovedCTR': aprovedCTRblock.string[:-2],
#                        'eCPM': td[13].string[1:],
                        }                        
            self.update_earnings(offer, record)