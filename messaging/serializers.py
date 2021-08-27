import json
from rest_framework import serializers
from .models import Message, DefaultMessage
from kindred.models import KindredMember
from django.utils.translation import ugettext_lazy as _
from kindred.serializers import RetrieveKindredMemberSerializer, RetrieveKindredSerializer
from kindred.apps import socket


class CreateMessageSerializer(serializers.ModelSerializer):
    default_message = serializers.PrimaryKeyRelatedField(queryset=DefaultMessage.objects.all(), required=False)
    content = serializers.CharField(required=False)

    class Meta:
        model = Message
        exclude = ('sent_from',)
    
    def validate(self, attrs):
        user = self.context['request'].user
        receiving_member = attrs['sent_to']
        default_message = attrs.get('default_message', None)
        content = attrs.get('content', None)
        try:
            KindredMember.objects.get(user=user, kindred=receiving_member.kindred)
        except KindredMember.DoesNotExist:
            raise serializers.ValidationError(_("You aren't member of this kindred."))
        if default_message and default_message.kindred != receiving_member.kindred:
            raise serializers.ValidationError(_("Given default message doesn't belong to this kindred."))
        if not content and not default_message:
            raise serializers.ValidationError(_('At least one of content or default_message fields are required.'))
        return attrs
    
    def create(self, validated_data):
        default_message = validated_data.get('default_message', None)
        user = self.context['request'].user
        sending_member = KindredMember.objects.get(user=user, kindred=validated_data['sent_to'].kindred)
        message = Message.objects.create(
            content=default_message.content if default_message else validated_data['content'],
            sent_from=sending_member,
            sent_to=validated_data['sent_to']
        )
        try:
            socket.publish(f'kindred-{sending_member.kindred.pk}', json.dumps({
                **RetrieveMessageSerializer(message, context=self.context).data,
                'action': 'new_message',
            },
                ensure_ascii=False
            ))
        except Exception:
            pass
        return message


class RetrieveMessageSerializer(serializers.ModelSerializer):
    sent_from = RetrieveKindredMemberSerializer()
    sent_to = RetrieveKindredMemberSerializer()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'
    
    def get_created_at(self, obj):
        return obj.created_at.timestamp()


class RetrieveChatMessageSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = '__all__'
    
    def get_created_at(self, obj):
        return obj.created_at.timestamp()


class CreateDefaultMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultMessage
        fields = '__all__'
    
    def validate(self, attrs):
        user = self.context['request'].user
        try:
            KindredMember.objects.get(user=user, kindred=attrs['kindred'])
        except KindredMember.DoesNotExist:
            raise serializers.ValidationError(_("You aren't member of this kindred."))
        return attrs


class RetrieveDefaultMessageSerializer(serializers.ModelSerializer):
    kindred = RetrieveKindredSerializer()
    class Meta:
        model = DefaultMessage
        fields = '__all__'


class UpdateDefaultMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultMessage
        exclude = ('kindred',)
