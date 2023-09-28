import logging
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from api.permissions import IsAdminOrReadOnly
from .services.chat_services import get_chat

# REST IMPORTS
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes, action, api_view
from db.queries import get_messages, get_chats
from .models import *
from .serializers import *
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from .serializers import ChatCreateSerializer,MessageCreateSerializer, ChatSerializer
from .services.chat_services import chat_create
from .services.message_service import get_message_data
logger = logging.getLogger(__name__)


# Create your views here.

class ChatCreate(APIView):
    @swagger_auto_schema(
        operation_summary="Сохраняет данные клиники в кэш",
        query_serializer=ChatCreateSerializer,
        responses={
            status.HTTP_200_OK: ChatSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        }
    )
    def post(self, request):
        print("SKJSAHASKJSHASAKJDAHJKJKHKJH")
        print(request.data)
        serializer = ChatCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            chat = chat_create(serializer.validated_data)
            chat_serializer = ChatSerializer(chat)
            if chat_serializer.is_valid():
                chat_data = chat_serializer.validated_data
                return Response(status=200, data=chat_data)
        else:
            return Response({'message': 'Неверный формат данных'}, status=status.HTTP_400_BAD_REQUEST)

class SendMessage(APIView):
    def post(self, request):
        pass


class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        messages = cache.get_or_set("messages", get_messages(chat=chat_id))
        serializer = MessageSerializer(messages, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        chat = cache.get_or_set("chat", get_chat(get_chats, user_id))
        serializer = ChatSerializer(chat, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)
