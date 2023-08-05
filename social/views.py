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

from .models import *
from .serializers import *

from loguru import logger

logger.add("logs/social.log", format="{time} {level} {message}", level="DEBUG", rotation="12:00", compression="zip")



# Create your views here.



class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        try:
            messages = Message.objects.all().filter(chat=chat_id)
            serializer = MessageSerializer(messages, many=True)
            logger.debug(serializer.data)
            logger.success(request.path)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            logger.info("No messages")
            logger.info(request.path)
            return Response({'result': 'No messages'})


class ChatView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        obj = get_chat(Chat, user_id)
        serializer = ChatSerializer(obj, many=True)
        logger.debug(serializer.data)
        logger.success(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)


