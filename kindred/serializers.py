import json
from phonenumber_field.serializerfields import PhoneNumberField
from users.serializers import RetrieveUserSerializer
from rest_framework import serializers
from .models import *
from .apps import socket
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
import random
from kindred_backend.settings import cache_db


class RetrieveKindredSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Kindred
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        else:
            return None


class RetrieveKindredMemberSerializer(serializers.ModelSerializer):
    user = RetrieveUserSerializer()
    kindred = RetrieveKindredSerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = KindredMember
        fields = '__all__'
    
    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        elif obj.user.image:
            return self.context['request'].build_absolute_uri(obj.user.image.url)
        else:
            return None


class RetrieveLocationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    kindred_member = RetrieveKindredMemberSerializer()

    class Meta:
        model = Location
        exclude = ('id',)
    
    def get_created_at(self, obj):
        return obj.created_at.timestamp()

class CreateLocationSerializer(serializers.ModelSerializer):
    kindred = serializers.PrimaryKeyRelatedField(queryset=Kindred.objects.all())

    class Meta:
        model = Location
        fields = ['coordinate', 'kindred']

    def validate(self, attrs):
        request = self.context['request']
        try:
            KindredMember.objects.get(user=request.user, kindred=attrs['kindred'])
        except KindredMember.DoesNotExist:
            raise serializers.ValidationError(_("You aren't member of this kindred."))
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        kindred_member = KindredMember.objects.get(user=request.user, kindred=validated_data['kindred'])
        location = Location.objects.create(coordinate=validated_data['coordinate'], kindred_member=kindred_member)
        try:
            socket.publish(f'kindred-{kindred_member.kindred.pk}', json.dumps({
                **RetrieveLocationSerializer(location, context={'request': request}).data,
                'action': 'new_location'
            },
                ensure_ascii=False
            ))
        except Exception:
            pass
        return location


class ListLocationsSerializer(serializers.Serializer):
    kindred = serializers.PrimaryKeyRelatedField(queryset=Kindred.objects.all())

    def validate(self, attrs):
        request = self.context['request']
        try:
            KindredMember.objects.get(user=request.user, kindred=attrs['kindred'])
        except KindredMember.DoesNotExist:
            raise serializers.ValidationError(_("You aren't member of this kindred."))
        return attrs

    def save(self, **kwargs):
        return self.validated_data['kindred']


class RetrieveShoppingItemSerializer(serializers.ModelSerializer):
    added_by = RetrieveKindredMemberSerializer()
    bought_by = RetrieveKindredMemberSerializer()
    added_at = serializers.SerializerMethodField()
    bought_at = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingItem
        fields = '__all__'

    def get_added_at(self, obj):
        return obj.added_at.timestamp()
    
    def get_bought_at(self, obj):
        if obj.is_bought:
            return obj.bought_at.timestamp()
        else:
            return None


class CreateShoppingItemSerializer(serializers.ModelSerializer):
    kindred = serializers.PrimaryKeyRelatedField(queryset=Kindred.objects.all())

    class Meta:
        model = ShoppingItem
        fields = ['name', 'kindred']

    def validate(self, attrs):
        request = self.context['request']
        try:
            KindredMember.objects.get(user=request.user, kindred=attrs['kindred'])
        except KindredMember.DoesNotExist:
            raise serializers.ValidationError(_("You aren't member of this kindred."))
        return attrs
    
    def create(self, validated_data):
        request = self.context['request']
        kindred_member = KindredMember.objects.get(user=request.user, kindred=validated_data.pop('kindred'))
        validated_data['added_by'] = kindred_member
        shopping_item = super().create(validated_data)
        try:
            socket.publish(f'kindred-{validated_data["added_by"].kindred.pk}', json.dumps({
                **RetrieveShoppingItemSerializer(shopping_item, context={'request': request}).data,
                'action': 'create_shopping_item'
            },
                ensure_ascii=False
            ))
        except Exception:
            pass
        return shopping_item


class EditShoppingItemSerializer(serializers.ModelSerializer):
    kindred = serializers.PrimaryKeyRelatedField(queryset=Kindred.objects.all())

    class Meta:
        model = ShoppingItem
        exclude = ('added_by',)
    
    def validate(self, attrs):
        request = self.context['request']
        try:
            KindredMember.objects.get(user=request.user, kindred=attrs['kindred'])
        except KindredMember.DoesNotExist:
            raise serializers.ValidationError(_("You aren't member of this kindred."))
        return attrs

    def update(self, instance, validated_data):
        request = self.context['request']
        if not instance.is_bought and validated_data.get('is_bought', None):
            validated_data['bought_by'] = KindredMember.objects.get(user=request.user, kindred=validated_data.pop('kindred'))
            validated_data['bought_at'] = datetime.utcnow()
        shopping_item = super().update(instance, validated_data)
        try:
            socket.publish(f'kindred-{validated_data["kindred"].pk}', json.dumps({
                **RetrieveShoppingItemSerializer(shopping_item, context={'request': request}).data,
                'action': 'edit_shopping_item'
            },
                ensure_ascii=False
            ))
        except Exception:
            pass

        return shopping_item


class InviteMemberSerializer(serializers.Serializer):
    kindred = serializers.PrimaryKeyRelatedField(queryset=Kindred.objects.all())
    phone_number = PhoneNumberField()

    def validate(self, attrs):
        request = self.context['request']
        try:
            KindredMember.objects.get(user=request.user, kindred=attrs['kindred'], is_admin=True)
        except KindredMember.DoesNotExist:
            raise serializers.ValidationError(_("You aren't admin of this kindred."))
        return attrs
    
    def save(self, **kwargs):
         phone_number = str(self.validated_data.pop('phone_number'))
         otp = random.randint(10000, 99999)
         cache_db.hmset(phone_number, {'kindred': self.validated_data['kindred'].pk, 'otp': otp, 'invited': 1})
         cache_db.expire(phone_number, timedelta(minutes=30))
         return otp


class InvitedMemberConfirmSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    otp = serializers.IntegerField()

    def validate(self, attrs):
        user_data = cache_db.hgetall(str(attrs['phone_number']))
        if not user_data or int(user_data['otp']) != attrs['otp'] or not int(user_data['invited']):
            raise serializers.ValidationError(_('OTP may be invalid or expired.'))
        return attrs
    
    def save(self, **kwargs):
        user_data = cache_db.hgetall(str(self.validated_data['phone_number']))
        cache_db.delete(str(self.validated_data['phone_number']))
        kindred = Kindred.objects.get(pk=user_data['kindred'])
        user = User.objects.create(
            phone_number=self.validated_data['phone_number'],
            default_kindred=kindred
        )
        kindred_member = KindredMember.objects.create(
            user=user,
            kindred=kindred
        )
        return kindred_member