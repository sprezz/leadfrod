""" """
from django.core.management.base import BaseCommand
from django.utils.importlib import import_module

from rotator.models import Network
from rotator import spyder_objects
from rotator.spyder_objects import NETWORKS_MAP


class Command(BaseCommand):

    """ Custom command for importing data from external networks """
    
    def handle(self, *args, **options):   
        """ This method should run every spyder to get all data from networks 
        """
    
        networks = Network.objects.all()
        for net in networks:
            try:    
                spy_class = getattr(spyder_objects, '%sSpyder' % (net.name[0].capitalize() + net.name[1:]))
            except AttributeError:
                continue
            else:
                if net.url in NETWORKS_MAP:                
                    spy_class(net).run_spyder()                
        
        print "Finished."