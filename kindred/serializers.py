import json
from users.serializers import RetrieveUserSerializer
from rest_framework import serializers
from .models import *
from .apps import socket


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