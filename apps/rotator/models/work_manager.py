# -*- coding:utf-8 -*-
import logging
from django.db import models
from django.db.models import F
from django.utils.timezone import now
import re
from rotator.models import ACTIVE, WorkInterceptedException, WorkerNotOnlineException, NoWorkException


class WorkItem(object):
    def __init__(self, workLead=None, workOffers=None):
        self.worker = None
        self.nextLead = None
        self.lead = workLead
        self.pattern = re.compile(r',|;')
        if workOffers is None:
            self.offers = []
        else:
            self.offers = workOffers

    def get_remaining_leads(self):
        from rotator.models.lead import Lead
        count = Lead.unlocked.filter(csv__niche=self.lead.csv.niche, status=ACTIVE, worker__isnull=True, deleted=False).count()
        return count - 1 if count > 0 else 0

    def get_header(self):
        return self.pattern.split(self.lead.csv.csv_headers)#.split(',')

    def get_data(self):
        return self.pattern.split(self.lead.lead_data)#.split(',')

    def format(self, s):
        return s.replace('"', '')

    def get_fields(self):
        fields = []
        data = self.get_data()
        for idx, f in enumerate(self.get_header()):
            try:
                fields.append((self.format(f), self.format(data[idx])))
            except:
                logging.warning("data with key %d is not exit:" % idx)
        return fields

    def addOffer(self, anOffer):
        anOffer.reduceCapacityOnShow()
        self.lead.offers_requested.add(anOffer)
        self.lead.save()
        self.offers.append(anOffer)

    def __str__(self):
        return '%s %s' % (self.lead, self.offers)


