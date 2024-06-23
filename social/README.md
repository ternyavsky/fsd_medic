<h1>Chat docs</h1>

## Setup
#![Screenshot from 2023-11-22 15-19-42](https://github.com/ternyavsky/fsd_medic/assets/105453132/e5098369-a540-451d-aaca-8406ac5697c6)
<p> connect ws for each user chat with token as query param</p>

![Screenshot from 2023-11-22 15-27-27](https://github.com/ternyavsky/fsd_medic/assets/105453132/a88a0777-4e70-43ed-acac-ac261987552f)


## Connect
<p>when connect you see message list for each chat, and list online users this chat</p>

![image](https://github.com/ternyavsky/fsd_medic/assets/105453132/3117521d-ad2b-4b6a-8b6b-bc18125845b1)

## Send message

![image](https://github.com/ternyavsky/fsd_medic/assets/105453132/1b559b37-409d-4995-a2ce-6a14338a0d64)

## Update, delete

![image](https://github.com/ternyavsky/fsd_medic/assets/105453132/d6bc7a89-eef9-4fa1-a0ce-fe051d415256)

## Typing
reacthotkeys, smth that

![image](https://github.com/ternyavsky/fsd_medic/assets/105453132/a8c0f072-1e65-49ec-b3a2-fc1597337c5e)


## Disconnect
<p>like connect </p>

![image](https://github.com/ternyavsky/fsd_medic/assets/105453132/e8673949-f5af-4fab-8676-44141490db8c)


## Unread messages
<p>unread message added into user model, but they created only when user inacitve(out of socket)
Because of this, those messages that come when a user activ(inside the socket) can be increased through the react state, but this will not be fixed in any way in the database</p>

![image](https://github.com/ternyavsky/fsd_medic/assets/105453132/cb2fe455-1639-47c1-853c-39ef32aa30a1)
