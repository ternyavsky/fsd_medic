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


# Create your views here.




class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        try:
            messages = Message.objects.all().filter(chat=chat_id)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'result': 'Сообщений нет'})

class ChatView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        obj = get_chat(Chat, user_id)
        serializer = ChatSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



def room(request, uuid):
    chat = Chat.objects.get(uuid=uuid)
    return render(request, 'social/room.html', context=
    {
        'chat': chat.uuid,
        'user': request.user,
        'messages': Message.objects.all()
    })
