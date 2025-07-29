from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import FoydalanuvchiStatistika

@receiver(user_logged_in)
def count_user_login(sender, request, user, **kwargs):
    stat, created = FoydalanuvchiStatistika.objects.get_or_create(id=1)
    stat.jami_kirishlar += 1
    stat.save()