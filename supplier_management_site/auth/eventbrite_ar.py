from django.views.i18n import get_formats
from social_core.backends.eventbrite import EventbriteOAuth2
from django.conf import settings
from django.views import i18n
from django.utils.translation import to_locale, get_language

class EventbriteAuth2(EventbriteOAuth2):
    AUTHORIZATION_URL = 'https://www.eventbrite.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://www.eventbrite.com/oauth/token'
    METADATA_URL = 'https://www.eventbriteapi.com/v3/users/me'

    def __init__(self, strategy, redirect_uri=None):
        super().__init__(strategy, redirect_uri)
        if to_locale(get_language()) == 'es' or strategy.session._session['_language'] == 'es':
            self.AUTHORIZATION_URL = 'https://www.eventbrite.com.ar/oauth/authorize'
            self.ACCESS_TOKEN_URL = 'https://www.eventbrite.com.ar/oauth/token'
            self.METADATA_URL = 'https://www.eventbriteapi.com.ar/v3/users/me'