class WorkManager(models.Model):
    """Manages work of workers through work strategy"""
    workers_online = models.ManyToManyField('auth.User', null=True, blank=True)

    @staticmethod
    def instance():
        if WorkManager.objects.count() == 0:
            WorkManager().save()
        return WorkManager.objects.get(pk=1)

    class WorkStrategy(object):
        def __init__(self):
            self.remainingLeads = 0

        def nextLead(self, csvFile):
            from rotator.models.lead import Lead
            try:
                csvLeads = Lead.unlocked.filter(csv=csvFile,
                                                status=ACTIVE,
                                                worker__isnull=True,
                                                deleted=False).order_by('?')
                #                csvLeads = Lead.objects.filter(csv=csvFile, status=ACTIVE, worker__isnull=True, deleted=False).order_by('?')
                leadsCount = csvLeads.count()
                if leadsCount == 0:
                    logging.debug('There is no lead available for %s' % csvFile)
                    return None, None
                    #csvLeads = sorted(csvLeads, key=lambda lead: lead.csv.niche.priority)
                logging.debug('Got lead %s' % csvLeads[0])
                return csvLeads[0], csvLeads[1] if leadsCount > 1 else None
            except Lead.DoesNotExist:
                return None, None

        def getOffersForLead(self, wi):
            """
                abudarevsky: how I understood (mayy be wrong) - each Lead goes to advertiser sooner or
                 later but untill it is accepted by an Advertiser it can proposed for different Offers. So once
                 we give the Lead to Advertiser we have to lock Lead not to show for others Offers
                [3:28:48 MSD] rovin.v: so an offer may have an advertiser, at most 1 advertiser
                [3:28:59 MSD] rovin.v: an offer may have 0 or 1 advertisers
                [3:29:04 MSD] abudarevsky: exactly
                [3:29:06 MSD] rovin.v: an advertiser may have 0 or more offers
                [3:29:12 MSD] abudarevsky: exactly
                [3:29:14 MSD] rovin.v: 1 lead can go into X offers
                [3:29:19 MSD] rovin.v: like 5
                [3:29:19 MSD] abudarevsky: true
                [3:29:34 MSD] rovin.v: each of those offers advertisers have to be unique or should be non existent
                [3:29:52 MSD] rovin.v: so like Advertiser A,B,C,no advertiser, no advertiser
                [3:30:04 MSD] rovin.v: it does not have to use every advertiser
                [3:30:13 MSD] rovin.v: it randomly picks 5 offers based on these rules

                 Algo:
                    1. Lead.getNiche
                    2. Get Offers per Niche
                    3.1 Filter out by DailyCap and Status
                    3.2 Filter out by unique assigned advertisers and no advertiser
                    4. Get 5 random from the rest
                    5. Return the list

            """
            from rotator.models.offer import Offer
            from rotator.models.network import Network

            leadNiche = wi.lead.getNiche()
            logging.debug('get offer per niche %s' % leadNiche)
            offers = Offer.objects.filter(niche=leadNiche, status=ACTIVE, capacity__gte=F('payout')).order_by('submits_today')
            logging.info('Found %d offers in niche %s' % (len(offers), leadNiche))
            offer_names = []
            networks = [] # for each lead only one network
            inetworks = Network.objects.filter(single=False)
            i = 0
            for offer in offers:
                if offer.name in offer_names:
                    continue

                if offer.network in networks and offer.network not in inetworks:
                    continue

                i += 1
                check_capacity = offer.checkCapacity()
                #logging.info('offer checking capacity=%d in offer %d: %s' % (int(check_capacity), i, offer.offer_num))
                if not check_capacity:
                    continue

                #logging.info('offer has capacity: %d: %s ' % (i,  offer.offer_num))
                logging.debug('offer has capacity: %s ' % offer)
                hasAdvertiser = offer.hasAdvertiser()
                #logging.info('offer %d: %s has advertiser = %s' % (i, offer.offer_num, hasAdvertiser))
                if hasAdvertiser:
                    if wi.lead.checkAdvertiser(offer.advertiser):
                        print wi.lead, 'already was given to ', offer.advertiser, '. Skipping...'
                        #logging.info('Skipping offer %d: %s because %s was given for lead %s' % (i, offer.offer_num, offer.advertiser, wi.lead.id))
                        logging.debug('%s already was given to %s. Skipping...' % (wi.lead, offer.advertiser))
                        continue
                    wi.lead.advertisers.add(offer.advertiser)
                    wi.lead.save()

                #logging.info('Adding offer %d: %s to resutlt' % (i, offer.offer_num))
                wi.addOffer(offer)
                offer.increase_submits()
                offer.reduce_capacity()
                offer_names.append(offer.name)
                networks.append(offer.network)

                if len(wi.offers) == wi.lead.csv.max_offers:
                    break
            logging.info('Found %d result offers in niche %s' % (len(wi.offers), leadNiche))
            return wi

    work_strategy = WorkStrategy()

    @property
    def getNumberOfOnlineWorkers(self):
        return self.workers_online.count()

    def completeCurrentWorkItem(self, workitem):
        """Set lead in work completed and adds adds stat information"""
        #        lead = self.getLeadInWork(worker)
        if not workitem:
            return
        if not (workitem.lead.is_locked and workitem.lead.is_locked_by(workitem.worker)):
            self.releaseCurrentWorkItem(workitem)
            raise WorkInterceptedException('Lead %s was unlocked or intercepted by another worker due to inactivity' % workitem.lead)
        if workitem.lead.is_locked and workitem.lead.is_locked_by(workitem.worker):
            workitem.lead.unlock_for(workitem.worker)
            workitem.lead.save()
        workitem.lead.status = 'completed'
        for offer in workitem.lead.offers_requested.all():
            workitem.lead.offers_completed.add(offer)
            workitem.lead.offers_requested.remove(offer)

        workitem.lead.save()

    def releaseCurrentWorkItem(self, workitem):
        """Release lead and deassociate lead and offers"""
        print 'Releasing lead', workitem.lead
        if not workitem.lead:
            print 'There are no leads in work for ', workitem.worker
            return
        if workitem.lead.is_locked and workitem.lead.is_locked_by(workitem.worker):
            print 'Unlock for', workitem.worker
            workitem.lead.unlock_for(workitem.worker)
            workitem.lead.save()
        if workitem.lead.worker == workitem.worker:
            workitem.lead.status = ACTIVE
            workitem.lead.worker = None
            for offer in workitem.lead.offers_requested.all():
                workitem.lead.offers_requested.remove(offer)
            workitem.lead.save()
        else:
            logging.debug('Lead %s was unlocked due to inactivity or administrator request' % workitem.lead)

    def unlockLead(self, lead_id, user):
        """Unlock lead and releases associated with it offers"""
        from rotator.models.lead import Lead
        try:
            lead = Lead.objects.get(pk=lead_id)
            if lead.is_locked:
                lead.unlock()
                lead.worker = None
                for offer in lead.offers_requested.all():
                    lead.offers_requested.remove(offer)
                lead.save()
                logging.info('Lead %s was unlocked by %s' % (lead, user))
        except Lead.DoesNotExist:
            logging.debug('Lead %s requested for release but does not exist')

    def checkOrCreateUserProfile(self, user):
        from rotator.models.worker_profile import WorkerProfile
        try:
            user.get_profile()
        except WorkerProfile.DoesNotExist:
            WorkerProfile.objects.create(user=user, status=ACTIVE)

    def signIn(self, worker):
        logging.debug('%s signing in ' % worker)
        wp = worker.get_profile()
        wp.now_online = True
        wp.save()
        self.workers_online.add(worker)
        self.save()

    def validateWorkItem(self, workitem):
        logging.debug('validate %s' % workitem)
        from rotator.models.lead import Lead
        try:
            lead = Lead.objects.get(pk=workitem.lead.id)
            return lead.is_locked and lead.is_locked_by(workitem.worker)
        except:
            return False

    def _checkCsvFileAndSaveIfLeadsCreated(self, csv_file):
        nleads = csv_file.leads.count()
        if not csv_file.hasLeads():
            return False
        if nleads != csv_file.leads.count():
            csv_file.save()
        return True

    def nextWorkItem(self, worker):
        def __nextWorkItem(lead, nextLead):
            exceptionMessage = None
            if not lead.is_locked:
                logging.info('{} - locking the lead'.format(now()))
                lead.lock_for(worker)
                lead.worker = worker
                lead.save()
            else:
                exceptionMessage = "Locked by {} at {}".format(lead.locked_by, lead.locked_at)
                logging.info("{} - {}".format(now(), exceptionMessage))
                return exceptionMessage

            wi = WorkItem(lead)
            wi.worker = worker
            wi.nextLead = nextLead
            wi = self.work_strategy.getOffersForLead(wi)
            logging.info('{} - found {} offers'.format(now(), len(wi.offers)))

            if len(wi.offers) == 0:
                logging.info('{} - unlock lead'.format(now()))
                lead.unlock_for(worker)
                lead.worker = None
                lead.save()
                exceptionMessage = "There are no offers with enough \
                    capacity left for the leads in niche %s and no offer \
                    after advertiser checking" % (lead.getNiche())
                logging.info("{} - {}".format(now(), exceptionMessage))
                return exceptionMessage

            logging.info('{} - before result:: {}'.format(now(), str(wi.__dict__)))
            return wi

        if not worker.get_profile().now_online:
            raise WorkerNotOnlineException()
        logging.debug('%s is online' % worker)
        lead = None
        nextLead = None
        exceptionMessage = False

        from rotator.models.csv_file import CSVFile
        csv_files = CSVFile.objects.filter(workers=worker).order_by('niche__priority')
        logging.info('Founded %d csv files' % len(csv_files))

        for csv_file in csv_files:
            if not self._checkCsvFileAndSaveIfLeadsCreated(csv_file):
                exceptionMessage = "wrong cheking CSV File %s" % csv_file
                logging.info('{} - {}'.format(now(), exceptionMessage))
                continue

            if lead:
                nextLead = self.work_strategy.nextLead(csv_file)
            else:
                logging.info('{} - {} get csv'.format(now(), csv_file))
                lead, nextLead = self.work_strategy.nextLead(csv_file)
                logging.info('{} - Lead instance {}'.format(now(), lead))

            if lead and nextLead:
                wi = __nextWorkItem(lead, nextLead)
                if type(wi) == str:
                    continue
                else:
                    return wi

        logging.info('{} - after loop :: {}'.format(now(), exceptionMessage))
        logging.info('{} - after loop lead:: {}'.format(now(), lead))
        if lead:
            wi = __nextWorkItem(lead, nextLead)
            if type(wi) == str:
                raise NoWorkException(wi)
            else:
                return wi

        if not lead:
            raise NoWorkException("There are no active leads for your account remaining")
        elif exceptionMessage:
            raise NoWorkException(exceptionMessage)

    def signOut(self, worker):
        logging.debug('signing out %s' % worker)
        if not worker.get_profile().now_online:
            raise WorkerNotOnlineException()
        from rotator.models.lead import Lead
        qset = Lead.locked.filter(worker=worker)
        if qset.exists():
            for lead in qset.all():
                lead.unlock_for(worker)
                lead.save()

        wp = worker.get_profile()
        wp.now_online = False
        wp.save()
        self.workers_online.remove(worker)
        self.save()

    class Meta:
        app_label = 'rotator'

    # def __unicode__(self):
    #     return u'WorkManager: %s workers online' % self.getNumberOfOnlineWorkers
