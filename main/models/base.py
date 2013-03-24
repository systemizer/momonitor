from django.db import models
from momonitor.main.decorators import ClassProperty
import json
from django.core.cache import cache
import time

class BaseModel(models.Model):
    @ClassProperty
    @classmethod
    def resource_name(cls):
        return cls.__name__.lower()

    class Meta:
        abstract = True
