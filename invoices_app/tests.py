from django.test import TestCase
from parameterized import parameterized
from .models import Company


class TestModels(TestCase):
    def setUp(self):
        pass

    @parameterized.expand([
        ('Eventbrite', 'Bringing the world together through live experiences')
    ])
    def test_company(self, name, description):
        company = Company(name=name, description=description)
        self.assertEqual(company.name, name)
        self.assertEqual(company.description, description)
        self.assertEqual(str(company), "Company:{} Description:{}".format(name, description))
