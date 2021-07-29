import json
from users.serializers import RetrieveUserSerializer
from rest_framework import serializers
from .models import *
from .apps import socket
from django.utils.translation import ugettext_lazy as _
from datetime import datetime


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
            socket.publish(f'kindred-{kindred_member.kindred.pk}', json.dumps(
                RetrieveLocationSerializer(location, context={'request': request}).data
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
            socket.publish(f'kindred-{validated_data["added_by"].kindred.pk}', json.dumps(
                RetrieveShoppingItemSerializer(shopping_item, context={'request': request}).data
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
            socket.publish(f'kindred-{validated_data["kindred"].pk}', json.dumps(
                RetrieveShoppingItemSerializer(shopping_item, context={'request': request}).data
            ))
        except Exception:
            pass

        return shopping_item