# Create your models here.
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import News, Center, Note
from auth_doctor.models import Doctor
from fsd_medic.settings import AUTH_USER_MODEL

User = AUTH_USER_MODEL


# Create your models here.


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=220, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text} {self.user}"

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class Chat(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    users = models.ManyToManyField(User, verbose_name=_("Пациенты"), blank=True)
    doctors = models.ManyToManyField(Doctor, verbose_name=_("Врачи"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat - {self.uuid}"

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

class Message(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.PROTECT, null=True, blank=True)
    reply = models.ForeignKey("Message", on_delete=models.CASCADE, related_name="reply_message", null=True, blank=True)
    note = models.ForeignKey(Note, on_delete=models.PROTECT, null=True, blank=True)
    text = models.TextField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # отправитель
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)  # отправитель
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Message {self.user} - {self.chat}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

class UnreadMessage(models.Model):
    message = models.ForeignKey(Message, verbose_name=_("Сообщение"), on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey(User, verbose_name=_("Пользователь"), on_delete=models.CASCADE, blank=True, null=True)
    doctor = models.ForeignKey(Doctor, verbose_name=_("Доктор"), on_delete=models.CASCADE, null=True, blank=True)
    center = models.ForeignKey(Center, verbose_name=_("Центр"), on_delete=models.CASCADE, null=True, blank=True)
    chat = models.ForeignKey(Chat, verbose_name=_("Чат"), on_delete=models.CASCADE)
    
