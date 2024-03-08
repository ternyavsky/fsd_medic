from ..models import Message, Chat
from api.models import User
from api.serializers import UserSerializer, DoctorGetSerializer
from ..serializers import MessageSerializer
from auth_doctor.models import Doctor
from .jwt_decode import jwt_decode
from django.core.cache import cache
from db.queries import get_users, get_doctors

def create_message(instance: User | Doctor, chat: Chat, text:str, reply: Message=None):
    print(type(instance) == User)
    if type(instance) == User:
        user = cache.get_or_set("users", get_users()).filter(id=instance["id"]).first()
        message = Message.objects.create(
            user=user,
            text=text,
            chat=chat,
            reply=reply if reply else None
            )
        message.save()
    else:
        doctor = cache.get_or_set("doctors", get_doctors()).filter(id=instance["id"]).first()
        message = Message.objects.create(
            doctor=doctor,
            text=text,
            chat=chat,
            reply=reply if reply else None
            )
        message.save()
    return MessageSerializer(message).data
