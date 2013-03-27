from django.conf import settings

def service_endpoints(request):
    return {
        'GRAPHITE_ENDPOINT' : settings.GRAPHITE_ENDPOINT if hasattr(settings,"GRAPHITE_ENDPOINT") and settings.GRAPHITE_ENDPOINT else None,
        'SENSU_API_ENDPOINT' : settings.SENSU_API_ENDPOINT if hasattr(settings,"SENSU_API_ENDPOINT") and settings.SENSU_API_ENDPOINT else None,
        'UMPIRE_ENDPOINT' : settings.UMPIRE_ENDPOINT if hasattr(settings,"UMPIRE_ENDPOINT") and settings.UMPIRE_ENDPOINT else None
        }
