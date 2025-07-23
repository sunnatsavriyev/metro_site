from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('news_editor', 'News Editor'),
        ('hr', 'HR'),
        ('statistician', 'Statistician'),
        ('lost_item_support', 'Lost Item Support'),
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
    title_uz = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)
    description_uz = models.TextField()
    description_ru = models.TextField()
    fullContent_uz = models.TextField()
    fullContent_ru = models.TextField()
    publishedAt = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(CustomUser, related_name='liked_news', blank=True)
    category_uz = models.CharField(max_length=100)
    category_ru = models.CharField(max_length=100)

    def __str__(self):
        return self.title_uz

    def like_count(self):
        return self.likes.count()


class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)


class Comment(models.Model):
    news = models.ForeignKey(News, related_name='comments', on_delete=models.CASCADE)
    author_uz = models.CharField(max_length=100)
    author_ru = models.CharField(max_length=100)
    content_uz = models.TextField()
    content_ru = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)


class JobVacancy(models.Model):
    title_uz = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)
    icon = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    requirements_uz = models.JSONField()
    requirements_ru = models.JSONField()
    benefits_uz = models.JSONField()
    benefits_ru = models.JSONField()
    ageRange = models.CharField(max_length=50) 
    category_uz = models.CharField(max_length=100)
    category_ru = models.CharField(max_length=100)
    salaryRange = models.CharField(max_length=50)  
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title_uz



class StatisticData(models.Model):
    STATION_CHOICES = [
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

    station_name = models.CharField(max_length=100, choices=STATION_CHOICES)
    month = models.CharField(max_length=20, choices=MONTH_CHOICES, default='Yanvar')
    user_count = models.PositiveIntegerField(default=0)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.station_name} ({self.month}) - {self.user_count} ta odam"


class LostItemRequest(models.Model):
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)  
    email = models.EmailField()  
    message_uz = models.TextField()
    message_ru = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lost item report from {self.name_uz}"
