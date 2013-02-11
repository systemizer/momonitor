from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

from django.core.management.base import BaseCommand, CommandError
from momonitor.main.models import Service
import logging
import croniter
import time


class Command(BaseCommand):
    '''Call update_status on all checks for all services'''
    def handle(self, *args, **options):        
        pool = Pool(size=10)
        now = time.time()
        for service in Service.objects.all():
            try:
                for check in service.all_checks():
                    logging.debug("Cron matched. running check %s" % check.name)
                    pool.spawn(check.update_status)

            except:
                logging.error("Failed to parse cron on check %s" % check.name)
                continue

        pool.join()
