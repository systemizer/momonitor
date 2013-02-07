from django.core.management.base import BaseCommand, CommandError
from momonitor.main.models import Service
import logging
import croniter
import time

class Command(BaseCommand):
    '''Call update_status on all checks for all services'''
    def handle(self, *args, **options):        
        now = time.time()
        for service in Service.objects.all():
            try:
                for check in service.all_checks():
                    if croniter.croniter(check.frequency,now).get_next()-now<=60:
                        logging.debug("Cron matched. running check %s" % check.name)
                        check.update_status()
                    else:
                        logging.debug("Cron didn't match. not running check %s" % check.name)
            except:
                logging.error("Failed to parse cron on check %s" % check.name)
                continue
