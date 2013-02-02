from django.db import models
from django.core.cache import cache
from main.constants import STATUS_UNKNOWN,STATUS_GOOD,STATUS_BAD
import requests
import time

class InvalidStatusException(Exception):
    pass

class Service(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

    def run_checks(self):
        for service_check in self.service_checks.all():
            service_check.update_status()
    
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

    def update_status(self):
        try:
            res = requests.get(self.endpoint)
            if res.status_code==200:
                value = STATUS_GOOD
            else:
                value = STATUS_BAD
        except requests.exceptions.ConnectionError:
            value = STATUS_UNKNOWN

        cache.set(self.redis_key,
                  "%s-%s" % (time.time(),value),
                  timeout=-1)        
