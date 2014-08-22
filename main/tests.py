from django.utils import unittest
import mock

from momonitor.main.constants import STATUS_BAD
from momonitor.main.models import Service, SimpleServiceCheck


class ServiceCheckAlertTest(unittest.TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name='test service',
            alert_type='pagerduty')
        self.service_check = SimpleServiceCheck.objects.create(
            endpoint="http://twitter.com",
            service=self.service)

        self.service._send_alert_pagerduty = mock.Mock()
        self.service._send_alert_email = mock.Mock()

    def test_service_check_alert(self):
        self.service_check.set_state(STATUS_BAD, None)

        self.service._send_alert_pagerduty.assert_called_with('')
        assert not self.service._send_alert_email.called

    def test_service_check_alert_override(self):
        self.service_check.alert_type = 'email'
        self.service_check.save()

        self.service_check.set_state(STATUS_BAD, None)

        assert not self.service._send_alert_pagerduty.called
        self.service._send_alert_email.assert_called_with('')
