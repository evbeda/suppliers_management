from django.test import SimpleTestCase, RequestFactory
from django.utils.translation import activate, ugettext_lazy as _
from parameterized import parameterized
from .views import home


class HomePageTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_plain_translation(self):
        activate('es')
        self.assertEqual(_('Hello world'), 'Hola Mundo')

    @parameterized.expand([
        ('en', 'Hello world'),
        ('es', 'Hola Mundo'),
        ('pt-BR', 'Olá, mundo!'),
    ])
    def test_testing_page_contains_correct_translation(self, lang, text):
        activate(lang)
        request = self.factory.get("/{}/".format(lang))
        response = home(request)
        self.assertContains(response, text)
