from django.db import models
from momonitor.common.decorators import ClassProperty
import json
from django.core.cache import cache
import time

class BaseModel(models.Model):
    @ClassProperty
    @classmethod
    def resource_name(cls):
        return cls.__name__.lower()

    @ClassProperty
    @classmethod
    def resource_template(cls):
        return "%s.html" % cls.resource_name

    class Meta:
        abstract = True
