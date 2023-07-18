from .models import Chat
from django.db.models import Q
def get_chat(Chat, user_id):
    obj1 = Chat.objects.all().filter(from_user=user_id)
    obj2 = Chat.objects.all().filter(to_user=user_id)
    return obj1 ^ obj2

