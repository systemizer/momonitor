from django import template
from django.core.urlresolvers import reverse
from django.conf import settings
from momonitor.main.models import CHECK_MODELS
import time
import logging
register = template.Library()

from momonitor.main.constants import (STATUS_GOOD,
                                      STATUS_BAD,
                                      STATUS_WARNING,
                                      STATUS_UNKNOWN)

def percentage(value):
    value*=100
    return ("%s" % int(value)) + "%"

def multiply(value,factor):
    return value*factor

def negate(value):
    return -value

def resource_url(instance):
    resource_name = instance.__class__.resource_name
    return "/api/v1/%s/%s/" % (resource_name,instance.id)
    
def since(value):
    if not type(value)==float:
        try:
            value = float(value)
        except:
            logging.debug("Cannot parse value %s with templatetag since" % value)
            return "unknown"
    seconds_since = int(time.time()-value)
    if seconds_since > 60*60*24:
        return "%s day(s) ago" % (seconds_since/(60*60*24))
    elif seconds_since > 60*60:
        return "%s hour(s) ago" % (seconds_since/(60*60))
    elif seconds_since > 60:
        return "%s minute(s) ago" % (seconds_since/60)
    elif seconds_since > 1:
        return "%s second(s) ago" % seconds_since
    else:
        return "just now"

def to_bootstrap_rowclass(value):    
    if value==STATUS_GOOD:
        return "success"
    elif value==STATUS_BAD:
        return "error"
    elif value==STATUS_WARNING:
        return "warning"
    else:
        return "warning"

def to_status_png(value):
    if value==STATUS_GOOD:
        return "%simg/green-dot.png" % settings.STATIC_URL
    elif value==STATUS_BAD:
        return "%simg/red-dot.png" % settings.STATIC_URL
    elif value==STATUS_WARNING:
        return "%simg/yellow-dot.png" % settings.STATIC_URL
    else:
        return "%simg/yellow-dot.png" % settings.STATIC_URL

def to_bootstrap_progressbarclass(value):    
    if value==STATUS_GOOD:
        return "bar-success"
    elif value==STATUS_BAD:
        return "bar-danger"
    elif value==STATUS_WARNING:
        return "bar-warning"
    else:
        return "bar-warning"

def status_count(service,check_type):
    return service.status_counts(check_type)

def sort_checks(check_items):
    return sorted(check_items, 
                  key= lambda x: CHECK_MODELS.index(x[0]))
    

register.filter('since', since)
register.filter('percentage', percentage)
register.filter('multiply', multiply)
register.filter('negate', negate)
register.filter('to_bootstrap_rowclass', to_bootstrap_rowclass)
register.filter('to_bootstrap_progressbarclass', to_bootstrap_progressbarclass)
register.filter('to_status_png', to_status_png)
register.filter('resource_url', resource_url)
register.filter('status_count', status_count)
register.filter('sort_checks', sort_checks)
