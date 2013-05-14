from django.core.management.base import BaseCommand, CommandError
from rotator.models.offer import Offer


class Command(BaseCommand):
    def handle(self, *args, **options):
        Offer.objects.clear_submits_today()
