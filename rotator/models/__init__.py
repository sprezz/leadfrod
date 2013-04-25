# -*- coding:utf-8 -*-
ACTIVE = 'active'
BANNED = 'banned'
PAUSED = 'paused'
SUSPICIOUS = 'suspicious'
DELETED = 'deleted'

STATUS_LIST = (
    (ACTIVE, ACTIVE),
    (BANNED, BANNED),
    (PAUSED, PAUSED),
    (SUSPICIOUS, SUSPICIOUS),
    (DELETED, DELETED),
)

AWAITING_APPROVAL = 'awaiting approval'
DEPLETED = 'depleted'
TRAFFIC_HOLDER_STATUS_LIST = (
    (AWAITING_APPROVAL, AWAITING_APPROVAL),
    (ACTIVE, ACTIVE),
    (PAUSED, PAUSED),
    (DELETED, DELETED),
    (DEPLETED, DEPLETED),
)


PAYMENT_TYPE_LIST = (
    ('CHECK', 'CHECK'),
    ('WIRE/ACH', 'WIRE/ACH'),
    ('PAYPAL', 'PAYPAL'),
)


class WorkerProfileDoesNotExistException(Exception):
    pass


class WorkerNotOnlineException(Exception):
    pass


class WorkInterceptedException(Exception):
    pass


class NoWorkException(Exception):
    pass


from .account import Account
from .account_api import AccountAPI
from .advertiser import Advertiser
from .advertiser_account_capacity import AdvertiserAccountCapacity
from .capacity import Capacity
from .company import Company
from csv_file import CSVFile
from .daily_cap import DailyCap
from .earnings import Earnings
from .ip_solution import IPSolution
from .lead import Lead
from .lead_source import LeadSource
from .lead_source_offer_exclusion import LeadSourceOfferExclusion
from .manual_queue import ManualQueue
from .network import Network
from .niche import Niche
from .offer import Offer
from .offer_clicks import OfferClicks
from .offer_queue import OfferQueue
from .owner import Owner
from .proxy_server import ProxyServer
from .trafficholder_order import TrafficHolderOrder
from .unknown_offer import UnknownOffer
from .work_manager import WorkManager
from .worker_profile import WorkerProfile

