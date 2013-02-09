from django.core.management.base import BaseCommand, CommandError
from momonitor.main.models import *

class Command(BaseCommand):
    ''' Sets umpire_range, failures_before_alert, and frequency to nothing if it equals the service value (default) '''
    def handle(self, *args, **options):
        for service in Service.objects.all():
            for check in service.all_checks():
                try:
                    if check.failures_before_alert == service.failures_before_alert:
                        check.failures_before_alert = None
                    if check.frequency == service.frequency:
                        check.frequency = None
                    if type(check) == UmpireServiceCheck and check.umpire_range == service.umpire_range:
                        check.umpire_range = None

                    check.save()
                except Exception:
                    self.stdout.write("Failed to update check %s" % check.name)
                    continue
