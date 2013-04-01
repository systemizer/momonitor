from service import Service
from simple_service_check import SimpleServiceCheck
from compare_service_check import CompareServiceCheck
from sensu_service_check import SensuServiceCheck
from code_service_check import CodeServiceCheck
from umpire_service_check import UmpireServiceCheck
from graphite_service_check import GraphiteServiceCheck
from django.conf import settings

AVAILABLE_CHECK_MODELS = [SimpleServiceCheck,
                          CompareServiceCheck,
                          SensuServiceCheck,
                          CodeServiceCheck,
                          UmpireServiceCheck,
                          GraphiteServiceCheck]

def _model_from_string(model_str):
    potential_models = filter(lambda model: model.__name__==model_str,
                              AVAILABLE_CHECK_MODELS)
    if len(potential_models)!=1:
        raise Exception("Error: Bad Model String: %s" % model_str)

    return potential_models[0]

if hasattr(settings,"CHECK_MODELS") and settings.CHECK_MODELS:
    CHECK_MODELS = [_model_from_string(model_str) for model_str in settings.CHECK_MODELS]
    
else:
    CHECK_MODELS = [SimpleServiceCheck,
                    UmpireServiceCheck,
                    CompareServiceCheck,
                    SensuServiceCheck,
                    GraphiteServiceCheck,
                    CodeServiceCheck]
    
RESOURCES = CHECK_MODELS+[Service]

RESOURCE_NAME_MAP = dict([(cls.resource_name,cls) for cls in RESOURCES])
