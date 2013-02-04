from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
import requests
from requests.exceptions import ConnectionError

from momonitor.main.models import Service,ServiceCheck
from momonitor.main.constants import STATUS_GOOD,STATUS_BAD

class Command(BaseCommand):

    def handle(self, *args, **options):        
        for service in Service.objects.all():
            for check in service.all_checks():
                check.update_status()
