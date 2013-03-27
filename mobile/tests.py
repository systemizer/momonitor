from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import unittest
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from momonitor.main.models import (Service,
                                   SimpleServiceCheck,
                                   UmpireServiceCheck,
                                   CompareServiceCheck,
                                   CodeServiceCheck,
                                   SensuServiceCheck)

class EndpointsTest(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username="testuser",password="test")
        self.user.save()
        self.client = Client()
        self.assertTrue(self.client.login(username="testuser",password="test"))

    def tearDown(self):
        self.user.delete()

    def test_index(self):        
        response = self.client.get(reverse("mobile:index"))
        self.assertEqual(response.status_code,200)

    def test_service(self):        
        response = self.client.get(reverse("mobile:service",kwargs={'service_id':self.service.id}))
        self.assertEqual(response.status_code,200)

    def test_check(self):
        for check in self.checks:
            response = self.client.get(reverse("mobile:check",
                                               kwargs={'check_name':check.__class__.resource_name,
                                                       'check_id':check.id}))
            self.assertEqual(response.status_code,200)
