import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, StopConsumer
from django.contrib.auth import get_user_model
from django.utils import text
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from django.core.cache import cache
from db.queries import get_chats, get_messages, get_users
from api.serializers import UserSerializer, CenterSerializer, DoctorGetSerializer
from .models import Chat, Message, Notification
from .serializers import MessageSerializer, NotificationSerializer
from django.db import transaction
from api.models import Center
from auth_doctor.models import Doctor

User = get_user_model()

logger = logging.getLogger(__name__)


class NotifyConsumer(GenericAsyncAPIConsumer, AsyncWebsocketConsumer):
    queryset = cache.get_or_set("users", get_users())
    serializer_class = UserSerializer


    @action()
    async def subscribe_to_notify_activity(self, request_id, **kwargs):
        user = await database_sync_to_async(User.objects.get)(id=self.scope["user"].id)
        await self.notify_activity.subscribe(user=user.id)

    @model_observer(Notification)
    async def notify_activity(self, message, observer=None, **kwargs):
        logger.debug(message)
        print(message)
        await self.send_json(message)

    @notify_activity.groups_for_signal
    def notify_activity(self, instance: Notification, **kwargs):
        yield f'user__{instance.user_id}'

    @notify_activity.groups_for_consumer
    def notify_activity(self, user, **kwargs):
        yield f'user__{user}'

    @notify_activity.serializer
    def notify_activity(self, instance, action, **kwargs):
        data = NotificationSerializer(instance).data
        print(data)
        return dict(data=data, type="notify", pk=instance.pk)

    def websocket_disconnect(self, message):
        print(message)
        raise StopConsumer()


class MyConsumer(AsyncWebsocketConsumer):
    queryset = cache.get_or_set("messages", get_messages())
    serializer = MessageSerializer

    #### CONNECT ####
    # ACTION WITH USER CONNECTED, THAT RECIEVE ON CONNECT
    active_entities = {}
    chats = cache.get_or_set("chats", get_chats())
    messages = cache.get_or_set("messages", get_messages())
    users = cache.get_or_set("users", get_users())
    hour = 60*60

    async def connect(self):
        self.chat_uuid = self.scope["url_route"]["kwargs"]["chat_uuid"]
        self.group_name = "chat_%s" % self.chat_uuid
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(self.scope["user"], 76)
        chat = self.chats.filter(uuid=self.chat_uuid).first()
        logger.debug(chat)
        data = {}
        serialize = UserSerializer(User.objects.get(number=self.scope["user"])).data
        data["number"] = serialize["number"]
        data["first_name"] = serialize["first_name"]

        a = cache.get(self.chat_uuid)
        if a:
            print("a != none")
            print(a, 86)
            if data not in a:
                a.append(data)
            print(a, 88)
            cache.set(self.chat_uuid, a, self.hour)
        else:
            cache.set(self.chat_uuid, [data], self.hour)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "open",
                "message": self.active_entities
            }
        )
        messages = await database_sync_to_async(self.queryset.filter)(chat=chat)
        logger.debug(messages)
        await self.send(
            text_data=json.dumps({
                'action': 'list_message',
                'chat': self.chat_uuid,
                'messages': dict(data=self.serializer(instance=messages, many=True).data)
            })  
        )

    async def open(self, e):
        await self.send(
            text_data=json.dumps({
                "action": 'user connect',
                "chat": self.chat_uuid,
                "online_users": cache.get(self.chat_uuid)
            })
        )
        

    #### CONNECT ####

    #### DISCONNECT ####
    # ACTION WITH USER DICCONNECTED, THAT RECIEVE ON DISCONNECT
    async def disconnect(self, code):
        data = {}
        serialize = UserSerializer(User.objects.get(number=self.scope["user"])).data
        data["number"] = serialize["number"]
        data["first_name"] = serialize["first_name"]
        
        a = cache.get(self.chat_uuid, None)
        a.remove(data)
        cache.set(self.chat_uuid, a, self.hour)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "close",
                "message": self.active_entities
            }
        )
    async def close(self, e):
        await self.send(text_data=json.dumps({
            "action": "user disconnect",
            "chat": self.chat_uuid,
            "online_users": cache.get(self.chat_uuid)
        }))


    #### DISCONNECT ####

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data, "data")
        
        action = data["action"]
        match action:  # CHOICE ACTION
            case 'typing':
                action_type = "typing"
                message = self.scope["user"]

            case 'send_message':
                obj = await database_sync_to_async(Message.objects.create)(
                    text=data["text"],
                    chat=self.chats.filter(uuid=data["chat_uuid"]).first(),
                    user=self.users.filter(id=self.scope["user"].id).first(),
                    note=data["note"] if "note" in data else None,
                    news=data["news"] if "news" in data else None
                )
                logger.debug(obj)
                message = dict(data=self.serializer(instance=obj).data)
                logger.debug(message)
                action_type = "send_message"

            case 'delete_message':
                obj = await self.get_message_db(data["pk"])
                logger.debug(obj)
                await self.delete_message_db(data["pk"])
                message = dict(data=self.serializer(instance=obj).data)
                logger.debug(message)
                action_type = "delete_message"

            case 'update_message':
                upd = await self.update_message_db(data["pk"], data["text"])
                logger.debug(upd)
                message = dict(data=self.serializer(instance=upd).data)
                logger.debug(message)
                action_type = "update_message"

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": action_type,
                "action": action,
                "message": message
            }
        )
        ### ACTION WITH CALLED WHEN SEND MESSAGE ###


    async def typing(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "aciton": event["action"],
                    "message": f"{event['message']} typing..."
                }
            )
        )
    async def update_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "action": event["action"],
                    "message": event["message"]
                }
            )
        )
        await self.disconnect(401)

    
    

    async def send_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "action": event["action"],
                    "message": event["message"]
                }
            )
        )

    ### ACTION WITH CALLED WHEN SEND MESSAGE ###

    ### ACTION WITH CALLED WHEN DELETE MESSAGE ###
    async def delete_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "action": event["action"],
                    "message": event["message"]
                }
            )
        )

    ### ACTION WITH CALLED WHEN SEND MESSAGE ###
    # Receive message from room group.
    #####  UTILS FOR DATABASE ####

    @database_sync_to_async
    @transaction.atomic
    def update_message_db(self, id, text):
        self.messages.filter(id=id).first().update(text=text)
        message = self.messages.filter(id=id).first()
        return message

    @database_sync_to_async
    def delete_message_db(self, id):
        message = self.messages.filter(id=id).first()
        message.delete()

    @database_sync_to_async
    def get_message_db(self, id):
        message = self.messages.filter(id=id).first()
        return message
