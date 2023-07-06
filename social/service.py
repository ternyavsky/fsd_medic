from .models import Chat
from django.db.models import Q
def get_chat(Chat, user_id):
    obj = Chat.objects.all().filter(user1=user_id) ^ Chat.objects.all().filter(user2=user_id)
    return obj

