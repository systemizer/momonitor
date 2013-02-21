from django.db import models
import logging
from django.template import Context
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.core.mail import send_mail
from smtplib import SMTPException
import pdb
import croniter
from django.core.cache import cache
import urllib
from django.contrib.contenttypes import generic
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from main.constants import (STATUS_UNKNOWN,
                            STATUS_GOOD,
                            STATUS_BAD,
                            ALERT_CHOICES,
                            SERIALIZATION_CHOICES,
                            UMPIRE_CHECK_TYPES,
                            COMPARATOR_CHOICES)
import requests
import json
import time

class Service(models.Model):
    resource_name="service"

    name = models.CharField(max_length=256)
    pagerduty_key = models.CharField(max_length=128,blank=True,null=True)
    email_contact = models.EmailField(null=True,blank=True)

    silenced = models.BooleanField(default=False)


    #Default values if not specified in the check
    frequency = models.CharField(max_length=128,default="*/5 * * * *") #cron format
    failures_before_alert = models.IntegerField(default=1)
    umpire_range = models.IntegerField(default=300)    
    alert_type = models.CharField(max_length=64,choices=ALERT_CHOICES,default="none")

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

    def _status_counts(self,check_type=""):
        all_checks = self.all_checks(check_type)
        return "%s/%s/%s" % (len(filter(lambda x: x.status==STATUS_GOOD,all_checks)),
                             len(filter(lambda x: x.status==STATUS_BAD,all_checks)),
                             len(filter(lambda x: x.status==STATUS_UNKNOWN,all_checks))
                             )

    @property
    def all_counts(self):
        return self._status_counts()

    @property
    def simple_counts(self):
        return self._status_counts(check_type="simpleservicecheck")

    @property
    def code_counts(self):
        return self._status_counts(check_type="codeservicecheck")

    @property
    def umpire_counts(self):
        return self._status_counts(check_type="umpireservicecheck")

    @property
    def compare_counts(self):
        return self._status_counts(check_type="compareservicecheck")

    @property
    def complex_counts(self):
        return self._status_counts(check_type="complexservicecheck")

    def _send_alert_pagerduty(self,description,event_type="trigger"):
        if not self.pagerduty_key:
            logging.info("No pagerduty key for service %s. Not sending alert." % self.name)
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

    def _send_alert_email(self,description):
        if not self.email_contact:
            logging.info("No email contact for service %s" % self.name)
        try:
            email_msg = get_template("alert_email.txt").render(
                Context({"description":description,
                         "service_name":self.name,
                         "url":"%s%s" % (settings.DOMAIN,
                                         reverse("main_service",kwargs={'service_id':self.id}))
                         })
                )
                    
            send_mail("MOMONITOR EVENT TRIGGERED",
                      email_msg,
                      settings.SERVER_EMAIL,
                      [self.email_contact,],
                      fail_silently=False)
        except SMTPException:
            logging.error("Failed to send email to %s for error %s" % (self.email_contact,description))

    def send_alert(self,description,alert_type=None,event_type="trigger"):
        if self.silenced:
            logging.debug("Service %s is silenced. Not sending pagerduty alert %s" % (self.name,description))
            return

        alert_type = alert_type or self.alert_type
        if alert_type == "pagerduty":
            self._send_alert_pagerduty(description,event_type)
        elif alert_type == "email":
            self._send_alert_email(description)
        else:
            logging.info("No alert being sent because alert type is 'none'")
        


    def all_checks(self,check_type=""):
        if check_type == "simpleservicecheck":
            return list(self.simpleservicecheck.all())
        elif check_type == "umpireservicecheck":
            return list(self.umpireservicecheck.all())
        elif check_type == "compareservicecheck":
            return list(self.compareservicecheck.all())
        elif check_type == "complexservicecheck":
            return list(self.complexservicecheck.all())
        elif check_type == "codeservicecheck":
            return list(self.codeservicecheck.all())
        else:
            return list(self.simpleservicecheck.all()) + \
                list(self.umpireservicecheck.all()) + \
                list(self.compareservicecheck.all()) + \
                list(self.complexservicecheck.all()) + \
                list(self.codeservicecheck.all())

    def update_status(self):
        for check in self.all_checks():
            check.update_status()

