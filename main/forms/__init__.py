from simple_service_check import SimpleServiceCheckForm
from compare_service_check import CompareServiceCheckForm
from sensu_service_check import SensuServiceCheckForm
from code_service_check import CodeServiceCheckForm
from graphite_service_check import GraphiteServiceCheckForm
from umpire_service_check import UmpireServiceCheckForm
from service import ServiceForm
from service_check import ServiceCheckForm

RESOURCE_FORM_MAP = {
    ServiceForm._meta.model:ServiceForm,
    UmpireServiceCheckForm._meta.model:UmpireServiceCheckForm,
    SimpleServiceCheckForm._meta.model:SimpleServiceCheckForm,
    CompareServiceCheckForm._meta.model:CompareServiceCheckForm,
    CodeServiceCheckForm._meta.model:CodeServiceCheckForm,
    SensuServiceCheckForm._meta.model:SensuServiceCheckForm,
    GraphiteServiceCheckForm._meta.model:GraphiteServiceCheckForm,
}

