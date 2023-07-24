import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from api.serializers import UserGetSerializer

from .models import Chat, Message
from .serializers import MessageSerializer, ChatSerializer, UserSerializer

User = get_user_model()


class NotifyConsumber(AsyncWebsocketConsumer):
    queryset = User.objects.all()
    serializer = UserGetSerializer
   
    online_users = [] 

    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.user = User.objects.get(id=user_id)
        self.group_name = "socket user_%s" % self.user_id
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        self.online_user.append(UserGetSerializerer(user).data)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "connect_to",
                "message": 'user connect',
                "user": self.scope['url_route']["kwargs"]["user_id"]
            },
        )


class MyConsumer(AsyncWebsocketConsumer):
    queryset = Message.objects.all()
    serializer = MessageSerializer

    #### CONNECT ####
    # ACTION WITH USER CONNECTED, THAT RECIEVE ON CONNECT
    active_users = []

    async def connect(self):
        self.chat_uuid = self.scope["url_route"]["kwargs"]["chat_uuid"]
        self.group_name = "socket chat_%s" % self.chat_uuid

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

        self.active_users.remove(UserSerializer(user).data)

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



