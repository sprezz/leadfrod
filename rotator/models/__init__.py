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
from csv_file import CSVFile
