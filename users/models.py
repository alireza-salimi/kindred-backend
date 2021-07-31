from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('User should have a phone number')
        if not password:
            raise ValueError('User should have a password')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    first_name = models.CharField(max_length=200, verbose_name=_('First name'), blank=True, null=True)
    last_name = models.CharField(max_length=200, verbose_name=_('Last name'), blank=True, null=True)
    date_of_birth = models.DateField(verbose_name=_('Date of birth'), null=True, blank=True)
    phone_number = PhoneNumberField(unique=True, verbose_name=_('Phone number'))
    image = models.ImageField(upload_to='images/', verbose_name=_('Image'), blank=True, null=True)
    default_kindred = models.ForeignKey(
        'kindred.Kindred', on_delete=models.SET_NULL, related_name='default_for_users',
        blank=True, null=True, verbose_name=_('Default kindred')
    )
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    username = None
    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)
