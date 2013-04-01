from compare_service_check import CompareServiceCheckForm
from code_service_check import CodeServiceCheckForm
from service import ServiceForm
from service_check import ServiceCheckForm
from utils import generate_check_modelform_cls

from momonitor.main.models import (SimpleServiceCheck,
                                   UmpireServiceCheck,
                                   GraphiteServiceCheck,
                                   SensuServiceCheck)

SimpleServiceCheckForm = generate_check_modelform_cls(SimpleServiceCheck,
                                                  template_path="main/modal_forms/simpleservicecheck.html")
UmpireServiceCheckForm = generate_check_modelform_cls(UmpireServiceCheck,
                                                  template_path="main/modal_forms/umpireservicecheck.html")
GraphiteServiceCheckForm = generate_check_modelform_cls(GraphiteServiceCheck,
                                                  template_path="main/modal_forms/graphiteservicecheck.html")
SensuServiceCheckForm = generate_check_modelform_cls(SensuServiceCheck,
                                                  template_path="main/modal_forms/sensuservicecheck.html")

RESOURCE_FORM_MAP = {
    ServiceForm._meta.model:ServiceForm,
    CompareServiceCheckForm._meta.model:CompareServiceCheckForm,
    CodeServiceCheckForm._meta.model:CodeServiceCheckForm,
    SimpleServiceCheckForm._meta.model:SimpleServiceCheckForm,
    UmpireServiceCheckForm._meta.model:UmpireServiceCheckForm,
    GraphiteServiceCheckForm._meta.model:GraphiteServiceCheckForm,
    SensuServiceCheckForm._meta.model:SensuServiceCheckForm,
}

