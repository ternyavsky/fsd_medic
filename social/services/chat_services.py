from ..models import Chat
from django.db.models import Q
from api.models import User, Center



def get_chat(Chat, user_id):
    obj1 = Chat.objects.all().filter(from_user=user_id)
    obj2 = Chat.objects.all().filter(to_user=user_id)
    return obj1 ^ obj2


def chat_create_data_validate(data: dict) -> tuple[bool,str, str]:
    user_ids = data.get("user_ids")
    if user_ids is not None:
        for user_id in user_ids:
            if not User.objects.filter(id=user_id).exists():
                return False,"user_ids", "Пользователя с таким id не существует"
    center_ids = data.get("center_ids")
    if center_ids is not None:
        for center_id in center_ids:
            if not Center.objects.filter(id=center_id).exists():
                return False,"center_ids", "Центра с таким id не существует"
    return True, "", ""


def chat_create(validated_data: dict):
    chat = Chat()
    user_ids = validated_data.get("user_ids")
    center_ids = validated_data.get("center_ids")
    users = User.objects.filter(id__in=user_ids)
    centers = Center.objects.filter(id__in=center_ids)
    chat.users.add(*users)
    chat.centers.add(*centers)
    chat.save()
    return chat