class ServiceCheck(models.Model):
    resource_name="servicecheck"
    class Meta:
        abstract=True

    name = models.CharField(max_length=256)
    description = models.TextField(null=True,blank=True)    
    service = models.ForeignKey(Service,related_name="%(class)s")
    silenced = models.BooleanField(default=False)
    alert_type = models.CharField(max_length=64,choices=ALERT_CHOICES,null=True,blank=True)
    frequency = models.CharField(max_length=128,null=True,blank=True)
    failures_before_alert = models.IntegerField(null=True,blank=True)

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

    def set_state(self,status,last_value):
        num_failures = self.num_failures+1 if status==STATUS_BAD else 0
        last_updated = self.last_updated if status==STATUS_UNKNOWN else time.time()

        if num_failures>=(self.failures_before_alert or self.service.failures_before_alert):
            self.send_alert()

        state = {'status':status,
                 'last_updated':last_updated,
                 'last_value':last_value,
                 'num_failures':num_failures}

        cache.set(self._redis_key,json.dumps(state),timeout=0)

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
                status = STATUS_BAD

        except requests.exceptions.ConnectionError:
            value = "Error connecting"
            status = STATUS_BAD
        except requests.exceptions.Timeout:
            value = "Timeout"
            status = STATUS_BAD

        self.set_state(status=status,last_value=value)

class UmpireServiceCheck(ServiceCheck):
    resource_name="umpireservicecheck"    

    umpire_metric = models.CharField(max_length=256)
    umpire_min = models.FloatField()
    umpire_max = models.FloatField()
    umpire_range = models.IntegerField(null=True,blank=True)
    umpire_check_type = models.CharField(max_length=64,choices=UMPIRE_CHECK_TYPES,default="static")

    def _update_history(self):
        if self.history_value:
            new_value = self.history_value*.9 \
                + self.last_value*.1
        else:
            new_value = self.last_value

        new_history = {
            'last_value':new_value,
            'last_updated':time.time()
            }
        cache.set(self._history_redis_key,json.dumps(new_history),timeout=60*60*24*7)

    def set_state(self,status,last_value):
        super(UmpireServiceCheck,self).set_state(status,last_value)
        last_history = {
            'last_value':last_value,
            'last_updated':time.time()
            }
        cache.set(self._last_history_redis_key,json.dumps(last_history),timeout=60*60*24*1.2)

    @property
    def history_value(self):
        if not cache.has_key(self._history_redis_key):
            return 0
        return json.loads(cache.get(self._history_redis_key)).get("last_value")

    def history_series(self,num_values=20):
        cur_time = croniter.croniter(self.frequency or self.service.frequency,time.time())
        key_series = ["%s:::%s" % (self._redis_key,(int(cur_time.get_prev()) % (60*60*24)) / 60) for i in range(num_values)]
        value_series = [json.loads(cache.get(key)).get("last_value") if cache.has_key(key) else 0 for key in key_series]
        value_series.reverse()
        value_series.append(self.history_value)
        return value_series

    def last_series(self,num_values=20):
        cur_time = croniter.croniter(self.frequency or self.service.frequency,time.time())
        key_series = ["%s:::%s:::%s" % (self._redis_key,(int(cur_time.get_prev()) % (60*60*24)) / 60,"last") for i in range(num_values)]
        value_series = [json.loads(cache.get(key)).get("last_value") if cache.has_key(key) else 0 for key in key_series]
        value_series.reverse()
        value_series.append(self.last_value)
        return value_series

    @property
    def _history_redis_key(self):
        cur_time = croniter.croniter(self.frequency or self.service.frequency,
                                     time.time()).get_next()
        cur_time = int(cur_time)
        return "%s:::%s" % (self._redis_key,(cur_time % (60*60*24)) / 60)

    @property
    def _last_history_redis_key(self):
        return "%s:::%s" % (self._history_redis_key,"last")

    def graphite_url(self):
        return "%s/render/?min=0&width=570&height=350&from=-3h&target=%s" % (settings.GRAPHITE_ENDPOINT,self.umpire_metric)

    def status_progress(self):
        if self.umpire_check_type=="static":
            return self._status_progress_static()
        else:
            return self._status_progress_dynamic()

    def _status_progress_static(self):
        #MMEEENNNGGG
        if self.umpire_max-self.umpire_min == 0:
            return 0
        return max(
            min(
                (self.last_value-self.umpire_min) / (self.umpire_max-self.umpire_min),
                1
                ),
            0
            )*100

    def _status_progress_dynamic(self):
        min_value = self.history_value*.8
        max_value = self.history_value*1.2
        #MMEEENNNGGG
        if max_value-min_value == 0:
            return 0
        return max(
            min(
                (self.last_value-min_value) / (max_value-min_value),
                1
                ),
            0
            )*100

    def _update_status_static(self):
        return (self.umpire_min,self.umpire_max)

    def _update_status_dynamic(self):
        if not self.history_value:
            #if you have no history, then you should accept all
            return 0,99999999999999999
        return .8*self.history_value,1.2*self.history_value

    def update_status(self):
        value = None
        status = STATUS_UNKNOWN
        
        if self.umpire_check_type=="static":            
            umpire_min,umpire_max = self._update_status_static()
        else:
            umpire_min,umpire_max = self._update_status_dynamic()

        get_parameters = {
            'metric':self.umpire_metric,
            'min':umpire_min,
            'max':umpire_max,
            'range':self.umpire_range or self.service.umpire_range
            }
        endpoint = "%s?%s" % (settings.UMPIRE_ENDPOINT,
                              urllib.urlencode(get_parameters))

        try:
            res = requests.get(endpoint)
            res_data = res.json()
            if res.status_code == 200:                
                value = res_data['value']
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
            value = round(float(value),2) #round to 2 decimal places for now
        except (ValueError,TypeError) as e:
            logging.error("Failed at converting value %s to rounded float" % value)
            value = None

        self.set_state(status=status,last_value=value)
        if status==STATUS_GOOD:
            self._update_history()

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
                status = STATUS_UNKNOWN
            else:
                if self.serialization=="json":
                    res_data = res.json()
                    for subfield in self.field.split("."):
                        if type(res_data) == list:
                            try:
                                subfield = int(subfield)
                                res_data = res_data[subfield]
                            except (ValueError,IndexError):
                                logging.error("Failed to parse json data correctly. Can't index %s in list of length" % (subfield,len(res_data)))
                                status = STATUS_UNKNOWN
                                res_data = None
                                break                            
                            
                        else:
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
                    value = round(float(res_data),2)
                    compared_value = round(float(self.compared_value),2)
                except ValueError:
                    value = res_data
                    compared_value = self.compared_value

                if self.comparator == "==":
                    status = STATUS_GOOD if value == compared_value else STATUS_BAD
                elif self.comparator == "!=":
                    status = STATUS_GOOD if value != compared_value else STATUS_BAD
                elif self.comparator == ">":
                    status = STATUS_GOOD if value > compared_value else STATUS_BAD
                elif self.comparator == ">=":
                    status = STATUS_GOOD if value >= compared_value else STATUS_BAD
                elif self.comparator == "<":
                    status = STATUS_GOOD if value < compared_value else STATUS_BAD
                elif self.comparator == "<=":                    
                    status = STATUS_GOOD if value <= compared_value else STATUS_BAD
                elif self.comparator == "contains":
                    status = STATUS_GOOD if compared_value in value else STATUS_BAD
                else:
                    status= STATUS_BAD

        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            logging.error("Unable to connect to the server")            
            status = STATUS_BAD

        self.set_state(status=status,last_value=value)

