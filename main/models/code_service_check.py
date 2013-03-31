import logging
from django.db import models
from momonitor.main.models.service_check import ServiceCheck
from momonitor.main.constants import (STATUS_UNKNOWN,
                                      STATUS_GOOD,
                                      STATUS_WARNING,
                                      STATUS_BAD)

class CodeServiceCheck(ServiceCheck):
    '''
    Code Service checks take in an arbitrary python script
    that contains a "run" function, which returns a tuple with
    (msg_status,code_status)
    '''
    resource_table_template = "main/tables/codeservicecheck.html"
    class Meta:
        app_label="main"

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
