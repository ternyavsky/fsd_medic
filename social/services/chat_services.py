from ..models import Chat
from django.db.models import Q
from api.models import User, Center






def chat_create_data_validate(data: dict) -> tuple[bool,str, str]:
    user_ids = data.get("user_ids")
    if user_ids is not None:
        for user_id in user_ids:
            if not User.objects.filter(id=user_id).exists():
                return False,"user_ids", "Пользователя с таким id не существует"
    if len(user_ids) == 0:
        return False,"user_ids", "Добавьте хотябы одного пациента в чат"
    center_ids = data.get("center_ids")
    if center_ids is not None:
        for center_id in center_ids:
            if not Center.objects.filter(id=center_id).exists():
                return False,"center_ids", "Центра с таким id не существует"
    if len(center_ids) == 0:
        return False,"center_ids", "Добавьте хотябы один центр в чат"
    return True, "", ""


def chat_create(validated_data: dict):
    chat = Chat()
    chat.save()
    user_ids = validated_data.get("user_ids")
    center_ids = validated_data.get("center_ids")
    users = User.objects.filter(id__in=user_ids)
    centers = Center.objects.filter(id__in=center_ids)
    chat.users.add(*users)
    chat.centers.add(*centers)
    chat.save()
    return chat