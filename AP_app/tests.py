from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from users_app.models import User


class TestAP(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='ap@eventbrite.com')
        self.client = Client()
        return super().setUp()

    def test_ap_site_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('ap-home'),
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
