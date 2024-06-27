from django.urls import path

from .views import ChatView, MessageView, NotificationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"api/notifications", NotificationViewSet, basename="notifications")
urlpatterns = [
    path(
        "api/chat/", ChatView.as_view(), name="chat_view_url"
    ),  # User chats with user_id
    path(
        "api/messages/<int:chat_id>/", MessageView.as_view(), name="messages_view_url"
    ),  # Chat messages with chat_id
]
urlpatterns += router.urls
