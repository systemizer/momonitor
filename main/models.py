from django.db import models
import logging
from django.core.cache import cache
import urllib
from django.conf import settings
from main.constants import (STATUS_UNKNOWN,
                            STATUS_GOOD,
                            STATUS_BAD,
                            SERIALIZATION_CHOICES,
                            COMPARATOR_CHOICES)
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
        all_checks = self.all_checks()
        if filter(lambda x: x.status==STATUS_BAD,all_checks):
            return STATUS_BAD
        elif filter(lambda x: x.status==STATUS_UNKNOWN,all_checks):
            return STATUS_UNKNOWN
        else:
            return STATUS_GOOD

    @property
    def last_updated(self):
        if self.all_checks():
            return min(self.all_checks(),key=lambda x:x.last_updated).last_updated
        else:
            return None

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
    frequency = models.CharField(max_length=128,default="*/5 * * * *") #cron format
    failures_before_alert = models.IntegerField(default=1)

    def __unicode__(self):
        return "%s: %s" % (self.service.name,self.name)

    @property
    def _redis_key(self):
        return "%s:::%s" % (self.resource_name,self.id)

    def _get_state(self):
        try:
            return json.loads(cache.get(self._redis_key))
        except Exception:
            return {}

    def set_state(self,status,last_updated,last_value,num_failures):
        state = {'status':status,
                 'last_updated':last_updated,
                 'last_value':last_value,
                 'num_failures':num_failures}
        cache.set(self._redis_key,json.dumps(state))

    @property
    def status(self):        
        return self._get_state().get("status",STATUS_UNKNOWN)

    @property
    def last_updated(self):
        return self._get_state().get("last_updated",None)

    @property
    def last_value(self):
        return self._get_state().get("last_value",None)

    @property
    def num_failures(self):
        return self._get_state().get("num_failures",0)

    def send_alert(self):
        if not self.silenced:
            self.service.send_alert(self.description or self.name)
        else:
            logging.info("Triggered alert on %s, but it is silenced" % self.name)

    def update_status(self):
        raise NotImplemented("need to implement update_stats")

class SimpleServiceCheck(ServiceCheck):
    resource_name="simpleservicecheck"

    endpoint = models.URLField(max_length=256)
    timeout = models.IntegerField(null=True,blank=True) # in ms

    def update_status(self):
        value = None
        status = STATUS_UNKNOWN

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
            value = "Error connecting"
            status = STATUS_BAD
        except requests.exceptions.Timeout:
            value = "Timeout"
            status = STATUS_BAD

        num_failures = self.num_failures+1 if status==STATUS_BAD else 0
        last_updated = self.last_updated if status==STATUS_UNKNOWN else time.time()
        if num_failures>=self.failures_before_alert:
            self.send_alert()

        self.set_state(status=status,
                       last_updated=last_updated,
                       last_value=value,
                       num_failures = num_failures
                       )

class UmpireServiceCheck(ServiceCheck):
    resource_name="umpireservicecheck"    

    umpire_metric = models.CharField(max_length=256)
    umpire_min = models.FloatField()
    umpire_max = models.FloatField()
    umpire_range = models.IntegerField(default=300)

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
        value = None
        status = STATUS_UNKNOWN

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
                    status = STATUS_BAD
                else:
                    logging.error("Error fetching value from umpire: %s" % endpoint)
                    value = self.last_value
                    status = STATUS_UNKNOWN

        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            logging.error("Umpire is down?!?")
            status = STATUS_UNKNOWN

        try:
            if value!=None:
                value = round(float(value),2) #round to 2 decimal places for now
        except ValueError:
            logging.error("Failed at converting value %s to rounded float" % value)
            value = None

        num_failures = self.num_failures+1 if status==STATUS_BAD else 0
        last_updated = self.last_updated if status==STATUS_UNKNOWN else time.time()
        if num_failures>=self.failures_before_alert:
            self.send_alert()

        self.set_state(status=status,
                       last_updated=last_updated,
                       last_value=value,
                       num_failures = num_failures
                       )

'''
This check looks at a specific field in a 
serialized response and applies an arithmatic 
check to that value
'''
class CompareServiceCheck(ServiceCheck):
    resource_name="compareservicecheck"    

    endpoint = models.URLField(max_length=256)
    serialization = models.CharField(max_length=128,choices=SERIALIZATION_CHOICES,default="json")
    field = models.CharField(max_length=256)
    comparator = models.CharField(max_length=128,choices=COMPARATOR_CHOICES,default="==")
    compared_value = models.CharField(max_length=512)

    @property
    def last_value(self):
        last_value = super(CompareServiceCheck,self).last_value
        try:
            return round(float(last_value),2)
        except:
            return last_value

    def update_status(self):        
        value = None
        status = STATUS_UNKNOWN

        try:
            res = requests.get(self.endpoint)
            if res.status_code!=200:
                status = STATUS_BAD
            else:
                if self.serialization=="json":
                    res_data = res.json()
                    for subfield in self.field.split("."):
                        if not res_data.has_key(subfield):
                            logging.error("Bad field path for check %s and field path %s" % (self.name,self.field))
                            status = STATUS_BAD
                            res_data = None
                            break
                        res_data = res_data[subfield]

                elif self.serialization=="plaintext":
                    res_data = res.text
                    
                try:
                    #attempt to cast as float 
                    value = float(res_data)
                except ValueError:
                    value = res_data

                if self.comparator == "==":
                    status = STATUS_GOOD if value == self.compared_value else STATUS_BAD
                elif self.comparator == "!=":
                    status = STATUS_GOOD if value != self.compared_value else STATUS_BAD
                elif self.comparator == ">":
                    status = STATUS_GOOD if value > self.compared_value else STATUS_BAD
                elif self.comparator == ">=":
                    status = STATUS_GOOD if value >= self.compared_value else STATUS_BAD
                elif self.comparator == "<":
                    status = STATUS_GOOD if value < self.compared_value else STATUS_BAD
                elif self.comparator == "<=":                    
                    status = STATUS_GOOD if value <= self.compared_value else STATUS_BAD
                else:
                    status= STATUS_BAD

        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            logging.error("Unable to connect to the server")            
            status = STATUS_BAD

        num_failures = self.num_failures+1 if status==STATUS_BAD else 0
        last_updated = self.last_updated if status==STATUS_UNKNOWN else time.time()
        if num_failures>=self.failures_before_alert:
            self.send_alert()
            
        self.set_state(status=status,
                       last_updated=last_updated,
                       last_value=value,
                       num_failures = num_failures
                       )
