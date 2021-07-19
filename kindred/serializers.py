from users.serializers import RetrieveUserSerializer
from rest_framework import serializers
from .models import *


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
