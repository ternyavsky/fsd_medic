from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import *
from .services.chat_services import chat_create_data_validate

User = get_user_model()


class ChatCreateSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    center_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

    def validate(self, data):
        res, field, msg = chat_create_data_validate(data)
        if not res:
            raise serializers.ValidationError({field, msg})
        return super().validate(data)


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "news", "chat", "note", "text", "user", "center", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = "__all__"
        depth = 1


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        depth = 1
