from service import Service
from simple_service_check import SimpleServiceCheck
from compare_service_check import CompareServiceCheck
from sensu_service_check import SensuServiceCheck
from code_service_check import CodeServiceCheck
from umpire_service_check import UmpireServiceCheck


RESOURCES = [SimpleServiceCheck,
             CompareServiceCheck,
             SensuServiceCheck,
             CodeServiceCheck,
             UmpireServiceCheck,
             Service]

RESOURCE_NAME_MAP = dict([(cls.resource_name,cls) for cls in RESOURCES])
