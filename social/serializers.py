from rest_framework import serializers
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
from .models import *
from api.serializers import NewsSerializer, UserGetSerializer, CenterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSerializer(serializers.ModelSerializer):
    to_user = UserGetSerializer()
    to_center= CenterSerializer()
    from_center = CenterSerializer()
    from_user = UserGetSerializer()

    class Meta:
        model = Chat
        fields = ['id', 'uuid', 'to_user', 'to_center' ,'from_center', 'from_user']





class MessageSerializer(serializers.ModelSerializer):
    news = PresentablePrimaryKeyRelatedField(
        queryset=News.objects.all(),
        presentation_serializer=NewsSerializer,
        required=False
    )
    chat = PresentablePrimaryKeyRelatedField(
        queryset=Chat.objects.all(),
        presentation_serializer=ChatSerializer
    )
    user = PresentablePrimaryKeyRelatedField(
        queryset=User.objects.all(),
        presentation_serializer=UserGetSerializer
    )
    created_at_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['pk', 'text', 'chat', 'user', 'news', 'created_at_formatted']

    def get_created_at_formatted(self, obj: Message):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
