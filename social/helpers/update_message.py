from ..models import Message, Chat
from api.models import User 
from api.serializers import UserSerializer, DoctorGetSerializer
from ..serializers import MessageSerializer
from auth_doctor.models import Doctor
from .jwt_decode import jwt_decode
from django.core.cache import cache
from db.queries import get_users, get_doctors

def update_message(message:Message, text:str):
    message = Message.objects.update(
        text=text
    )
    message.save()
    return MessageSerializer(message).data