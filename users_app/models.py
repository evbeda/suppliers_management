from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    preferred_language = models.CharField(
        max_length=40,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE
    )

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def get_name(self):
        if self.username is None:
            return self.email.split('@')[0]
        return self.username

    @property
    def is_ap_account(self):
        return self.has_perm('users_app.ap_role')

    @property
    def is_AP(self):
        return self.groups.filter(name='ap_admin').exists()

    @property
    def is_ap_reporter(self):
        return self.groups.filter(name='ap_reporter').exists()

    @property
    def is_ap_manager(self):
        return self.groups.filter(name='ap_manager').exists()

    @property
    def is_supplier(self):
        return self.groups.filter(name='supplier').exists()

    class Meta:
        index_together = ["email"]
