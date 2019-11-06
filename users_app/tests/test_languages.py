from http import HTTPStatus
from parameterized import parameterized

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
    RequestFactory,
)
from django.utils.translation import (
    activate,
    get_language,
    ugettext_lazy as _
)

from supplier_management_site.tests.views import home

from users_app.factory_boy import (
    UserFactory
)

LANGUAGES = [
    ('en',),
    ('es',),
    ('pt-br',),
]

class TestTranslationConfiguration(TestCase):
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


class TestLanguageSelection(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(
            email='sup@gmail.com',
        )
        self.user.groups.add(Group.objects.get(name='supplier'))
        self.home = 'supplier-home'
        self.taxpayer_create = 'taxpayer-create'

    def tearDown(self):
        activate('en')

    def _set_language(self, language):
        data = {
            'language': language,
            'next': self.home,
        }
        return self.client.post(
            reverse(
                'set_user_language',
            ),
            data,
            follow=True
        )


    # Test default language
    def test_user_default_language(self):
        self.client.get(reverse(self.home))
        self.assertEqual(get_language(), 'en')

    # Test cambia idioma en login y se guarda en session
    @parameterized.expand(LANGUAGES)
    def test_user_selecting_preferred_languages_in_login(
        self,
        language
    ):
        self.client.get(reverse('login'))
        self._set_language(language)
        self.assertEqual(get_language(), language)

    @parameterized.expand(LANGUAGES)
    def test_user_selects_language_and_its_stored_in_session(
        self,
        language
    ):
        self.client.force_login(self.user)
        self.client.get(reverse(self.home))
        self._set_language(language)
        session_language = get_language()
        self.assertEqual(session_language, language)

    @parameterized.expand(LANGUAGES)
    def test_users_language_selection_persist_in_current_session(
        self,
        language
    ):
        self.client.force_login(self.user)
        self.client.get(reverse(self.home))
        self._set_language(language)
        selected_lang = get_language()
        self.client.get(reverse(self.taxpayer_create))
        persisted_lang = get_language()
        self.assertEqual(selected_lang, language)
        self.assertEqual(persisted_lang, language)

    @parameterized.expand(LANGUAGES)
    def test_user_select_language_redirects_to_same_url(
        self,
        language
    ):
        self.client.force_login(self.user)
        self.client.get(reverse(self.home))
        response = self._set_language(language)
        self.assertEqual(
            response.redirect_chain[0],
            (self.home, HTTPStatus.FOUND)
        )
