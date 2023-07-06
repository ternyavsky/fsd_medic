from rest_framework import serializers
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
from .models import *
from api.serializers import NewsSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', "first_name", "email"]

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['first_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChatSerializer(serializers.Serializer):
    user1 = UserSerializer()
    user2 = UserSerializer()

    def create(self, validated_data):
        chat = Chat(
            user1=validated_data['user1'],
            user2=validated_data['user2']
        )
        chat.save()
        return chat

    class Meta:
        fields = ['pk', 'uuid', 'user1', 'user2']


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
        presentation_serializer=UserSerializer
    )
    created_at_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['pk', 'text', 'chat', 'user', 'news', 'created_at_formatted']

    def get_created_at_formatted(self, obj: Message):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
