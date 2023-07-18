from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from fsd_medic.settings import AUTH_USER_MODEL
from api.models import News
import uuid

User = AUTH_USER_MODEL
# Create your models here.
class Chat(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='started')

    def __str__(self):
        return f"{self.id} Chat ({self.user1} -  {self.user2})"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.PROTECT,null=True, blank=True)
    text = models.TextField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message {self.user} - {self.chat}'