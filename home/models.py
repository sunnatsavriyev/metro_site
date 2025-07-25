from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('news_editor', 'Yangiliklar muharriri'),
        ('hr', 'Kadrlar bo‘limi'),
        ('statistician', 'Statistik'),
        ('lost_item_support', 'Murojatlar bo‘limi'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.username

    @property
    def is_news_editor(self):
        return self.role == 'news_editor'

    @property
    def is_hr(self):
        return self.role == 'hr'

    @property
    def is_statistician(self):
        return self.role == 'statistician'

    @property
    def is_lost_item_support(self):
        return self.role == 'lost_item_support'


class News(models.Model):
    title_uz = models.CharField("Sarlavha (uz)", max_length=255)
    title_ru = models.CharField("Sarlavha (ru)", max_length=255)
    description_uz = models.TextField("Qisqa tavsif (uz)")
    description_ru = models.TextField("Qisqa tavsif (ru)")
    fullContent_uz = models.TextField("To‘liq matn (uz)")
    fullContent_ru = models.TextField("To‘liq matn (ru)")
    publishedAt = models.DateTimeField("E’lon qilingan vaqt", default=timezone.now)
    likes = models.ManyToManyField(CustomUser, related_name='liked_news', blank=True, verbose_name="Layklar")
    category_uz = models.CharField("Kategoriya (uz)", max_length=100)
    category_ru = models.CharField("Kategoriya (ru)", max_length=100)

    def __str__(self):
        return self.title_uz

    def like_count(self):
        return self.likes.count()


class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='images', on_delete=models.CASCADE, verbose_name="Yangilik")
    image = models.ImageField("Rasm", upload_to='news_images/', null=True, blank=True)


class Comment(models.Model):
    news = models.ForeignKey(News, related_name='comments', on_delete=models.CASCADE, verbose_name="Yangilik")
    author_uz = models.CharField("Muallif (uz)", max_length=100)
    author_ru = models.CharField("Muallif (ru)", max_length=100)
    content_uz = models.TextField("Izoh (uz)")
    content_ru = models.TextField("Izoh (ru)")
    timestamp = models.DateTimeField("Yaratilgan vaqt", default=timezone.now)


class JobVacancy(models.Model):
    title_uz = models.CharField("Nom (uz)", max_length=255)
    title_ru = models.CharField("Nom (ru)", max_length=255)
    requirements_uz = models.TextField("Talablar (uz)")
    requirements_ru = models.TextField("Talablar (ru)")
    benefits_uz = models.TextField("Imtiyozlar (uz)")
    benefits_ru = models.TextField("Imtiyozlar (ru)")
    ageRange = models.CharField("Yosh oralig‘i", max_length=50)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Kim tomonidan yaratilgan")

    def __str__(self):
        return self.title_uz


