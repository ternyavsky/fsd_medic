from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from auth_doctor.models import Doctor, Interview
from auth_user.service import start_time_reminder
from social.models import Chat, Message, Notification
from .models import Center, Clinic, Disease, Like, News, Note, User, Saved, City, Country


# CACHE SIGNALS

@receiver(post_delete, sender=Country, dispatch_uid="countries_deleted")
def country_post_delete_handler(sender, **kwargs):
    cache.delete('countries')


@receiver(post_save, sender=Country, dispatch_uid='countries_updated')
def country_post_save_handler(sender, **kwargs):
    cache.delete('countries')


@receiver(post_delete, sender=City, dispatch_uid="cities_deleted")
def city_post_delete_handler(sender, **kwargs):
    cache.delete('cities')


@receiver(post_save, sender=City, dispatch_uid='cities_updated')
def city_post_save_handler(sender, **kwargs):
    cache.delete('cities')


@receiver(post_delete, sender=Message, dispatch_uid="messages_deleted")
def message_post_delete_handler(sender, **kwargs):
    cache.delete('messages')


@receiver(post_save, sender=Message, dispatch_uid='messagess_updated')
def message_post_save_handler(sender, **kwargs):
    cache.delete('messages')


@receiver(post_delete, sender=Chat, dispatch_uid="chats_deleted")
def chat_post_delete_handler(sender, **kwargs):
    cache.delete('chats')


@receiver(post_save, sender=Chat, dispatch_uid='chats_deleted')
def chat_post_save_handler(sender, **kwargs):
    cache.delete('chats')


@receiver(post_delete, sender=Disease, dispatch_uid="diseases_deleted")
def disease_post_delete_handler(sender, **kwargs):
    cache.delete('diseases')


@receiver(post_save, sender=Disease, dispatch_uid='diseases_updated')
def disease_post_save_handler(sender, **kwargs):
    cache.delete('diseases')


@receiver(post_delete, sender=Saved, dispatch_uid="saved_deleted")
def saved_post_delete_handler(sender, **kwargs):
    cache.delete('saved')


@receiver(post_save, sender=Saved, dispatch_uid='saved_updated')
def saved_post_save_handler(sender, **kwargs):
    cache.delete('saved')


@receiver(post_delete, sender=Like, dispatch_uid="likes_deleted")
def like_post_delete_handler(sender, **kwargs):
    cache.delete('likes')


@receiver(post_save, sender=Like, dispatch_uid='likes_updated')
def like_post_save_handler(sender, **kwargs):
    cache.delete('likes')


@receiver(post_delete, sender=News, dispatch_uid="news_deleted")
def news_post_delete_handler(sender, **kwargs):
    cache.delete('news')


@receiver(post_save, sender=News, dispatch_uid='news_updated')
def news_post_save_handler(sender, **kwargs):
    cache.delete('news')


@receiver(post_delete, sender=Interview, dispatch_uid="interviews_deleted")
def interview_post_delete_handler(sender, **kwargs):
    cache.delete('interview')


@receiver(post_save, sender=Interview, dispatch_uid='interviews_updated')
def interview_post_save_handler(sender, **kwargs):
    cache.delete('interview')


@receiver(post_delete, sender=Note, dispatch_uid="notes_deleted")
def note_post_delete_handler(sender, **kwargs):
    cache.delete('notes')


@receiver(post_save, sender=Note, dispatch_uid='notes_updated')
def note_post_save_handler(sender, **kwargs):
    cache.delete('notes')


@receiver(post_delete, sender=Center, dispatch_uid="centers_deleted")
def center_post_delete_handler(sender, **kwargs):
    cache.delete('centers')


@receiver(post_save, sender=Center, dispatch_uid='centers_updated')
def center_post_save_handler(sender, **kwargs):
    cache.delete('centers')


@receiver(post_delete, sender=User, dispatch_uid="users_deleted")
def user_post_delete_handler(sender, **kwargs):
    cache.delete('users')


@receiver(post_save, sender=User, dispatch_uid='users_updated')
def user_post_save_handler(sender, **kwargs):
    cache.delete('users')


@receiver(post_delete, sender=Doctor, dispatch_uid="doctors_deleted")
def doctor_post_delete_handler(sender, **kwargs):
    cache.delete('doctors')


@receiver(post_save, sender=Doctor, dispatch_uid='doctors_updated')
def doctor_post_save_handler(sender, **kwargs):
    cache.delete('doctors')


@receiver(post_delete, sender=Clinic, dispatch_uid="clinics_deleted")
def clinic_post_delete_handler(sender, **kwargs):
    cache.delete('clinics')


@receiver(post_save, sender=Clinic, dispatch_uid='clinics_updated')
def clinic_post_save_handler(sender, **kwargs):
    cache.delete('clinics')

@receiver(post_delete, sender=Notification, dispatch_uid="notify_deleted")
def notification_post_delete_handler(sender, **kwargs):
    cache.delete('notifications')


@receiver(post_save, sender=Clinic, dispatch_uid='notify_updated')
def clinic_post_save_handler(sender, **kwargs):
    cache.delete('notifications')


# NOTIFY SIGNALS

# Center post signal
@receiver(pre_save, sender=News)
def notify_center(sender, instance, **kwargs):
    users = User.objects.filter(main_center=instance.center)
    users2 = User.objects.filter(centers=instance.center)
    data = users.union(users2)
    for i in range(len(data)):
        Notification.objects.create(
            user=data[i], text=f"Вышел новый пост у мед.центра {instance.center.name}")

    # Change status Note signal


@receiver(post_save, sender=Note)
def notify_note(sender, instance, created, **kwargs):
    if not created:
        if instance.special_check == True:
            Notification.objects.create(
                user=instance.user, text="Созданная запись прошла дополнительную проверку")
        if instance.status == "Rejected":
            Notification.objects.create(
                user=instance.user, text="Запись была отклонена вашим центром")
        elif instance.status == "Passed":
            Notification.objects.create(
                user=instance.user, text="Запись была подтверждена вашим центром")


@receiver(post_save, sender=User)
def notify_verify(sender, instance, created, **kwargs):
    if not created:
        if instance.verification_code != 0 and instance.email_verification_code != 0:
            Notification.objects.create(
                user=instance, text="Ваш аккаунт был успешно защищен эл.почтой или телефоном")

# SEND REMINDER FOR NOTE

@receiver(post_save, sender=Note)
def notify_time(sender, instance, created, **kwargs):
    if created:
        start_time_reminder.s(instance.user.id, instance.notify).apply_async(
            eta=instance.notify)
