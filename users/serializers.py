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
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_of_birth = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'])

    def validate(self, attrs):
        user_exists = User.objects.filter(phone_number=attrs['phone_number']).exists()
        if user_exists:
            raise serializers.ValidationError(_('There is already a user with this phone number.'))
        return attrs
    
    def save(self, **kwargs):
        phone_number = str(self.validated_data.pop('phone_number'))
        self.validated_data['date_of_birth'] = str(self.validated_data['date_of_birth'])
        otp = random.randint(10000, 99999)
        cache_db.hmset(phone_number, {**self.validated_data, 'otp': otp})
        return otp


class UserConfirmSignupSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    otp = serializers.IntegerField()

    def validate(self, attrs):
        user_data = cache_db.hgetall(str(attrs['phone_number']))
        print(user_data)
        if not user_data or int(user_data['otp']) != attrs['otp']:
            raise serializers.ValidationError(_('OTP may be invalid or expired.'))
        return attrs
    
    def save(self, **kwargs):
        user_data = cache_db.hgetall(str(self.validated_data['phone_number']))
        cache_db.delete(str(self.validated_data['phone_number']))
        user = User.objects.create(
            phone_number=self.validated_data['phone_number'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            date_of_birth=user_data['date_of_birth']
        )
        kindred = Kindred.objects.create(
            name=user_data['first_name'] + ' ' + user_data['last_name'] + "'s kindred"
        )
        kindred_member = KindredMember.objects.create(
            user=user,
            name=user_data['first_name'] + ' ' + user_data['last_name'],
            kindred=kindred,
            is_admin=True
        )
        return kindred_member


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
