from datetime import timedelta
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from users.models import User
from django.utils.translation import ugettext_lazy as _
from kindred_backend.settings import cache_db
import random
from kindred.models import *


class UserSignUpSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    
    def save(self, **kwargs):
        phone_number = str(self.validated_data.pop('phone_number'))
        otp = random.randint(10000, 99999)
        cache_db.hmset(phone_number, {'otp': otp, 'invited': 0})
        cache_db.expire(phone_number, timedelta(minutes=30))
        return otp


class UserConfirmSignupSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    otp = serializers.IntegerField()

    def validate(self, attrs):
        user_data = cache_db.hgetall(str(attrs['phone_number']))
        if not user_data or int(user_data['otp']) != attrs['otp'] or int(user_data['invited']):
            raise serializers.ValidationError(_('OTP may be invalid or expired.'))
        return attrs
    
    def save(self, **kwargs):
        cache_db.delete(str(self.validated_data['phone_number']))
        try:
            user = User.objects.get(
                phone_number=self.validated_data['phone_number']
            )
        except User.DoesNotExist:
            user = User.objects.create(
                phone_number=self.validated_data['phone_number']
            )
        return user

class RetrieveUserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'date_of_birth', 'image']
    
    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        else:
            return None


class UserCompleteProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_of_birth = serializers.DateField()
    image = serializers.ImageField()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'date_of_birth', 'image']
