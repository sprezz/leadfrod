# -*- coding:utf-8 -*-
from django.contrib import admin

from rotator.admin.account import AccountAdmin
from rotator.admin.account_api import AccountAPIAdmin
from rotator.admin.advertiser import AdvertiserAdmin
from rotator.admin.company import CompanyAdmin
from rotator.admin.csv_file import CSVFileAdmin
from rotator.admin.earnings import EarningsAdmin
from rotator.admin.lead import LeadAdmin
from rotator.admin.manual_queue import ManualQueueAdmin
from rotator.admin.network import NetworkAdmin
from rotator.admin.niche import NicheAdmin
from rotator.admin.offer import OfferAdmin
from rotator.admin.offer_queue import OfferQueueAdmin
from rotator.admin.proxy_server import ProxyServerAdmin
from rotator.admin.unknown_offer import UnknownOfferAdmin

from rotator.models.account import Account
from rotator.models.account_api import AccountAPI
from rotator.models.advertiser import Advertiser
from rotator.models.advertiser_account_capacity import AdvertiserAccountCapacity
from rotator.models.capacity import Capacity
from rotator.models.company import Company
from rotator.models.csv_file import CSVFile
from rotator.models.earnings import Earnings
from rotator.models.ip_solution import IPSolution
from rotator.models.lead import Lead
from rotator.models.lead_source import LeadSource
from rotator.models.manual_queue import ManualQueue
from rotator.models.network import Network
from rotator.models.niche import Niche
from rotator.models.offer import Offer
from rotator.models.offer_queue import OfferQueue
from rotator.models.owner import Owner
from rotator.models.proxy_server import ProxyServer
from rotator.models.trafficholder_order import TrafficHolderOrder
from rotator.models.unknown_offer import UnknownOffer
from rotator.models.work_manager import WorkManager
from rotator.models.worker_profile import WorkerProfile


admin.site.register(ProxyServer, ProxyServerAdmin)
admin.site.register(ManualQueue, ManualQueueAdmin)
admin.site.register(AccountAPI, AccountAPIAdmin)
admin.site.register(Niche, NicheAdmin)
admin.site.register(LeadSource)
admin.site.register(CSVFile, CSVFileAdmin)
admin.site.register(WorkManager)
admin.site.register(Owner)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(AdvertiserAccountCapacity)
admin.site.register(Advertiser, AdvertiserAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(IPSolution)
admin.site.register(WorkerProfile)
admin.site.register(Capacity)
admin.site.register(Lead, LeadAdmin)
admin.site.register(TrafficHolderOrder)
admin.site.register(UnknownOffer, UnknownOfferAdmin)
admin.site.register(OfferQueue, OfferQueueAdmin)
admin.site.register(Earnings, EarningsAdmin)

