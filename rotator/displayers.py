import mechanize
from BeautifulSoup import BeautifulSoup
import datetime
import re
import logging

SITES_MAP = {
    'jumptap.com': {
        'username_key': 'username',
        'password_key': 'password',
        'username': 'benb24', 
        'password': 'busby123',
        'loginurl': 'https://www.jumptap.com/cas-1.0/login?service=https%3A%2F%2Fppc.jumptap.com%2Ftapmatch31%2Fj_spring_cas_security_check',
        'login_form_selector': {'nr': 0},
        'url': 'https://ppc.jumptap.com/tapmatch31/listCampaign.html',        
        #table id="campaigns" class="tblManageList"
    },
    'admob.com': {
        'username_key': 'email',
        'password_key': 'password',
        'username': 'Ryanwessels21@yahoo.com', 
        'password': 'proballer25',
        'loginurl': 'http://www.admob.com/',
        'login_form_selector': {'nr': 0},
        'url': 'http://www.admob.com/campaigns/?start_date=%s&end_date=%s',
        'ajax_url': 'http://www.admob.com/campaigns/view/ajax_stats?ids[]='
    },
    'inmobi.com': {
        'username_key': 'username',
        'password_key': 'passWd',
        'username': 'benb24@gmail.com', 
        'password': 'busby123',
        'loginurl': 'https://www.inmobi.com/advertiser/Login.html',
        'login_form_selector': {'name': 'loginForm'},
        'url': 'https://www.inmobi.com/advertiser/reports.html',
        'ajax_url': "https://www.inmobi.com/advertiser/tablereports.html?page=1&rp=1000&sortname=cost&sortorder=desc",
        #'url': 'https://www.inmobi.com/advertiser/tablereports.html?page=1&rp=50&sortname=cost&sortorder=desc',
    },
    'moolah-media.com': {
        'username_key': 'mail',
        'password_key': 'pass', 
        'username': 'benb24@gmail.com',
        'password': 'busby123',       
        'loginurl': 'http://moolah-media.com/login.php',
        'login_form_selector': {'name': 'form_'},
        'url': 'http://publisher.moolah-media.com/xhr/affiliate.report.php?datefromtime=%s&datetotime=%s&unix_timestamp=0&link_id=all_links&sub_id=0'
    } 
}


class Displayer:
    def __init__(self, site):
        self.params = SITES_MAP[site].copy()
        self.br = mechanize.Browser()
        self.br.set_debug_responses(True)
        self.br.set_debug_redirects(True)
        self.br.set_handle_robots(False)
    
    def getSoup(self):
        self.br.open(self.params['loginurl']) 
        self.br.select_form(**self.params['login_form_selector'])
        #self.br.form.new_control('text', self.params['username_key'], {'value': self.params['username']})
        #self.br.form.new_control('text', self.params['password_key'], {'value': self.params['password']})
        self.br[self.params['username_key']] = self.params['username']
        self.br[self.params['password_key']] = self.params['password']
        self.br.submit()
        
        return BeautifulSoup(self.br.open(self.params['url']).read())

    def run(self):
        return self.getSoup()
    

class JumptapDisplayer(Displayer):   
    pass


class AdmobDisplayer(Displayer):
    def __init__(self, site):
        Displayer.__init__(self, site)
        d = str(datetime.date.today().strftime("%Y-%m-%d"))
        self.params['url'] = self.params['url'] % (d, d)
        
    def run(self):
        soup = self.getSoup()
        table = soup.find('table', {'class':'altRowTable '})
        offers  = {}
        for tr in table.find('tbody').findAll('tr'):
            td = tr.findAll('td')
            s = str(tr)
            m = re.compile(r'.*rel="(.*)" class.*').search(s)
            if m:
                key = m.groups()[0]
                print td[3]
                offers[key] = {
                    'Campaign': td[1].strong.a.string,
                    'Created': td[2].string,
                    'Status': td[3].div['alt'],
                    'Budget': td[4].string
                }
            
        ids = offers.keys()
        response = self.br.open(self.params['ajax_url'] + "&ids[]=".join(ids))
        
        data = eval(response.read())
        
        content = """<table width='100%' border='1'><tr><th>Campaign</th><th>Created</th><th>Status</th>
            <th>Budget</th><th>Avg. CPC</th><th>Impressions</th><th>Clicks</th><th>CTR</th><th>Cost</th></tr>"""
        for id in ids:
            offers[id]['Avg. CPC'] = data['s'][id][0]
            offers[id]['Cost'] = data['s'][id][1]
            offers[id]['Impressions'] = data['s'][id][4]
            offers[id]['Clicks'] = data['s'][id][3]
            offers[id]['CTR'] = data['s'][id][2]
            content += """<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                <td>%s</td><td>%s</td></tr>""" % (offers[id]['Campaign'], offers[id]['Created'], 
                offers[id]['Status'], offers[id]['Budget'], offers[id]['Avg. CPC'], offers[id]['Impressions'],
                offers[id]['Clicks'], offers[id]['CTR'], offers[id]['Cost'])
        content += "</table>"    

        return content


class InmobiDisplayer(Displayer):
    def run(self):
        soup = self.getSoup()
        self.br.select_form(nr=1)
        self.br.form.controls[3].readonly = False
        self.br['timefilter'] = 'last3months'
        response = self.br.submit()
        #response = self.br.open(self.params['ajax_url'])
        return str(response.read())


class MoolahDisplayer(Displayer):
    def __init__(self, site):
        Displayer.__init__(self, site)
        d = str(datetime.date.today().strftime("%m/%d/%Y"))
        self.params['url'] = self.params['url'] % (d, d)
        
        
        

      
    