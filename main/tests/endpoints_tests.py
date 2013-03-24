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
        self.service.delete()
        for check in self.checks:
            check.delete()
        self.user.delete()

    def test_index(self):        
        response = self.client.get(reverse("main:index"))
        self.assertEqual(response.status_code,200)

    def test_how_it_works(self):        
        response = self.client.get(reverse("main:how_it_works"))
        self.assertEqual(response.status_code,200)

    def test_service(self):        
        response = self.client.get(reverse("main:service",kwargs={'service_id':self.service.id}))
        self.assertEqual(response.status_code,200)

    def test_service_refresh(self):
        response = self.client.get(reverse("main:refresh",kwargs={'resource_name':Service.resource_name,'resource_id':self.service.id}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest'
                                   )
        
        self.assertEqual(response.status_code,200)

    def test_check_refresh(self):
        for check in self.checks:
            response = self.client.get(reverse("main:refresh",kwargs={'resource_name':check.__class__.resource_name,'resource_id':check.id}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code,200)

    def test_service_modal_create(self):
        response = self.client.get(reverse("main:modal_form",kwargs={'resource_name':Service.resource_name}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,200)

    def test_service_modal_edit(self):
        response = self.client.get(reverse("main:modal_form",kwargs={'resource_name':Service.resource_name,'resource_id':self.service.id}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,200)

    def test_service_check_modal_create(self):
        for check in self.checks:
            response = self.client.get(reverse("main:modal_form",kwargs={'resource_name':check.__class__.resource_name}),
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code,200)

    def test_service_check_modal_edit(self):
        for check in self.checks:
            response = self.client.get(reverse("main:modal_form",kwargs={'resource_name':check.__class__.resource_name,'resource_id':check.id}),
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code,200)

    def test_tastypie_get(self):
        for check in self.checks:
            response = self.client.get("%s?format=json" % reverse("main:api_dispatch_detail",kwargs={
                        'resource_name':check.__class__.resource_name,
                        'api_name':'v1',
                        'pk':check.id
                        }),
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')

            self.assertEquals(response.status_code,200)


