import logging
from django.db import models
from momonitor.main.models.service_check import ServiceCheck
from momonitor.main.constants import (STATUS_UNKNOWN,
                                      STATUS_GOOD,
                                      STATUS_WARNING,
                                      STATUS_BAD)
import requests


class SimpleServiceCheck(ServiceCheck):
    '''
    Simple Checks hit an HTTP endpoint and check
    whether or not the response's status code is 200
    '''
    resource_table_template = "main/tables/simpleservicecheck.html"
    class Meta:
        app_label="main"

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
