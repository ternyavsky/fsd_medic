import logging

from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# REST IMPORTS
from rest_framework.views import APIView

from .models import Notification
from db.queries import get_messages, get_chats, get_notifications
from .serializers import *
from api.serializers import NotificationSerializer, ChatSerializer
from .serializers import ChatCreateSerializer 
from .services.chat_services import chat_create
import socketio
logger = logging.getLogger(__name__)




# Create your views here.

class NotifyView(APIView):
    # permission_classes = [IsAuthenticated]


    def get(self, request):
        notifications = cache.get_or_set("notifications", get_notifications()) 
        serializer = NotificationSerializer(notifications, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ChatCreate(APIView):

    def post(self, request):
        serializer = ChatCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            chat = chat_create(serializer.validated_data)
            return Response(status=200, data={"chat_id": chat.id})


class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        messages = cache.get_or_set("messages", get_messages())
        result = messages.filter(chat_id=chat_id).order_by("-created_at")
        serializer = MessageSerializer(result, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_summary="Получение чатов по конкретному пользователю")
    def get(self, request):
        chat = cache.get_or_set("chats", get_chats())
        result = chat.filter(users=request.user)
        serializer = ChatSerializer(result, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)
