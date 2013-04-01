import logging
from django.db import models
from momonitor.main.models.service_check import ServiceCheck
from momonitor.main.constants import (STATUS_UNKNOWN,
                                      STATUS_GOOD,
                                      STATUS_WARNING,
                                      STATUS_BAD)
import requests
from django.conf import settings


class GraphiteServiceCheck(ServiceCheck):
    '''
    Graphite Checks mimic Umpire's Functionality
    '''
    resource_table_template = "main/tables/graphiteservicecheck.html"
    class Meta:
        app_label="main"

    graphite_range = models.IntegerField(default=300)
    graphite_metric = models.CharField(max_length=256)
    graphite_lower_bound = models.FloatField()
    graphite_upper_bound = models.FloatField()

    @property
    def graphite_url(self):
        return "%s/render/?min=0&width=570&height=350&from=-3h&target=%s" % (settings.GRAPHITE_ENDPOINT,self.graphite_metric)

    def update_status(self):
        value = None
        status = STATUS_UNKNOWN

        
        try:
            res = requests.get("%s/render/?target=%s&from=-%ss&rawData=true" % (
                    settings.GRAPHITE_ENDPOINT,
                    self.graphite_metric,
                    self.graphite_range))

            if res.status_code!=200:
                self.set_state(status=STATUS_UNKNOWN,last_value="Graphite returned a non-200 code")
                return

        except requests.exceptions.ConnectionError:
            self.set_statue(status=STATUS_UNKNOWN,last_value="Failed to connect to graphite")
            return

        except requests.exceptions.Timeout:
            self.set_state(status=STATUS_UNKNOWN,last_value="Graphite Timed Out")
            return
        except Exception:
            self.set_state(status=STATUS_UNKNOWN,last_value="Something went wrong")
            return

        data = res.text.split("|")
        data_values = data[1].split(",")
        average_value = sum([float(d) for d in data_values])/len(data_values)

        if self.graphite_lower_bound <= average_value and \
                self.graphite_upper_bound >= average_value:
            status = STATUS_GOOD
        else:
            status = STATUS_BAD


        self.set_state(status=status,last_value=average_value)
