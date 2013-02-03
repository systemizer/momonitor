from django.db import models
from django.core.cache import cache
from django.conf import settings
from main.constants import STATUS_UNKNOWN,STATUS_GOOD,STATUS_BAD
import requests
import json
import time

class InvalidStatusException(Exception):
    pass

class Service(models.Model):
    name = models.CharField(max_length=256)
    pagerduty_key = models.CharField(max_length=128,blank=True,null=True)

    def __unicode__(self):
        return self.name

    def run_checks(self):        
        for service_check in self.service_checks.all():
            service_check.update_status()

    @property
    def status(self):
        statuses = [check.status for check in self.service_checks.all()]
        return "%s/%s/%s" % (len(filter(lambda x: x==STATUS_GOOD,statuses)),
                             len(filter(lambda x: x==STATUS_BAD,statuses)),
                             len(filter(lambda x: x==STATUS_UNKNOWN,statuses)))

    @property
    def last_updated(self):
        '''TO IMPLEMENT'''
        return time.time()
        
    
class ServiceCheck(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    service = models.ForeignKey(Service,related_name="service_checks")
    endpoint = models.URLField()

    def __unicode__(self):
        return "%s: %s" % (self.service.name,self.name)

    @property
    def redis_key(self):
        return "servicecheck:::%s" % (self.id)
    
    @property
    def status(self):        
        if not cache.has_key(self.redis_key):
            return STATUS_UNKNOWN
        last_updated,status = cache.get(self.redis_key).split("-")
        return int(status)

    @property
    def last_updated(self):
        if not cache.has_key(self.redis_key):
            return None
        last_updated,status = cache.get(self.redis_key).split("-")        
        return float(last_updated)

    def send_alert(self):
        payload = {
            'service_key':self.service.pagerduty_key,
            'event_type':'trigger',
            'description':self.description
            }
        headers = {'content-type': 'application/json'}
        res = requests.post(settings.PAGERDUTY_ENDPOINT,
                            data=json.dumps(payload),
                            headers=headers)

        if not res.status_code==200:
            logging.error("Failed to alert pagerduty of event %s" % self.description)


    def update_status(self):
        try:
            res = requests.get(self.endpoint)
            if res.status_code==200:
                value = STATUS_GOOD
            else:
                self.send_alert()
                value = STATUS_BAD
        except requests.exceptions.ConnectionError:
            self.send_alert()
            value = STATUS_UNKNOWN

        cache.set(self.redis_key,
                  "%s-%s" % (time.time(),value),
                  timeout=-1)        
