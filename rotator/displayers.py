import mechanize
from BeautifulSoup import BeautifulSoup


SITES_MAP = {
    'jumptap.com': {
        'username_key': 'username',
        'password_key': 'password',
        'username': 'benb24', 
        'password': 'busby123',
        'loginurl': 'https://www.jumptap.com/cas-1.0/login?service=https%3A%2F%2Fppc.jumptap.com%2Ftapmatch31%2Fj_spring_cas_security_check',
        'login_form_selector': {'nr':0},
        'url': 'https://ppc.jumptap.com/tapmatch31/listCampaign.html',        
        #table id="campaigns" class="tblManageList"
    },
    'admob.com': {
        'username_key': 'email',
        'password_key': 'password',
        'username': 'Ryanwessels21@yahoo.com', 
        'password': 'proballer25',
        'loginurl': 'http://www.admob.com/',
        'login_form_selector': {'nr':0},
        'url': 'http://www.admob.com/campaigns/',
        #table class="altRowTable "
    },
    'inmobi.com': {
        'username_key': 'username',
        'password_key': 'passWd',
        'username': 'benb24@gmail.com', 
        'password': 'busby123',
        'loginurl': 'https://www.inmobi.com/advertiser/Login.html',
        'login_form_selector': {'name':'loginForm'},
        'url': 'https://www.inmobi.com/advertiser/tablereports.html?page=1&rp=50&sortname=cost&sortorder=desc',
    },
    'moolah-media.com': {
        
    } 
}


class Displayer:
    def __init__(self, site):
        self.params = SITES_MAP[site]
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
    def run(self):
        soup = self.getSoup()
        content = ''
        for link in soup.findAll('link'):
            content += str(link)
        content += str(soup.find('table', {'class':'altRowTable '}))
        """
        url = "http://www.admob.com/campaigns/view/ajax_stats?ids%5B%5D=a14db3791010f67&ids%5B%5D=a14db5eb624d120&ids%5B%5D=a14db65fa1d1063&ids%5B%5D=a14dbdd7b8e0cdf&ids%5B%5D=a14dbe00398890c"
        response = self.br.open(url)
        content = response.read()
        """
        return content


class InmobiDisplayer(Displayer):
    pass


class MoolahDisplayer(Displayer):
    pass

      
    