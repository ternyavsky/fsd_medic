from rest_framework import serializers
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
from .models import *
from api.serializers import NewsSerializer, UserGetSerializer, CenterSerializer
from django.contrib.auth import get_user_model
from .services.chat_services import chat_create_data_validate
from .services.message_service import first_message_validate
from api.serializers import NewsPreviewSerializer
User = get_user_model()


class FirstMessageCreateSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    center_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    news = serializers.IntegerField(min_value=0, required=False)
    text = serializers.CharField(max_length=500, required=False)
    user = serializers.IntegerField(min_value=0, required=False)
    center = serializers.IntegerField(min_value=0, required=False)
    note = serializers.IntegerField(min_value=0, required=False)
    def validate(self, data):
        res, field, msg = chat_create_data_validate(data)
        if not res:
            raise serializers.ValidationError({field, msg})
        res, field, msg = first_message_validate(data)
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

class ChatSerializerNew(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'uuid', 'users', 'centers']


class ChatSerializer(serializers.ModelSerializer):
    to_user = UserGetSerializer()
    to_center = CenterSerializer()
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
