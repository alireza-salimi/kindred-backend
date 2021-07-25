from django.db import models
from users.models import User
from django.utils.translation import ugettext_lazy as _
from location_field.models.plain import PlainLocationField


class Kindred(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    image = models.ImageField(upload_to='kindred/images/', verbose_name=_('Image'), blank=True, null=True)

    def __str__(self):
        return self.name


class KindredMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='members', verbose_name=_('User'))
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    kindred = models.ForeignKey(Kindred, on_delete=models.CASCADE, related_name='members', verbose_name=_('Kindred'))
    is_admin = models.BooleanField(default=False, verbose_name=_('Is admin'))
    image = models.ImageField(upload_to='members/images/', verbose_name=_('Image'), blank=True, null=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    coordinate = PlainLocationField(based_fields=['city'], zoom=7, verbose_name=_('Coordinate'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    kindred_member = models.ForeignKey(
        'kindred.KindredMember', on_delete=models.CASCADE, related_name='locations', verbose_name=_('Kindred member')
    )