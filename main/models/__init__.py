from service import Service
from simple_service_check import SimpleServiceCheck
from compare_service_check import CompareServiceCheck
from sensu_service_check import SensuServiceCheck
from code_service_check import CodeServiceCheck
from umpire_service_check import UmpireServiceCheck
from graphite_service_check import GraphiteServiceCheck

from django.conf import settings

if hasattr(settings,"CHECK_MODELS"):
    CHECK_MODELS = settings.CHECK_MODELS
else:
    CHECK_MODELS = [SimpleServiceCheck,
                    UmpireServiceCheck,
                    CompareServiceCheck,
                    SensuServiceCheck,
                    GraphiteServiceCheck,
                    CodeServiceCheck]
    
RESOURCES = CHECK_MODELS+[Service]

RESOURCE_NAME_MAP = dict([(cls.resource_name,cls) for cls in RESOURCES])
