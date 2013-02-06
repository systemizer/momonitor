from django.db import models
import logging
from django.core.cache import cache
import urllib
from django.conf import settings
from main.constants import (STATUS_UNKNOWN,
                            STATUS_GOOD,
                            STATUS_BAD)
import requests
import json
import time

class Service(models.Model):
    resource_name="service"

    name = models.CharField(max_length=256)
    pagerduty_key = models.CharField(max_length=128,blank=True,null=True)

    def __unicode__(self):
        return self.name

    @property
    def status(self):
        return STATUS_BAD \
            if filter(lambda x: x.status==STATUS_BAD or x.status==STATUS_UNKNOWN,self.all_checks()) \
            else STATUS_GOOD

    @property
    def last_updated(self):
        if self.all_checks():
            return min(self.all_checks(),key=lambda x:x.last_updated).last_updated
        else:
            time.time()

    def status_counts(self):
        all_checks = self.all_checks()
        return "%s/%s/%s" % (len(filter(lambda x: x.status==STATUS_GOOD,all_checks)),
                             len(filter(lambda x: x.status==STATUS_BAD,all_checks)),
                             len(filter(lambda x: x.status==STATUS_UNKNOWN,all_checks))
                             )

    def send_alert(self,description,event_type="trigger"):
        if not self.pagerduty_key:
            logging.info("No pagerduty key for service %s. Not sending alert." % self.pagerduty_key)
            return

        if not description:
            description = "no description for this check is provided"
        
        payload = {
            'service_key':self.pagerduty_key,
            'event_type':event_type,
            'description':description
            }

        headers = {'content-type': 'application/json'}
        res = requests.post(settings.PAGERDUTY_ENDPOINT,
                            data=json.dumps(payload),
                            headers=headers)

        if not res.status_code==200:
            logging.error("Failed to alert pagerduty of event %s" % description)

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
    silenced = models.BooleanField(default=False)

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

    @property
    def redis_key(self):
        return "%s:::%s" % (self.resource_name,self.id)

    def send_alert(self):
        if not self.silenced:
            self.service.send_alert(self.description)
        else:
            logging.info("Triggered alert on %s, but it is silenced" % self.name)
            

    def update_status(self):
        raise NotImplemented("need to implement update_stats")

class SimpleServiceCheck(ServiceCheck):
    resource_name="simpleservicecheck"

    endpoint = models.URLField(max_length=256)
    timeout = models.IntegerField(null=True,blank=True) # in ms

    def update_status(self):
        try:
            if self.timeout:
                res = requests.get(self.endpoint,timeout=float(self.timeout)/1000.0)
            else:
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
            status = STATUS_BAD
        except requests.exceptions.Timeout:
            self.send_alert()
            value = "Timeout"
            status = STATUS_BAD

        cache.set(self.redis_key,
                  "%s///%s///%s" % (time.time(),status,value),
                  timeout=-1)

class UmpireServiceCheck(ServiceCheck):
    resource_name="umpireservicecheck"    

    umpire_metric = models.CharField(max_length=256)
    umpire_min = models.FloatField()
    umpire_max = models.FloatField()
    umpire_range = models.IntegerField(default=300)

    @property
    def last_value(self):
        last_value = super(UmpireServiceCheck,self).last_value
        try:
            return round(float(last_value),2)
        except:
            return None

    def graphite_url(self):
        return "%s/render/?min=0&width=570&height=350&from=-3h&target=%s" % (settings.GRAPHITE_ENDPOINT,self.umpire_metric)

    def status_progress(self):
        if not self.last_value:
            return 0

        if self.last_value<self.umpire_min:
            return 0
        elif self.last_value>self.umpire_max:
            return 100
        else:
            return (self.last_value-self.umpire_min)/(self.umpire_max-self.umpire_min)*100

    def update_status(self):
        get_parameters = {
            'metric':self.umpire_metric,
            'min':self.umpire_min,
            'max':self.umpire_max,
            'range':self.umpire_range
            }
        endpoint = "%s?%s" % (settings.UMPIRE_ENDPOINT,
                              urllib.urlencode(get_parameters))

        value = None
        status = None
        try:
            res = requests.get(endpoint)
            res_data = res.json()
            if res.status_code == 200:                
                value = res.json()['value']
                status = STATUS_GOOD
            else:
                if res_data.has_key("value"):
                    value = res_data['value']
                else:
                    logging.error("Error fetching value from umpire: %s" % endpoint)

                status = STATUS_BAD
                self.send_alert()

        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            logging.error("Umpire is down?!?")
            status = STATUS_UNKNOWN

        cache.set(self.redis_key,
                  "%s///%s///%s" % (time.time(),status,value),
                  timeout=-1)
