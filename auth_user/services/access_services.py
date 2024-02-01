from django.core.cache import cache

from api.models import Access
from api.serializers import UserSerializer
from db.queries import get_centers, get_chats, get_users, get_access, get_doctors
from django.db import transaction

from social.models import Notification, Chat

@transaction.atomic
def add_access_service(request):
    request.data["id"] = int(request.data["id"])
    users = cache.get_or_set("users", get_users())
    print(users.filter(id=int(request.data["id"])).first())
    user_to_access, uta_created = Access.objects.get_or_create(
        user=users.filter(id=request.data["id"]).first())
    user, user_created = Access.objects.get_or_create(
        user=users.filter(id=request.user.id).first())
    user.access_unaccept.add(user_to_access.user)
    user_to_access.access_unaccept.add(user.user)
    Notification.objects.create(
        user=user_to_access.user, text="Вам отправлен запрос на доступ от", add=UserSerializer(user.user).data)

@transaction.atomic
def accept_access_service(request):
    users = cache.get_or_set("users", get_users())
    user_i = users.filter(id=request.data["id"]).first()
    user = get_access(user=user_i).first()
    user_to_accept_access = get_access(
        user=users.filter(id=request.user.id).first()).first()
    user.access_unaccept.remove(user_to_accept_access.user)
    user_to_accept_access.access_unaccept.remove(user.user)
    user.access_accept.add(user_to_accept_access.user)
    user_to_accept_access.access_accept.add(user.user)
    chats = cache.get_or_set("chats", get_chats())
    doctor = cache.get_or_set("doctors", get_doctors()).filter(main_status=True, country=user.country).first()
    chat_to_add = chats.filter(doctors=doctor, users=user_i).first()
    chat_to_add.users.add(user_to_accept_access)


    

@transaction.atomic
def delete_access_service(request):
    users = cache.get_or_set("users", get_users())
    user_to_delete_access = get_access(
        user=users.filter(id=request.data["id"]).first()).first()
    user = get_access(user=users.filter(
        id=request.user.id).first()).first()
    if request.data["access"] == "accept":
        user.access_accept.remove(user_to_delete_access.user)
        user_to_delete_access.access_accept.remove(user.user)
    else:
        user.access_unaccept.remove(user_to_delete_access.user)
        user_to_delete_access.access_unaccept.remove(user.user)
