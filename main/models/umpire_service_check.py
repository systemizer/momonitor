import logging
from django.db import models
import urllib
from django.core.cache import cache
import time
from django.conf import settings
import croniter
from momonitor.main.models.service_check import ServiceCheck
from momonitor.main.constants import (STATUS_UNKNOWN,
                                      STATUS_GOOD,
                                      STATUS_WARNING,
                                      STATUS_BAD)
import requests
import json

UMPIRE_CHECK_TYPES = (
    ("static","static"),
    ("dynamic","dynamic")
)

UMPIRE_RANGE_TYPES = (
    ("current","current"),
    ("day","day")
)


class UmpireServiceCheck(ServiceCheck):
    '''
    Umpire Service Checks hit and umpire endpoint to 
    determine whether an graphite metric is outside 
    the bounds of umpire_min and umpire_max
    '''
    resource_table_template = "main/tables/umpireservicecheck.html"
    class Meta:
        app_label="main"

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
        if not last_value or not new_mean:
            new_std = None
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
            'metric':self.umpire_metric.replace(" ",""),
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
                    logging.warning("Error fetching value from umpire: %s" % endpoint)
                    value = self.last_value
                    status = STATUS_UNKNOWN

        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            logging.error("Umpire is down?!?")
            status = STATUS_UNKNOWN
        except ValueError:
            logging.error("Failed to parse json in check %s" % self.name)
            status = STATUS_UNKNOWN

        try:
            value = round(float(value),2) #round to 2 decimal places for now
        except (ValueError,TypeError) as e:
            logging.warning("Failed at converting value %s to rounded float" % value)
            value = None

        self.set_state(status=status,last_value=value)
        if status==STATUS_GOOD:
            self._update_history()
