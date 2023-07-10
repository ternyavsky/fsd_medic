import os
from twilio.rest import Client

account_sid = 'ACd548081533cb63842df3f788a3920ad8'
auth_token = '68ff76d15a270c72e6b5ac114bb224fb'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Тимур, привет. Это тествое сообщение с twilio",
                     from_='+18335872557',
                     to='+13475437408'
                 )

print(message.body)