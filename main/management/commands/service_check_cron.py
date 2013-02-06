from django.core.management.base import BaseCommand, CommandError
from momonitor.main.models import Service

class Command(BaseCommand):
    '''Call update_status on all checks for all services'''
    def handle(self, *args, **options):        
        for service in Service.objects.all():
            for check in service.all_checks():
                check.update_status()
