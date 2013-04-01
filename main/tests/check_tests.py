from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import unittest
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.conf import settings

from momonitor.main.constants import (STATUS_GOOD,
                                      STATUS_BAD,
                                      STATUS_UNKNOWN)

from momonitor.main.models import (Service,
                                   SimpleServiceCheck,
                                   UmpireServiceCheck,
                                   CompareServiceCheck,
                                   GraphiteServiceCheck,
                                   CodeServiceCheck,
                                   SensuServiceCheck)

class CheckTest(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser",password="test")
        self.user.save()
        self.client = Client()
        self.assertTrue(self.client.login(username="testuser",password="test"))
        self.service = Service(name="test service")
        self.service.save()
        self.good_checks = []
        self.bad_checks = []
        self.unknown_checks = []

    def test_good_checks(self):
        for check in self.good_checks:
            check.update_status()
            self.assertEqual(check.status,STATUS_GOOD)

    def test_bad_checks(self):
        for check in self.bad_checks:
            check.update_status()
            self.assertEqual(check.status,STATUS_BAD)

    def test_unknown_checks(self):
        for check in self.unknown_checks:
            check.update_status()
            self.assertEqual(check.status,STATUS_UNKNOWN)

    def tearDown(self):
        self.service.delete()
        self.user.delete()
        for check in self.good_checks:
            check.delete()
        for check in self.bad_checks:
            check.delete()
        for check in self.unknown_checks:
            check.delete()

class SimpleServiceCheckTest(CheckTest):
    def setUp(self):

        super(SimpleServiceCheckTest,self).setUp()
        good_check = SimpleServiceCheck(
            endpoint="http://%s:%s/simple/good/" % (settings.FAKE_APP_HOST,settings.FAKE_APP_PORT),
            service=self.service)
        good_check.save()
        self.good_checks.append(good_check)

        bad_check = SimpleServiceCheck(
            endpoint="http://%s:%s/simple/bad/" % (settings.FAKE_APP_HOST,settings.FAKE_APP_PORT),
            service=self.service)
        bad_check.save()
        self.bad_checks.append(bad_check)

class UmpireServiceCheckTest(CheckTest):
    def setUp(self):
        super(UmpireServiceCheckTest,self).setUp()

        good_check = UmpireServiceCheck(umpire_metric="good_metric",
                                        umpire_min=0,
                                        umpire_max=1000,
                                        service=self.service)
        good_check.save()
        self.good_checks.append(good_check)

        bad_check = UmpireServiceCheck(umpire_metric="bad_metric",
                                            umpire_min=0,
                                            umpire_max=10,
                                            service=self.service)
        bad_check.save()
        self.bad_checks.append(bad_check)

class CompareServiceCheckTest(CheckTest):
    def setUp(self):
        super(CompareServiceCheckTest,self).setUp()

        good_check = CompareServiceCheck(
            endpoint="http://%s:%s/compare/" % (settings.FAKE_APP_HOST,settings.FAKE_APP_PORT),
            serialization="json",
            field="test_field_name",
            comparator="==",
            compared_value=1000,
            service=self.service)

        good_check.save()

        bad_check = CompareServiceCheck(
            endpoint="http://%s:%s/compare/" % (settings.FAKE_APP_HOST,settings.FAKE_APP_PORT),
            serialization="json",
            field="test_field_name",
            comparator="==",
            compared_value=10,
            service=self.service)

        bad_check.save()

        unknown_check = CompareServiceCheck(
            endpoint="http://%s:%s/compare/unknown/" % (settings.FAKE_APP_HOST,settings.FAKE_APP_PORT),
            serialization="json",
            field="test_field_name",
            comparator="==",
            compared_value="test",
            service=self.service)

        unknown_check.save()

        self.good_checks.append(good_check)
        self.bad_checks.append(bad_check)
        self.unknown_checks.append(unknown_check)
                                            

#TODO
class CodeServiceCheckTest(CheckTest):
    pass

class SensuServiceCheckTest(CheckTest):
    def setUp(self):
        super(SensuServiceCheckTest,self).setUp()
        good_check = SensuServiceCheck(sensu_check_name="good_check",
                                       service=self.service)
        good_check.save()
        self.good_checks.append(good_check)

        bad_check = SensuServiceCheck(sensu_check_name="bad_check",
                                      service=self.service)
        bad_check.save()
        self.bad_checks.append(bad_check)

        unknown_check = SensuServiceCheck(sensu_check_name="unknown_check",
                                      service=self.service)
        unknown_check.save()
        self.unknown_checks.append(unknown_check)

        
class GraphiteServiceCheckTest(CheckTest):
    def setUp(self):
        super(GraphiteServiceCheckTest,self).setUp()
        good_check = GraphiteServiceCheck(graphite_metric="good_metric",
                                          graphite_range=300,
                                          graphite_lower_bound=0,
                                          graphite_upper_bound=100,
                                          service=self.service)

        good_check.save()
        self.good_checks.append(good_check)

        bad_check = GraphiteServiceCheck(graphite_metric="bad_metric",
                                         graphite_range=300,
                                         graphite_lower_bound=0,
                                         graphite_upper_bound=100,
                                         service=self.service)

        bad_check.save()
        self.bad_checks.append(bad_check)

        unknown_check = GraphiteServiceCheck(graphite_metric="unknown_metric",
                                             graphite_range=300,
                                             graphite_lower_bound=0,
                                             graphite_upper_bound=100,
                                             service=self.service)

        unknown_check.save()
        self.unknown_checks.append(unknown_check)

        
