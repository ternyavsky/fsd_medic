from time import sleep
from celery import shared_task
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from auth_doctor.models import Doctor, Interview
from auth_user.service import start_time_reminder
from fsd_medic.settings import SOCKET_IO
from social.models import Chat, Message, Notification
from celery.signals import after_task_publish
from api.models import News, User, Note
from .serializers import NotificationSerializer
import datetime


@shared_task
def notify_make(user):
    notif = Notification.objects.create(
        user_id=user, text="Напоминание о записи завтра в"
    )
    notif.save()


@receiver(post_save, sender=Note)
def create_notify(sender, instance: Note, **kwargs):
    note_date = instance.time_start.date()
    notify_make.apply_async(
        args=[instance.user.id], eta=(instance.time_start - datetime.timedelta(days=1))
    )

    # Notification.objects.create(user=instance.user, text="well")


@receiver(post_save, sender=Notification)
def send_notify(sender, instance: Notification, **kwargs):
    SOCKET_IO.emit("newNotify", NotificationSerializer(instance).data)


@receiver(pre_save, sender=News)
def notify_center(sender, instance, **kwargs):
    if instance.clinic:
        users = User.objects.filter(clinic=instance.clinic)
        for i in range(len(users)):
            notification = Notification.objects.create(
                user=users[i], text=f"Вышел новый пост у клиники{instance.clinic.name}"
            )


# @receiver(post_save, sender=Note)
# def notify_note(sender, instance, created, **kwargs):
#     if not created:
#         notify = None
#         if instance.special_check:
#             notify = Notification.objects.create(
#                 user=instance.user,
#                 text="Созданная запись прошла дополнительную проверку",
#             )
#         if instance.status == "Rejected":
#             notify = Notification.objects.create(
#                 user=instance.user, text="Запись была отклонена вашим центром"
#             )
#         elif instance.status == "Passed":
#             notify = Notification.objects.create(
#                 user=instance.user, text="Запись была подтверждена вашим центром"
#             )
#         notify.save()
#         server.emit(
#             "notification", {"notification": NotificationSerializer(notify).data}
#         )


# @receiver(post_save, sender=User)
# def notify_verify(sender, instance, created, **kwargs):
#     if not created:
#         if instance.verification_code != 1 and instance.number_verification_code != 1:
#             notify = Notification.objects.create(
#                 user=instance,
#                 text="Ваш аккаунт был успешно защищен эл.почтой или телефоном",
#             )
#             notify.save()
#             server.emit(
#                 "notification", {"notification": NotificationSerializer(notify).data}
#             )


@receiver(post_delete, sender=Message, dispatch_uid="messages_deleted")
def message_post_delete_handler(sender, **kwargs):
    cache.delete("messages")


@receiver(post_save, sender=Message, dispatch_uid="messages_updated")
def message_post_save_handler(sender, **kwargs):
    cache.delete("messages")


@receiver(post_delete, sender=Chat, dispatch_uid="chats_deleted")
def chat_post_delete_handler(sender, **kwargs):
    cache.delete("chats")


@receiver(post_save, sender=Chat, dispatch_uid="chats_deleted")
def chat_post_save_handler(sender, **kwargs):
    cache.delete("chats")
