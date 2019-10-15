import factory

from django.contrib.auth.models import Group

from users_app.models import (
    User
)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Sequence(lambda n: 'person{}@gmail.com'.format(n))
