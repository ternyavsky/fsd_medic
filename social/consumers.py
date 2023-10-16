import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, StopConsumer
from django.contrib.auth import get_user_model
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


class NotifyConsumer(GenericAsyncAPIConsumer):
    queryset = cache.get_or_set("users", get_users())
    serializer_class = UserSerializer

    @action()
    async def subscribe_to_notify_activity(self, request_id, **kwargs):
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        user = await database_sync_to_async(User.objects.get)(id=user_id)
        await self.notify_activity.subscribe(user=user_id)

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
    active_entities = []
    chats = cache.get_or_set("chats", get_chats())
    messages = cache.get_or_set("messages", get_messages())
    users = cache.get_or_set("users", get_users())

    async def connect(self):
        self.chat_uuid = self.scope["url_route"]["kwargs"]["chat_uuid"]
        self.group_name = "chat_%s" % self.chat_uuid
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        chat = self.chats.filter(uuid=self.chat_uuid).first()
        logger.debug(chat)
        messages = await database_sync_to_async(self.queryset.filter)(chat=chat)
        logger.debug(messages)
        await self.send(
            text_data=json.dumps({
                'action': 'list_message',
                'messages': dict(data=self.serializer(instance=messages, many=True).data)
            })  
        )

    #### CONNECT ####

    #### DISCONNECT ####
    # ACTION WITH USER DICCONNECTED, THAT RECIEVE ON DISCONNECT


    #### DISCONNECT ####

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data, "data")
        action = data["action"]
        match action:  # CHOICE ACTION
            case 'connect_entity':
                if data['type'] == 'user':
                    obj = await database_sync_to_async(User.objects.get)(
                        id=data['id']
                    )
                    ins = UserSerializer(obj).data

                elif data['type'] == 'center':
                    obj = await database_sync_to_async(Center.objects.get)(
                        id=data['id']
                    )
                    ins = CenterSerializer(obj).data

                elif data["type"] == 'doctor':
                    obj = await database_sync_to_async(Doctor.objects.get)(
                        id=data['id']
                    )

                    ins = DoctorGetSerializer(obj).data
                if ins not in self.active_entities:
                    self.active_entities.append(ins)
                message = {
                    "message": "connected", 
                    "active_entities": self.active_entities 
                    }
                action_type = "connect_entity"
                
            case 'disconnect_entity':
                if data['type'] == 'user':
                    obj = await database_sync_to_async(User.objects.get)(
                        id=data['id']
                    )
                    ins = UserSerializer(obj).data

                elif data['type'] == 'center':
                    obj = await database_sync_to_async(Center.objects.get)(
                        id=data['id']
                    )
                    ins = CenterSerializer(obj).data

                elif data["type"] == 'doctor':
                    obj = await database_sync_to_async(Doctor.objects.get)(
                        id=data['id']
                    )

                    ins = DoctorGetSerializer(obj).data
                self.active_entities.remove(ins)
                message = {
                    "message": "disconnected", 
                    "active_entities": self.active_entities 
                    }
                action_type = "disconnect_entity"
            
            case 'send_message':
                obj = await database_sync_to_async(Message.objects.create)(
                    text=data["text"],
                    chat=self.chats.filter(uuid=data["chat_uuid"]).first(),
                    user=self.users.filter(id=data["user_id"]).first(),
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

    async def update_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "action": event["action"],
                    "message": event["message"]
                }
            )
        )
    async def connect_entity(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "action": event["action"],
                    "message": event["message"]
                }
            )
        )
    async def disconnect_entity(self, event):
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
