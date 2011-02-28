class NoCapacityException:
    pass

def check_offer_advertiser_capacity(offer):
    if not offer.hasAdvertiser() or offer.advertiser.daily_cap==0:
        raise NoCapacityException
    
def check_account_capacity(account):
    if account.daily_cap==0:
        raise NoCapacityException    
