from momonitor.main.models.base import BaseModel
from momonitor.main.models.service import Service
from django.db import models
from momonitor.main.constants import (STATUS_UNKNOWN,
                                      STATUS_GOOD,
                                      STATUS_WARNING,
                                      ALERT_CHOICES,
                                      STATUS_BAD)
import json
from django.core.cache import cache
import time

class ServiceCheck(BaseModel):
    resource_table_template = "main/tables/servicecheck.html"

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

    def set_state(self,status,last_value,extra={}):
        num_failures = self.num_failures+1 if status==STATUS_BAD else 0
        last_updated = self.last_updated if status==STATUS_UNKNOWN else time.time()

        if num_failures>=(self.failures_before_alert or self.service.failures_before_alert):
            self.send_alert(self.alert_type or self.service.alert_type)

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

    def send_alert(self,alert_type=None):
        if not self.silenced:
            self.service.send_alert(self.description or self.name,alert_type)
        else:
            logging.info("Triggered alert on %s, but it is silenced" % self.name)

    def update_status(self):
        raise NotImplemented("need to implement update_stats")
