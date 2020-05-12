from django.views.i18n import get_formats
from social_core.backends.eventbrite import EventbriteOAuth2
from django.conf import settings
from django.views import i18n
from django.utils.translation import to_locale, get_language


class EventbriteAuth2(EventbriteOAuth2):

    def authorization_url(self):
        if to_locale(get_language()) == 'es':
            self.AUTHORIZATION_URL = 'https://www.eventbrite.com.ar/oauth/authorize'
        return self.AUTHORIZATION_URL

    def access_token_url(self):
        if to_locale(get_language()) == 'es':
            self.ACCESS_TOKEN_URL = 'https://www.eventbrite.com.ar/oauth/token'
        return self.ACCESS_TOKEN_URL

    def user_data(self, access_token, *args, **kwargs):
        if to_locale(get_language()) == 'es':
            self.METADATA_URL = 'https://www.eventbriteapi.com.ar/v3/users/me'
        return self.get_json(self.METADATA_URL, headers={
          'Authorization': 'Bearer ' + access_token
        })
