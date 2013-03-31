import logging
from django.db import models
from momonitor.main.models.service_check import ServiceCheck
from momonitor.main.constants import (STATUS_UNKNOWN,
                                      STATUS_GOOD,
                                      STATUS_WARNING,
                                      STATUS_BAD)
import requests

SERIALIZATION_CHOICES = (
    ("json","json"),
    ("plaintext","plaintext"),
)

COMPARATOR_CHOICES = (
    ("==","=="),
    ("!=","!="),
    (">",">"),
    (">=",">="),
    ("<","<"),
    ("<=","<="),
    ("contains","contains"),
)


class CompareServiceCheck(ServiceCheck):
    '''
    This check looks at a specific field in a 
    serialized response and applies an arithmatic 
    check to that value
    '''
    resource_table_template = "main/tables/compareservicecheck.html"
    class Meta:
        app_label="main"

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

    def _parse_json(self,res):
        try:
            res_data = res.json()
        except ValueError:
            logging.warning("Failed to parse json in check %s" % self.name)
            return None

        for subfield in self.field.split("."):
            if type(res_data) == list:
                try:
                    subfield = int(subfield)
                    res_data = res_data[subfield]
                except (ValueError,IndexError):
                    res_data = None
                    break                            
                            
            else:
                if not res_data.has_key(subfield):
                    #No key found
                    res_data = None
                    break

                res_data = res_data[subfield]
        return res_data

    def update_status(self):        
        value = None
        status = STATUS_UNKNOWN

        try:
            res = requests.get(self.endpoint)
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout) as e:
            logging.warningr("Unable to connect to the server")
            self.set_state(status=STATUS_BAD,last_value="Unable to connect")
            return 
        
        if res.status_code!=200:
            self.set_state(status=STATUS_UNKNOWN,last_value="Non-200 http response")
            return 

        if self.serialization=="json":
            res_data = self._parse_json(res)
        else:
            res_data = res.text

        if res_data == None:
            self.set_state(status=STATUS_UNKNOWN,last_value="Failed to parse value")
            return         
                    
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

        self.set_state(status=status,last_value=value)
