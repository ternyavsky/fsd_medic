import logging
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from api.permissions import IsAdminOrReadOnly
from .service import get_chat

# REST IMPORTS
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes, action, api_view
from drf_yasg.utils import swagger_auto_schema
from db.queries import get_messages, get_chats
from .models import *
from .serializers import *
from django.core.cache import cache

logger = logging.getLogger(__name__)


# Create your views here.


class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Получение сообщений по конкретному чату")
    def get(self, request, chat_id):
        messages = cache.get_or_set("messages", get_messages(chat=chat_id))
        serializer = MessageSerializer(messages, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Получение чатов по конкретному пользователю")
    def get(self, request, user_id):
        chat = cache.get_or_set("chat", get_chat(get_chats, user_id))
        serializer = ChatSerializer(chat, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)
