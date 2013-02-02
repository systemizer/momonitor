from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
import requests
from requests.exceptions import ConnectionError

from momonitor.main.models import Service,ServiceCheck
from momonitor.main.constants import STATUS_GOOD,STATUS_BAD

class Command(BaseCommand):

    def handle(self, *args, **options):
        
        for service in Service.objects.all():
            for service_check in ServiceCheck.objects.filter(service=service):
                service_check.update_status()