class CodeServiceCheck(ServiceCheck):
    resource_name = "codeservicecheck"
    code_file = models.FileField(upload_to="uploaded_scripts")

    @property
    def file_name(self):
        return self.code_file.name.split("/")[-1].replace(".py","")

    def update_status(self):
        value = None
        status = STATUS_UNKNOWN

        try:
            parent_module = __import__("uploaded_scripts.%s" % self.file_name)
            module = eval("parent_module.%s" % self.file_name)
            value,succeeded = module.run()
            status = STATUS_GOOD if succeeded else STATUS_BAD
        except:            
            status = STATUS_UNKNOWN
            value = None
        
        self.set_state(status=status,last_value=value)

class ComplexServiceCheck(ServiceCheck):
    resource_name = "complexservicecheck"

    def update_status(self):
        value = None
        status = STATUS_UNKNOWN

        for check in self.checks.order_by("order"):
            status,value = check.update_status()
            if status==STATUS_BAD:
                break
        
        self.set_state(status=status,last_value=value)

class ComplexRelatedField(models.Model):
    resource_name = "complexrelatedfield"
    complex_check = models.ForeignKey(ComplexServiceCheck,related_name="checks")
    order = models.IntegerField()

    object_type = models.ForeignKey(ContentType, related_name="related_%(class)s")
    object_id = models.IntegerField(db_index=True)
    check = generic.GenericForeignKey(ct_field="object_type", fk_field="object_id")

    class Meta:
        unique_together=(("complex_check","order"),)

RESOURCES = [
    Service,
    ServiceCheck,
    SimpleServiceCheck,
    UmpireServiceCheck,
    CompareServiceCheck,
    CodeServiceCheck,
    ComplexServiceCheck,
    ComplexRelatedField
]

RESOURCE_NAME_MAP = dict([(cls.resource_name,cls) for cls in RESOURCES])
