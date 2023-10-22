from django.urls import path

from .views import ChatView, MessageView, NotifyView

urlpatterns = [
    path('api/chat/<int:user_id>/', ChatView.as_view(), name='chat_view_url'),  # User chats with user_id
    path('api/messages/<int:chat_id>/', MessageView.as_view(), name='messages_view_url'),  # Chat messages with chat_id
    path('api/notifications/<int:user_id>', NotifyView.as_view(), name='notify_view_url')
]
