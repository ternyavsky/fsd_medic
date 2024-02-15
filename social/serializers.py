from django.contrib.auth import get_user_model
from rest_framework import fields, serializers


from api import serializers as api_s

from .models import *
from .services.chat_services import chat_create_data_validate

User = get_user_model()



class UnreadMsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnreadMessage
        fields = "__all__"
       # depth = 1

class ChatCreateSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    center_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

    def validate(self, data):
        res, field, msg = chat_create_data_validate(data)
        if not res:
            raise serializers.ValidationError({field, msg})
        return super().validate(data)


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "news", "chat", "note", "text", "user",  "created_at"]




class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = "__all__"
        #depth = 1


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
       # depth = 1
