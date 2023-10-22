import logging

from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# REST IMPORTS
from rest_framework.views import APIView

from db.queries import get_messages, get_chats
from .serializers import *
from .serializers import ChatCreateSerializer, ChatSerializer
from .services.chat_services import chat_create

logger = logging.getLogger(__name__)


# Create your views here.

class ChatCreate(APIView):
    @swagger_auto_schema(
        operation_summary="Создание чата при первом сообщении",
        query_serializer=ChatCreateSerializer,
        responses={
            status.HTTP_200_OK: ChatSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        }
    )
    def post(self, request):
        serializer = ChatCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            chat = chat_create(serializer.validated_data)
            return Response(status=200, data={"chat_id": chat.id})
        else:
            return Response({'message': 'Неверный формат данных'}, status=status.HTTP_400_BAD_REQUEST)


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
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Получение чатов по конкретному пользователю")
    def get(self, request, user_id):
        chat = cache.get_or_set("chats", get_chats())
        result = chat.filter(users__id=user_id)
        serializer = ChatSerializer(result, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)
