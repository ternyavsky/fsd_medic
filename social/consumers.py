import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.decorators import action
from api.serializers import UserGetSerializer, CenterSerializer, NewsSerializer
from api.models import Centers, News

from .models import Chat, Message

from .serializers import MessageSerializer, ChatSerializer, UserSerializer

User = get_user_model()


class NotifyConsumer(GenericAsyncAPIConsumer):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer


    @action()
    async def subscribe_to_main_center_activity(self, request_id, **kwargs):
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        user = await database_sync_to_async(User.objects.get)(id=user_id)
        center = user.main_center
        print('Main center user with id', user_id, center)
        await self.main_center_activity.subscribe(center=center.id)



    @model_observer(News)
    async def main_center_activity(self, message, observer=None, **kwargs):
        if message["action"] == 'create':
            await self.send_json(message)

    @main_center_activity.groups_for_signal
    def main_center_activity(self, instance: News, **kwargs):
        yield f'center__{instance.center_id}'

    @main_center_activity.groups_for_consumer
    def main_center_activity(self, center, **kwargs):
        yield f'center__{center}'


    @main_center_activity.serializer
    def main_center_activity(self, instance, action, **kwargs):
        return dict(text="New post from main center",  data=NewsSerializer(instance).data, action=action.value, pk=instance.pk)
    
    @action()
    async def subscribe_to_centers_activity(self, **kwargs):
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        user = await database_sync_to_async(User.objects.get)(id=user_id)
        await self.centers_activity.subscribe(center=user.centers.all())
    
    @model_observer(News)
    async def centers_activity(self, message, observer=None, **kwargs):
        if message["update"] == 'create':
            await self.send_json(message)


    @centers_activity.groups_for_signal
    def centers_activity(self, instance: News, **kwargs):
        yield f'center__{instance.center_id}'

    @centers_activity.groups_for_consumer
    def centers_activity(self, center, **kwargs):
        for i in center:
            yield f'center__{i.id}'

    @centers_activity.serializer
    def centers_activity(self, instance, action, **kwargs):
        return dict(text="New post from user centers", data=NewsSerializer(instance).data, action=action.value, pk=instance.pk)

class MyConsumer(AsyncWebsocketConsumer):
    queryset = Message.objects.all()
    serializer = MessageSerializer

    #### CONNECT ####
    # ACTION WITH USER CONNECTED, THAT RECIEVE ON CONNECT
    active_users = []

    async def connect(self):
        self.chat_uuid = self.scope["url_route"]["kwargs"]["chat_uuid"]
        self.group_name = "chat_%s" % self.chat_uuid

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        user = User.objects.get(id=user_id)

        self.active_users.append(UserGetSerializer(user).data)

        

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "connect_to",
                "message": 'user connect',
                "user": self.scope['url_route']["kwargs"]["user_id"]
            },
        )

        chat = Chat.objects.get(uuid=self.chat_uuid)
        messages = await database_sync_to_async(self.queryset.filter)(chat=chat)

        await self.send(
            text_data=json.dumps({
                'action': 'list_message',
                'messages': dict(data=self.serializer(instance=messages, many=True).data)
            })
        )

    # FUNCTION, THAT SEND JSON ON CONNECT
    async def connect_to(self, event):
        print(event, 'evented')
        await self.send(
            text_data=json.dumps({
                'message': f'user with id - {event["user"]} online',
                'active_users': self.active_users
            })
        )

    #### CONNECT ####

    #### DISCONNECT ####
    # ACTION WITH USER DICCONNECTED, THAT RECIEVE ON DISCONNECT
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        user_id = self.scope['url_route']["kwargs"]["user_id"]
        user = User.objects.get(id=user_id)

        self.active_users.remove(UserGetSerializer(user).data)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "disconnect_to",
                "message": 'user disconnect',
                "user": self.scope['url_route']["kwargs"]["user_id"]
            },
        )

    # FUNCTION, THAT SEND JSON ON DISCONNECT
    async def disconnect_to(self, event):
        await self.send(
            text_data=json.dumps({
                'message': f'user with id - {event["user"]} disconnected',
                'active_users': self.active_users
            })
        )

    #### DISCONNECT ####

    # This function receive messages from WebSocket.
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data["action"]
        match action:  # CHOICE ACTION
            case 'send_message':
                obj = await database_sync_to_async(Message.objects.create)(
                    text=data["text"],
                    chat=Chat.objects.get(uuid=data["chat_uuid"]),
                    user=User.objects.get(id=data["user_id"])
                )
                message = dict(data=self.serializer(instance=obj).data)
                action_type = "send_message"

            case 'delete_message':
                obj = await self.get_message_db(data["pk"])
                await self.delete_message_db(data["pk"])
                message = dict(data=self.serializer(instance=obj).data)
                action_type = "delete_message"

            case 'update_message':
                upd = await self.update_message_db(data["pk"], data["text"])
                message = dict(data=self.serializer(instance=upd). data)
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
    def update_message_db(self, id, text):
        Message.objects.filter(id=id).update(text=text)
        message = Message.objects.get(id=id)
        return message

    @database_sync_to_async
    def delete_message_db(self, id):
        message = Message.objects.get(id=id)
        message.delete()

    @database_sync_to_async
    def get_message_db(self, id):
        message = Message.objects.get(id=id)
        return message



