import json
from phonenumber_field.serializerfields import PhoneNumberField
from users.serializers import RetrieveUserSerializer
from rest_framework import serializers
from .models import *
from .apps import socket
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from kindred_backend.settings import cache_db
import random
import string


class RetrieveKindredSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Kindred
        exclude = ('unique_id',)

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
        invited_user = User.objects.filter(phone_number=attrs['phone_number']).first()
        if invited_user:
            if KindredMember.objects.filter(user=invited_user, kindred=attrs['kindred']):
                raise serializers.ValidationError(_('This phone number already exists in this kindred.'))
        try:
            KindredMember.objects.get(user=request.user, kindred=attrs['kindred'], is_admin=True)
        except KindredMember.DoesNotExist:
            raise serializers.ValidationError(_("You aren't admin of this kindred."))
        return attrs
    
    def save(self, **kwargs):
        kindred = self.validated_data['kindred']
        phone_number = str(self.validated_data.pop('phone_number'))
        cache_db.sadd(kindred.unique_id, phone_number)
        return kindred.unique_id


class InvitedMemberConfirmSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    invitation_code = serializers.CharField()

    def validate(self, attrs):
        try:
            user = User.objects.get(phone_number=attrs['phone_number'])
        except User.DoesNotExist:
            raise serializers.ValidationError(_('There is no user with this phone number.'))
        if not user.is_completed:
            raise serializers.ValidationError(_("You haven't completed your profile."))
        try:
            kindred = Kindred.objects.get(unique_id=attrs['invitation_code'])
        except Kindred.DoesNotExist:
            raise serializers.ValidationError(_('There is no kindred with this id.'))
        kindred_member_exists = KindredMember.objects.filter(user=user, kindred=kindred).exists()
        if kindred_member_exists:
            raise serializers.ValidationError(_('You are already member of this kindred.'))
        kindred_invited_members = cache_db.smembers(attrs['invitation_code'])
        if not kindred_invited_members or str(attrs['phone_number']) not in kindred_invited_members:
            raise serializers.ValidationError(_('Invitation code is invalid'))
        return attrs
    
    def save(self, **kwargs):
        
        cache_db.srem(self.validated_data['invitation_code'], str(self.validated_data['phone_number']))
        kindred = Kindred.objects.get(unique_id=self.validated_data['invitation_code'])
        user = User.objects.get(
            phone_number=self.validated_data['phone_number']
        )
        kindred_member = KindredMember.objects.create(
            user=user,
            kindred=kindred
        )
        if not user.default_kindred:
            user.default_kindred = kindred
            user.save()
        return kindred_member


class CreateKindredSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_completed:
            raise serializers.ValidationError(_('Please complete your profile first.'))
        return attrs

    class Meta:
        model = Kindred
        fields = ['name', 'image']
    
    def create(self, validated_data):
        user = self.context['request'].user
        letters = string.ascii_lowercase + string.digits
        result_str = ''.join(random.choice(letters) for i in range(8))
        while result_str in Kindred.objects.values_list('unique_id', flat=True):
            result_str = ''.join(random.choice(letters) for i in range(8))
        validated_data['unique_id'] = result_str
        kindred = super().create(validated_data)
        if not user.default_kindred:
            user.default_kindred = kindred
            user.save()
        KindredMember.objects.create(user=user, kindred=kindred, is_admin=True)
        return kindred


class ListKindredMembersSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = KindredMember
        exclude = ('kindred',)

    def get_user(self, obj):
        data = RetrieveUserSerializer(obj.user, context=self.context).data
        del data['kindreds']
        return data


class ChangeKindredAdminSerializer(serializers.Serializer):
    kindred_member = serializers.PrimaryKeyRelatedField(queryset=KindredMember.objects.all())
    kindred = serializers.PrimaryKeyRelatedField(queryset=Kindred.objects.all())

    def validate(self, attrs):
        request = self.context['request']
        kindred_member = KindredMember.objects.filter(user=request.user, kindred=attrs['kindred'], is_admin=True).first()
        if not kindred_member:
            raise serializers.ValidationError(_("You aren't admin of this kindred."))
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        old_admin = KindredMember.objects.get(kindred=self.validated_data['kindred'], user=user)
        old_admin.is_admin = False
        old_admin.save()
        new_admin = self.validated_data['kindred_member']
        new_admin.is_admin = True
        new_admin.save()
        return new_admin


class RemoveKindredMemberSerializer(serializers.Serializer):
    kindred_member = serializers.PrimaryKeyRelatedField(queryset=KindredMember.objects.all())
    kindred = serializers.PrimaryKeyRelatedField(queryset=Kindred.objects.all())

    def validate(self, attrs):
        request = self.context['request']
        kindred_member = KindredMember.objects.filter(user=request.user, kindred=attrs['kindred']).first()
        if not kindred_member:
            raise serializers.ValidationError(_("You aren't member of this kindred."))
        if kindred_member == attrs['kindred_member'] and kindred_member.is_admin:
            raise serializers.ValidationError(_("You can't remove yourself while you're admin. Change the admin first."))
        if kindred_member != attrs['kindred_member'] and not kindred_member.is_admin:
            raise serializers.ValidationError(_("You aren't admin of this kindred."))
        return attrs
    
    def save(self, **kwargs):
        self.validated_data['kindred_member'].delete()
