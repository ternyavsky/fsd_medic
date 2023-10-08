from django.core.cache import cache

from api.models import Access
from api.serializers import UserSerializer
from db.queries import get_users, get_access

from social.models import Notification, Chat


def add_access_service(request):
    users = cache.get_or_set("users", get_users())
    user_to_access, uta_created = Access.objects.get_or_create(
        user=users.filter(id=request.data["id"]).first())
    user, user_created = Access.objects.get_or_create(
        user=users.filter(id=request.user.id).first())
    user.access_unaccept.add(user_to_access.user)
    user_to_access.access_unaccept.add(user.user)
    Notification.objects.create(
        user=user_to_access.user, text="Вам отправлен запрос на доступ от", add=UserSerializer(user.user).data)


def accept_access_service(request):
    users = cache.get_or_set("users", get_users())
    user = get_access(user=users.filter(
        id=request.data["id"]).first()).first()
    user_to_accept_access = get_access(
        user=users.filter(id=request.user.id).first()).first()
    user.access_unaccept.remove(user_to_accept_access.user)
    user_to_accept_access.access_unaccept.remove(user.user)
    user.access_accept.add(user_to_accept_access.user)
    user_to_accept_access.access_accept.add(user.user)


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
