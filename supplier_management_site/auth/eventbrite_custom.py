from social_core.backends.eventbrite import EventbriteOAuth2
from django.utils.translation import to_locale, get_language


class LanguageAwareEventbriteOAuth2(EventbriteOAuth2):

    def authorization_url(self):
        self.AUTHORIZATION_URL = self.change_language_url() + '/oauth/authorize'
        return self.AUTHORIZATION_URL

    def access_token_url(self):
        self.ACCESS_TOKEN_URL = self.change_language_url() + '/oauth/token'
        return self.ACCESS_TOKEN_URL

    def user_data(self, access_token, *args, **kwargs):
        self.METADATA_URL = self.change_language_api() + '/v3/users/me'
        return self.get_json(self.METADATA_URL, headers={
          'Authorization': 'Bearer ' + access_token
        })

    @staticmethod
    def change_language_url():
        if to_locale(get_language()) == 'es':
            return 'https://www.eventbrite.com.ar'
        else:
            return 'https://www.eventbrite.com'

    @staticmethod
    def change_language_api():
        if to_locale(get_language()) == 'es':
            return 'https://www.eventbriteapi.com.ar'
        else:
            return 'https://www.eventbriteapi.com'
