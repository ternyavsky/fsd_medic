import socketio
from .helpers.jwt_decode import jwt_decode

# server = socketio.Server(async_mode="eventlet")
server = socketio.Server(cors_allowed_origins="*", async_mode="eventlet")
from api.serializers import UserSerializer
from .serializers import ChatSerializer
from db.queries import get_chats, get_messages
from django.core.cache import cache
from .models import Message, Chat
from .helpers.create_message import create_message
from .helpers.update_message import update_message as upd_message
from .helpers.delete_message import delete_message as del_message


@server.event
def connectCall(sid, token):
    # change user.online
    instance = jwt_decode(token)
    server.emit("connectCall", {"instance connected": instance})


@server.event
def disconnectCall(sid, token):
    # change user.online
    instance = jwt_decode(token, connect=False)
    server.emit("disconnectCall", {"instance disconnected": instance})


@server.event
def typing(sid, token, chat_id):
    instance = jwt_decode(token)
    chat = cache.get_or_set("chats", get_chats()).filter(id=chat_id).first()
    server.emit(
        "typing", {"typing": {"chat": ChatSerializer(chat).data, "instance": instance}}
    )


@server.event
def send_message(
    sid, token: str, chat_id: Chat.id, text: str, reply_id: Message.id = None
):
    instance = jwt_decode(token)
    chat = cache.get_or_set("chats", get_chats()).filter(id=chat_id).first()
    reply = (
        cache.get_or_set("messages", get_messages()).filter(id=reply_id).first()
        if reply_id
        else None
    )
    message = (
        create_message(instance, chat, text, reply)
        if reply
        else create_message(instance, chat, text)
    )
    server.emit("send_message", message)


@server.event
def update_message(sid, text: str, message_id: Message.id):
    msg = cache.get_or_set("messages", get_messages()).filter(id=message_id).first()
    message = upd_message(msg, text)
    server.emit("update_message", message)


@server.event
def delete_message(sid, message_id: Message.id):
    msg = cache.get_or_set("messages", get_messages()).filter(id=message_id).first()
    message = del_message(msg)
    server.emit("delete_message", message.id)
