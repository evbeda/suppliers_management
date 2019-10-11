import factory

from users_app.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Sequence(lambda n: 'person{}@gmail.com'.format(n))