class StatisticData(models.Model):
    STATION_CHOICES = [
        # Bekatlar nomlari
        ('Beruniy', 'Beruniy'),
        ('Tinchlik', 'Tinchlik'),
        ('Chorsu', 'Chorsu'),
        ('Gʻafur Gʻulom', 'Gʻafur Gʻulom'),
        ('Alisher Navoiy', 'Alisher Navoiy'),
        ('Abdulla Qodiriy', 'Abdulla Qodiriy'),
        ('Pushkin', 'Pushkin'),
        ('Buyuk Ipak Yoʻli', 'Buyuk Ipak Yoʻli'),
        ('Novza', 'Novza'),
        ('Milliy bogʻ', 'Milliy bogʻ'),
        ('Xalqlar doʻstligi', 'Xalqlar doʻstligi'),
        ('Chilonzor', 'Chilonzor'),
        ('Mirzo Ulugʻbek', 'Mirzo Ulugʻbek'),
        ('Olmazor', 'Olmazor'),
        ('Doʻstlik', 'Doʻstlik'),
        ('Mashinasozlar', 'Mashinasozlar'),
        ('Toshkent', 'Toshkent'),
        ('Oybek', 'Oybek'),
        ('Kosmonavtlar', 'Kosmonavtlar'),
        ('Oʻzbekiston', 'Oʻzbekiston'),
        ('Hamid Olimjon', 'Hamid Olimjon'),
        ('Ming Oʻrik', 'Ming Oʻrik'),
        ('Yunus Rajabiy', 'Yunus Rajabiy'),
        ('Shahriston', 'Shahriston'),
        ('Bodomzor', 'Bodomzor'),
        ('Minor', 'Minor'),
        ('Turkiston', 'Turkiston'),
        ('Yunusobod', 'Yunusobod'),
        ('Tuzel', 'Tuzel'),
        ('Yashnobod', 'Yashnobod'),
        ('Texnopark', 'Texnopark'),
        ('Doʻstlik-2', 'Doʻstlik-2'),
        ('Sergeli', 'Sergeli'),
        ('Afrosiyob', 'Afrosiyob'),
        ('Choshtepa', 'Choshtepa'),
        ('Turon', 'Turon'),
        ('Chinor', 'Chinor'),
        ('Yangiobod', 'Yangiobod'),
        ('Rohat', 'Rohat'),
        ('Oʻzgarish', 'Oʻzgarish'),
        ('Yangihayot', 'Yangihayot'),
        ('Qoʻyliq', 'Qoʻyliq'),
        ('Matonat', 'Matonat'),
        ('Qiyot', 'Qiyot'),
        ('Tolariq', 'Tolariq'),
        ('Xonobod', 'Xonobod'),
        ('Quruvchilar', 'Quruvchilar'),
        ('Olmos', 'Olmos'),
        ('Amir Temur xiyoboni', 'Amir Temur xiyoboni'),
        ('Mustaqillik maydoni', 'Mustaqillik maydoni'),
    ]

    MONTH_CHOICES = [
        ('Yanvar', 'Yanvar'),
        ('Fevral', 'Fevral'),
        ('Mart', 'Mart'),
        ('Aprel', 'Aprel'),
        ('May', 'May'),
        ('Iyun', 'Iyun'),
        ('Iyul', 'Iyul'),
        ('Avgust', 'Avgust'),
        ('Sentyabr', 'Sentyabr'),
        ('Oktyabr', 'Oktyabr'),
        ('Noyabr', 'Noyabr'),
        ('Dekabr', 'Dekabr'),
    ]

    station_name = models.CharField("Bekat nomi", max_length=100, choices=STATION_CHOICES)
    month = models.CharField("Oy", max_length=20, choices=MONTH_CHOICES, default='Yanvar')
    user_count = models.PositiveIntegerField("Foydalanuvchilar soni", default=0)
    created_at = models.DateTimeField("Qo‘shilgan vaqt", auto_now_add=True)

    def __str__(self):
        return f"{self.station_name} ({self.month}) - {self.user_count} ta odam"


class LostItemRequest(models.Model):
    name_uz = models.CharField("Ism (uz)", max_length=100)
    name_ru = models.CharField("Ism (ru)", max_length=100)
    phone = models.CharField("Telefon raqam", max_length=20)
    email = models.EmailField("Email")
    message_uz = models.TextField("Xabar (uz)")
    message_ru = models.TextField("Xabar (ru)")
    created_at = models.DateTimeField("Qo‘shilgan vaqt", auto_now_add=True)

    def __str__(self):
        return f"Yo‘qolgan buyum: {self.name_uz}"





class FoydalanuvchiStatistika(models.Model):
    jami_kirishlar = models.PositiveIntegerField(default=0, verbose_name="Jami kirishlar soni")
    oxirgi_faollik = models.DateTimeField(auto_now=True, verbose_name="Oxirgi yangilanish vaqti")

    def __str__(self):
        return f"Jami kirishlar: {self.jami_kirishlar}"

    @staticmethod
    def get_onlayn_foydalanuvchilar():
        """So‘nggi 5 daqiqada aktiv bo‘lganlarni onlayn deb hisoblaymiz"""
        vaqt_chegarasi = timezone.now() - timedelta(minutes=5)
        return SessiyaIzlovi.objects.filter(oxirgi_harakat__gte=vaqt_chegarasi).count()


class SessiyaIzlovi(models.Model):
    sessiya_id = models.CharField(max_length=100, unique=True)
    oxirgi_harakat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sessiya: {self.sessiya_id} ({self.oxirgi_harakat})"

