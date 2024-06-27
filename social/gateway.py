import socketio
from .helpers.jwt_decode import jwt_decode

# SOCKET_IO = socketio.Server(async_mode="eventlet")
from api.serializers import UserSerializer

from .serializers import ChatSerializer
from db.queries import get_chats, get_messages
from django.core.cache import cache
from .models import Message, Chat
from .helpers.create_message import create_message
from .helpers.update_message import update_message as upd_message
from .helpers.delete_message import delete_message as del_message
from fsd_medic.settings import SOCKET_IO


@SOCKET_IO.event
def connectCall(sid, token):
    print(sid, token, 19)
    # change user.online
    instance = jwt_decode(token)
    SOCKET_IO.emit("connectCall", {"instance connected": instance})


@SOCKET_IO.event
def disconnectCall(sid, token):
    # change user.online
    instance = jwt_decode(token, connect=False)
    SOCKET_IO.emit("disconnectCall", {"instance disconnected": instance})


@SOCKET_IO.event
def typing(sid, token, chat_id):
    instance = jwt_decode(token)
    chat = cache.get_or_set("chats", get_chats()).filter(id=chat_id).first()
    SOCKET_IO.emit(
        "typing", {"typing": {"chat": ChatSerializer(chat).data, "instance": instance}}
    )


@SOCKET_IO.event
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
    SOCKET_IO.emit("send_message", message)


@SOCKET_IO.event
def update_message(sid, text: str, message_id: Message.id):
    msg = cache.get_or_set("messages", get_messages()).filter(id=message_id).first()
    message = upd_message(msg, text)
    SOCKET_IO.emit("update_message", message)


@SOCKET_IO.event
def delete_message(sid, message_id: Message.id):
    msg = cache.get_or_set("messages", get_messages()).filter(id=message_id).first()
    message = del_message(msg)
    SOCKET_IO.emit("delete_message", message.id)
