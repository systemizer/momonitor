from django import template
import time
import logging
register = template.Library()

from momonitor.main.constants import (STATUS_GOOD,
                                      STATUS_BAD,
                                      STATUS_UNKNOWN)

def since(value):
    if not type(value)==float:
        try:
            value = float(value)
        except:
            logging.error("Cannot parse value %s with templatetag since" % value)
            return ""
    seconds_since = int(time.time()-value)
    if seconds_since > 60*60*24:
        return "%s days ago" % (seconds_since/(60*60*24))
    elif seconds_since > 60*60:
        return "%s hours ago" % (seconds_since/(60*60))
    elif seconds_since > 60:
        return "%s minutes ago" % (seconds_since/60)
    elif seconds_since > 1:
        return "%s seconds ago" % seconds_since
    else:
        return "just now"

def to_bootstrap_rowclass(value):    
    if value==STATUS_GOOD:
        return "success"
    elif value==STATUS_BAD:
        return "error"
    else:
        return "warning"

register.filter('since', since)
register.filter('to_bootstrap_rowclass', to_bootstrap_rowclass)
