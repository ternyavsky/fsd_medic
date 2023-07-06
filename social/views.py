from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import *


# Create your views here.

def room(request, uuid):
    chat = Chat.objects.get(uuid=uuid)
    return render(request, 'social/room.html', context=
    {
        'chat': chat.uuid,
        'user': request.user,
        'messages': Message.objects.all()
    })
