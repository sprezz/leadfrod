from django_extensions.management.jobs import DailyJob
from rotator.models import Offer


class Job(DailyJob):
    help = "Resets all the capacities daily."    
    
    def execute(self):
        for offer in Offer.objects.all():
            offer.restoreDailyCapCapacity()
        Offer.objects.clear_submits_today()