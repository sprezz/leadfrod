from django.core.management.base import BaseCommand, CommandError
from rotator.models import Offer


class Command(BaseCommand):
    def handle(self, *args, **options):
        Offer.clear_submits_today()
  
            
