import logging
from django.db import models
from momonitor.main.models.service_check import ServiceCheck
from momonitor.main.constants import (STATUS_UNKNOWN,
                                      STATUS_GOOD,
                                      STATUS_WARNING,
                                      STATUS_BAD)
import requests
from django.conf import settings

class SensuServiceCheck(ServiceCheck):
    '''
    Sensu checks integrate with a sensu server.
    It looks at the latest aggregate for a single
    check idetified by sensu_check_name
    '''
    resource_table_template = "main/tables/sensuservicecheck.html"
    class Meta:
        app_label="main"

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
            logging.warning("Failed to connect with sensu api server")
        
        extra = {}
        if last_aggregate:
            extra.update({"last_updated":last_aggregate})
        
        self.set_state(status=status,last_value=value,extra=extra)
