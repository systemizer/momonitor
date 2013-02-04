from django.db import models
import logging
from django.core.cache import cache
import urllib
from django.conf import settings
from main.constants import STATUS_UNKNOWN,STATUS_GOOD,STATUS_BAD
import requests
import json
import time

class InvalidStatusException(Exception):
    pass

class Service(models.Model):
    resource_name="service"

    name = models.CharField(max_length=256)
    pagerduty_key = models.CharField(max_length=128,blank=True,null=True)

    def __unicode__(self):
        return self.name

    @property
    def status(self):
        return STATUS_BAD if [check for check in self.all_checks() if check.status!=STATUS_GOOD] else STATUS_GOOD

    def status_counts(self):
        all_checks = self.all_checks()
        return "%s/%s/%s" % (len(filter(lambda x: x.status==STATUS_GOOD,all_checks)),
                             len(filter(lambda x: x.status==STATUS_BAD,all_checks)),
                             len(filter(lambda x: x.status==STATUS_UNKNOWN,all_checks))
                             )
                             

    @property
    def last_updated(self):
        all_checks = self.all_checks();
        if all_checks:
            return min(self.all_checks(),key=lambda x:x.last_updated).last_updated
        else:
            time.time()

    def all_checks(self):
        return list(self.simpleservicecheck.all()) + \
            list(self.umpireservicecheck.all())

class ServiceCheck(models.Model):
    resource_name="servicecheck"
    class Meta:
        abstract=True

    name = models.CharField(max_length=256)
    description = models.TextField()    
    service = models.ForeignKey(Service,related_name="%(class)s")

    def __unicode__(self):
        return "%s: %s" % (self.service.name,self.name)

    @property
    def status(self):        
        if not cache.has_key(self.redis_key):
            return STATUS_UNKNOWN
        last_updated,status,last_value = cache.get(self.redis_key).split("///")
        return int(status)

    @property
    def last_updated(self):
        if not cache.has_key(self.redis_key):
            return None
        last_updated,status,last_value = cache.get(self.redis_key).split("///")        
        return float(last_updated)

    @property
    def last_value(self):
        if not cache.has_key(self.redis_key):
            return None
        last_updated,status,last_value = cache.get(self.redis_key).split("///")        
        return last_value

    def send_alert(self):
        if not self.service.pagerduty_key:
            logging.info("No pagerduty key for service %s. Not sending alert." % self.service.pagerduty_key)
            return

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

    @property
    def redis_key(self):
        return "%s:::%s" % (self.resource_name,self.id)

    def update_status(self):
        raise NotImplemented("need to implement update_stats")



class SimpleServiceCheck(ServiceCheck):
    resource_name="simpleservicecheck"

    endpoint = models.URLField(max_length=256,null=True,blank=True)

    def update_status(self):
        try:
            res = requests.get(self.endpoint)
            value = res.text
            if res.status_code==200:
                status = STATUS_GOOD
            else:
                self.send_alert()
                status = STATUS_BAD
        except requests.exceptions.ConnectionError:
            self.send_alert()
            value = "Error connecting"
            status = STATUS_UNKNOWN

        cache.set(self.redis_key,
                  "%s///%s///%s" % (time.time(),status,value),
                  timeout=-1)

class UmpireServiceCheck(ServiceCheck):
    resource_name="umpireservicecheck"    

    umpire_metric = models.CharField(max_length=256,null=True,blank=True)
    umpire_min = models.FloatField(null=True,blank=True)
    umpire_max = models.FloatField(null=True,blank=True)
    umpire_range = models.IntegerField(null=True,blank=True)

    def graphite_url(self):
        return "%s/render/?min=0&width=570&height=350&from=-1h&target=%s" % (settings.GRAPHITE_ENDPOINT,self.umpire_metric)

    def update_status(self):
        get_parameters = {
            'metric':self.umpire_metric,
            'min':self.umpire_min,
            'max':self.umpire_max,
            'range':self.umpire_range
            }
        endpoint = "%s?%s" % (settings.UMPIRE_ENDPOINT,
                              urllib.urlencode(get_parameters))
        try:
            res = requests.get(endpoint)
            res_data = res.json()
            if res.status_code == 200:                
                value = res.json()['value']
                status = STATUS_GOOD
            else:
                if res_data.has_key("value"):
                    value = res_data['value']
                elif res_data.has_key("error"):
                    value = res_data['error']
                else:
                    value = "something went wrong"

                status = STATUS_BAD
                self.send_alert()
        except requests.exceptions.ConnectionError:
            self.send_alert()
            value = "Error connecting"
            status = STATUS_UNKNOWN

        cache.set(self.redis_key,
                  "%s///%s///%s" % (time.time(),status,value),
                  timeout=-1)
