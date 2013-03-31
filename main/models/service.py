import logging
from django.db import models
import itertools
from momonitor.main.models.base import BaseModel
from momonitor.main.constants import (STATUS_UNKNOWN,
                                      STATUS_GOOD,
                                      STATUS_WARNING,
                                      ALERT_CHOICES,
                                      STATUS_BAD)
import requests

class Service(BaseModel):
    class Meta:
        app_label="main"

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
        '''Returns the last_updated of the oldest (or unknown) check'''
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
            email_msg = get_template("alert_email.txt").render(
                Context({"description":description,
                         "service_name":self.name,
                         "url":"%s%s" % (settings.DOMAIN,
                                         reverse("main:service",kwargs={'service_id':self.id}))
                         if settings.hasattr("DOMAIN") and settings.DOMAIN  else ""
                             
                         })
                )
                    
            send_mail("MOMONITOR EVENT TRIGGERED",
                      email_msg,
                      settings.SERVER_EMAIL,
                      [self.email_contact,],
                      fail_silently=False)
        except SMTPException:
            logging.error("Failed to send email to %s for error %s" % (self.email_contact,description))

    def send_alert(self,description,alert_type=None):
        if self.silenced:
            logging.info("Service %s is silenced. Not sending pagerduty alert %s" % (self.name,description))
            return

        alert_type = alert_type or self.alert_type
        if alert_type == "pagerduty":
            self._send_alert_pagerduty(description)
        elif alert_type == "email":
            self._send_alert_email(description)
        else:
            logging.info("No alert being sent because alert type is 'none'")

    def all_checks(self,check_type=""):
        from momonitor.main.models import CHECK_MODELS
        resource_names = [m.resource_name for m in CHECK_MODELS]

        if check_type:
            if check_type not in resource_names:
                logging.warning("Could not find check type: %s" % check_type)
                return []
            return list(getattr(self,check_type).all())
        return list(itertools.chain(*[list(getattr(self,name).all()) for name in resource_names]))

    def update_status(self):
        for check in self.all_checks():
            check.update_status()
