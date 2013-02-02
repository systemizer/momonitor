from momonitor.main.constants import STATUS_GOOD,STATUS_BAD,STATUS_UNKNOWN

def statuses(request):
    return {'STATUS_GOOD':STATUS_GOOD,
            'STATUS_BAD':STATUS_BAD,
            'STATUS_UNKNOWN':STATUS_UNKNOWN
            }

    
