from django.db import models
import logging
import itertools
from django.template import Context
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.core.mail import send_mail
from smtplib import SMTPException
import croniter
from django.core.cache import cache
import urllib
from django.conf import settings
from main.constants import (STATUS_UNKNOWN,
                            STATUS_GOOD,
                            STATUS_BAD,
                            ALERT_CHOICES,
                            SERIALIZATION_CHOICES,
                            UMPIRE_CHECK_TYPES,
                            UMPIRE_RANGE_TYPES,
                            COMPARATOR_CHOICES)
import requests
import json
import time

import pdb

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

    def status_counts(self,check_type=""):
        all_checks = self.all_checks(check_type)
        return "%s/%s/%s" % (len(filter(lambda x: x.status==STATUS_GOOD,all_checks)),
                             len(filter(lambda x: x.status==STATUS_BAD,all_checks)),
                             len(filter(lambda x: x.status==STATUS_UNKNOWN,all_checks))
                             )

    def _send_alert_pagerduty(self,description):
        if not self.pagerduty_key:
            logging.warning("No pagerduty key for service %s. Not sending alert." % self.name)
            return

        payload = {
            'service_key':self.pagerduty_key,
            'event_type':"trigger",
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
            logging.warning("No email contact for service %s" % self.name)
        try:
            title = "{} Service Check Failed: {}".format(self.name, description)
            email_msg = get_template("alert_email.txt").render(
                Context({"description":description,
                         "service_name":self.name,
                         "url":"%s%s" % (settings.DOMAIN,
                                         reverse("main:service",kwargs={'service_id':self.id}))
                         })
                )

            send_mail(title,
                      email_msg,
                      settings.SERVER_EMAIL,
                      [self.email_contact,],
                      fail_silently=False)
        except SMTPException:
            logging.error("Failed to send email to %s for error %s" % (self.email_contact,description))

    def send_alert(self,description,alert_type=None):
        if self.silenced:
            logging.debug("Service %s is silenced. Not sending pagerduty alert %s" % (self.name,description))
            return

        alert_type = alert_type or self.alert_type
        if alert_type == "pagerduty":
            self._send_alert_pagerduty(description)
        elif alert_type == "email":
            self._send_alert_email(description)
        else:
            logging.info("No alert being sent because alert type is 'none'")

    def all_checks(self,check_type=""):
        resource_names = [service_class.resource_name for service_class in ServiceCheck.__subclasses__()]
        if check_type:
            if check_type not in resource_names:
                logging.warning("Could not find check type: %s" % check_type)
                return []
            return list(getattr(self,check_type).all())
        return list(itertools.chain(*[list(getattr(self,name).all()) for name in resource_names]))

    def update_status(self):
        for check in self.all_checks():
            check.update_status()

class ServiceCheck(models.Model):
    resource_name = "servicecheck"
    class Meta:
        abstract=True

    name = models.CharField(max_length=256)
    description = models.TextField(null=True,blank=True)
    service = models.ForeignKey(Service,related_name="%(class)s")
    silenced_until = models.IntegerField(default=0) # This is a timestamp (seconds since unix epoch).
    alert_type = models.CharField(max_length=64,choices=ALERT_CHOICES,null=True,blank=True)
    frequency = models.CharField(max_length=128,null=True,blank=True)
    failures_before_alert = models.IntegerField(null=True,blank=True)

    def __unicode__(self):
        return "%s: %s" % (self.service.name,self.name)

    @property
    def is_silenced(self):
        return time.time() < self.silenced_until

    @property
    def _redis_key(self):
        return "%s:::%s" % (self.resource_name,self.id)

    def _get_state(self):
        try:
            return json.loads(cache.get(self._redis_key))
        except Exception:
            return {}

    def set_state(self,status,last_value,extra={}):
        num_failures = self.num_failures+1 if status==STATUS_BAD else 0
        last_updated = self.last_updated if status==STATUS_UNKNOWN else time.time()

        if num_failures>=(self.failures_before_alert or self.service.failures_before_alert):
            self.send_alert()

        state = {'status':status,
                 'last_updated':last_updated,
                 'last_value':last_value,
                 'num_failures':num_failures}

        state.update(extra)

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
        if not self.is_silenced:
            self.service.send_alert(self.description or self.name, self.alert_type)
        else:
            logging.info("Triggered alert on %s, but it is silenced" % self.name)

    def update_status(self):
        raise NotImplemented("need to implement update_stats")

class SimpleServiceCheck(ServiceCheck):
    resource_name = "simpleservicecheck"
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
    resource_name = "umpireservicecheck"
    umpire_metric = models.CharField(max_length=256)
    umpire_min = models.FloatField(default=0)
    umpire_max = models.FloatField(default=0)
    umpire_range = models.IntegerField(null=True,blank=True)
    umpire_check_type = models.CharField(max_length=64,choices=UMPIRE_CHECK_TYPES,default="static")
    umpire_range_type = models.CharField(max_length=64,choices=UMPIRE_RANGE_TYPES,default="current")
    umpire_percent_error = models.FloatField(default=.25)

    @property
    def last_std(self):
        return self._get_state().get("last_std",None)

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

    def set_state(self,status,last_value,extra={}):
        #Calculate new mean (to calc std)
        if self.history_value:
            new_mean = self.history_value*.9 + last_value*.1
        else:
            new_mean = last_value

        #Calculate new std. dont update if above 2 stds
        if last_value == None or new_mean == None:
            new_std = 0
        elif self.last_std == None:
            new_std = abs(last_value-new_mean)
        elif abs(last_value-new_mean)>2*self.last_std:
            new_std = abs(self.last_std)
        else:
            new_std = (((self.last_std**2)*9 + (last_value-new_mean)**2)/10)**.5

        super(UmpireServiceCheck,self).set_state(status,last_value,{'last_std':new_std})

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

    def history_series(self,num_values=40):
        cur_time = croniter.croniter(self.frequency or self.service.frequency,time.time())
        cur_time.get_next() #get next so the first get_prev is the current value

        key_series = ["%s:::%s" % (self._redis_key,self._standardize_minutes(cur_time.get_prev())) for i in range(num_values)]

        value_series = [json.loads(cache.get(key)).get("last_value") if cache.has_key(key) else 0 for key in key_series]
        value_series.reverse()
        return value_series

    def last_series(self,num_values=40):
        cur_time = croniter.croniter(self.frequency or self.service.frequency,time.time())
        cur_time.get_next() #get next so the first get_prev is the current value

        key_series = ["%s:::%s:::%s" % (self._redis_key,self._standardize_minutes(cur_time.get_prev()),"last") for i in range(num_values)]

        value_series = [json.loads(cache.get(key)).get("last_value") if cache.has_key(key) else 0 for key in key_series]
        value_series.reverse()
        return value_series

    def error_range_series(self,num_values=40):
        if self.umpire_check_type == "dynamic":
            return [[val*(1-self.umpire_percent_error),val*(1+self.umpire_percent_error)] for val in self.history_series()]
        else:
            return [[self.umpire_min,self.umpire_max] for i in range(num_values)]

    @property
    def _history_redis_key(self):
        cur_time = croniter.croniter(self.frequency or self.service.frequency,time.time()).get_next()
        return "%s:::%s" % (self._redis_key,self._standardize_minutes(cur_time))

    def _standardize_minutes(self,cur_time):
        return (int(cur_time) % (60*60*24)) / 60

    @property
    def error_lower_bound(self):
        if self.umpire_check_type == "static":
            return self.umpire_min
        else:
            return self.history_value*(1-self.umpire_percent_error)

    @property
    def error_upper_bound(self):
        if self.umpire_check_type == "static":
            return self.umpire_max
        else:
            return self.history_value*(1+self.umpire_percent_error)

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
        if self.error_upper_bound-self.error_lower_bound == 0:
            return 0
        return max(
            min(
                (self.last_value-self.error_lower_bound) / (self.error_upper_bound-self.error_lower_bound),
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
        return self.error_lower_bound,self.error_upper_bound

    def update_status(self):
        value = None
        status = STATUS_UNKNOWN

        if self.umpire_check_type=="static":
            umpire_min,umpire_max = self._update_status_static()
        else:
            umpire_min,umpire_max = self._update_status_dynamic()

        if self.umpire_range_type=="day":
            umpire_range = max(300,time.time() % (60*60*24))
        else:
            umpire_range = self.umpire_range or self.service.umpire_range

        get_parameters = {
            'metric':self.umpire_metric,
            'min':umpire_min,
            'max':umpire_max,
            'range':umpire_range
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
    resource_name = "compareservicecheck"
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
        except Exception as e:
            status = STATUS_UNKNOWN
            value = str(e)

        self.set_state(status=status,last_value=value)

class SensuServiceCheck(ServiceCheck):
    resource_name="sensuservicecheck"
    sensu_check_name = models.CharField(max_length=256)

    def get_result_data(self):
        if not self.last_updated:
            logging.info("Requested result data when no data available")
            return []

        endpoint = "%s/aggregates/%s/%s?results=true" % (settings.SENSU_API_ENDPOINT,
                                                         self.sensu_check_name,
                                                         self.last_updated)
        res = requests.get(endpoint)
        if not res.status_code==200:
            logging.warning("Failed to get data from sensu server")
            return []

        return res.json().get('results',[])

    def update_status(self):
        value = None
        status = STATUS_UNKNOWN
        last_aggregate = None

        try:
            url = "%s/aggregates/%s" % (settings.SENSU_API_ENDPOINT,self.sensu_check_name)
            res = requests.get(url)
            if res.status_code == 200:
                aggregates = res.json()
                last_aggregate = aggregates[0]
                url2 = "%s/aggregates/%s/%s" % (settings.SENSU_API_ENDPOINT,
                                                self.sensu_check_name,
                                                last_aggregate)
                res2 = requests.get(url2)
                if res2.status_code==200:
                    aggregate_data = res2.json()
                    if aggregate_data.get("critical",0):
                        status = STATUS_BAD
                    elif aggregate_data.get("warning",0) or aggregate_data.get("unknown",0):
                        status = STATUS_UNKNOWN
                    else:
                        status = STATUS_GOOD

                    value = "%s/%s/%s" % (aggregate_data.get("ok",0),
                                          aggregate_data.get("critical",0),
                                          aggregate_data.get("warning",0) + aggregate_data.get("unknown",0)
                                          )

        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            logging.error("Failed to connect with sensu api server")

        extra = {}
        if last_aggregate:
            extra.update({"last_updated":last_aggregate})

        self.set_state(status=status,last_value=value,extra=extra)

RESOURCES = [
    Service,
    ServiceCheck,
    SimpleServiceCheck,
    UmpireServiceCheck,
    CompareServiceCheck,
    CodeServiceCheck,
    SensuServiceCheck
]

RESOURCE_NAME_MAP = dict([(cls.resource_name,cls) for cls in RESOURCES])
