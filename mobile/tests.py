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
        self.user = User.objects.create_user(username="testuser",password="test")
        self.user.save()
        self.client = Client()
        self.assertTrue(self.client.login(username="testuser",password="test"))

        self.service = Service(name="test service")
        self.service.save()
        self.checks = []
        
        simple_check = SimpleServiceCheck(endpoint="http://google.com",service=self.service)
        simple_check.save()
        compare_check = CompareServiceCheck(endpoint="http://google.com",
                                            field="",
                                            compared_value="test_value",
                                            service=self.service)
        compare_check.save()

        sensu_check = SensuServiceCheck(sensu_check_name="test_check",
                                        service=self.service)
        sensu_check.save()

        umpire_check = UmpireServiceCheck(umpire_metric="good_metric",
                                          service=self.service)
        umpire_check.save()

        self.checks.append(simple_check)
        self.checks.append(compare_check)
        self.checks.append(sensu_check)
        self.checks.append(umpire_check)


    def tearDown(self):
        self.user.delete()
        self.service.delete()
        for check in self.checks:
            check.delete()
            

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
