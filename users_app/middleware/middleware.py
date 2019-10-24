import django
from django.utils import translation


def is_django_greater_than_1_10():
    main_version, sub_version, _, _, _ = django.VERSION
    return (
        main_version > 1 or (
            main_version == 1 and
            sub_version >= 10
        )
    )

if is_django_greater_than_1_10():
    from django.utils.deprecation import MiddlewareMixin
    superclass = MiddlewareMixin
else:
    superclass = object



class UserLanguageMiddleware(superclass):
    def process_response(self, request, response):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return response

        user_language = user.preferred_language

        if not user_language:
            return response

        translation.activate(user_language)
        request.session[translation.LANGUAGE_SESSION_KEY] = user_language

        return response
