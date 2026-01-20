from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random

# -------------------- CustomUser --------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('news_editor', 'Yangiliklar muharriri'),
        ('hr', 'Kadrlar bo‘limi'),
        ('statistician', 'Statistik'),
        ('lost_item_support', 'Murojatlar bo‘limi'),
        ('simple', 'Simple User'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
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
    LANG_CHOICES = (('uz', 'Uz'), ('ru', 'Ru'), ('en', 'En'))
    language = models.CharField(max_length=2, choices=LANG_CHOICES, default='uz',null=True, blank=True)
    
    title = models.CharField("Sarlavha", max_length=255,null=True, blank=True)
    description = models.TextField("Qisqa tavsif",null=True, blank=True)
    fullContent = models.TextField("To‘liq matn",null=True, blank=True)
    category = models.CharField("Kategoriya", max_length=100,null=True, blank=True)
    
    publishedAt = models.DateTimeField(default=timezone.now)
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"[{self.language}] {self.title}"
    
    

class NewsImage(models.Model):
    news = models.ForeignKey(
        News,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name="Yangilik / Новость / News"
    )
    image = models.ImageField("Rasm / Фото / Image", upload_to='news_images/', null=True, blank=True)

class NewsLike(models.Model):
    news = models.ForeignKey(
        News,
        related_name='likes',
        on_delete=models.CASCADE
    )
    session_key = models.CharField(
        max_length=40,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('news', 'session_key')
        verbose_name = "News Like"
        verbose_name_plural = "News Likes"


class NewsView(models.Model):
    news = models.ForeignKey(
        News,
        related_name='views',
        on_delete=models.CASCADE
    )
    session_key = models.CharField(max_length=40, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('news', 'session_key')
        verbose_name = "News View"
        verbose_name_plural = "News Views"


# -------------------- Comment --------------------
class Comment(models.Model):
    news = models.ForeignKey(
        News,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name="Yangilik / Новость / News"
    )
    author = models.CharField("Muallif", max_length=100, blank=True, null=True)

    content= models.TextField("Izoh", blank=True, null=True)

    timestamp = models.DateTimeField(
        "Yaratilgan vaqt",
        default=timezone.now
    )

class JobVacancy(models.Model):
    LANG_CHOICES = (('uz', 'Uz'), ('ru', 'Ru'), ('en', 'En'))
    language = models.CharField(max_length=2, choices=LANG_CHOICES, default='uz',null=True, blank=True)

    title = models.CharField("Nom", max_length=255,null=True, blank=True)
    requirements = models.TextField("Talablar",null=True, blank=True)
    mutaxasislik = models.TextField("Mutaxasislik",null=True, blank=True)
    
    EDUCATION_CHOICES = [('oliy', 'Oliy/Высшее'), ('o-rta', "O'rta/Среднее"), ('o-rta-mahsus', "O'rta mahsus")]
    education_status = models.CharField(max_length=20, choices=EDUCATION_CHOICES,null=True, blank=True)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # Qo‘lda kiritiladiganlar
    answered_requests = models.PositiveIntegerField(default=0, verbose_name="Qabul qilinganlar")
    rejected_requests = models.PositiveIntegerField(default=0, verbose_name="Rad etilganlar")
    pending_requests = models.PositiveIntegerField(default=0, verbose_name="Ko‘rib chiqilayotganlar")

    def __str__(self):
        return self.title or "No title"


class JobVacancyRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', "Ko'rilmoqda"),     
        ('answered', "Javob berilgan"), 
        ('rejected', "Rad etilgan"),     
    ]

    jobVacancy = models.ForeignKey(
        JobVacancy,
        related_name='requests',
        on_delete=models.CASCADE,
        verbose_name="Vakansiya"
    )
    name = models.CharField("Ism (uz)", max_length=100, blank=True, null=True)
    phone = models.CharField("Telefon", max_length=20, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)
    file = models.FileField("Fayl", upload_to='jobVacancyRequests/', null=True, blank=True)
    status = models.CharField(
        "Holat",
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField("Qo‘shilgan vaqt", auto_now_add=True)

    def __str__(self):
        return f"{self.name } - {self.jobVacancy}"



# -------------------- StatisticData --------------------
class StatisticData(models.Model):
    # Tarjima lug‘atlar
    STATION_TRANSLATIONS = {
        'Beruniy': {'uz': 'Beruniy', 'ru': 'Беруни', 'en': 'Beruniy'},
        'Tinchlik': {'uz': 'Tinchlik', 'ru': 'Тинчлик', 'en': 'Tinchlik'},
        'Chorsu': {'uz': 'Chorsu', 'ru': 'Чорсу', 'en': 'Chorsu'},
        'Gʻafur Gʻulom': {'uz': 'Gʻafur Gʻulom', 'ru': 'Ғафур Ғулом', 'en': "G'afur G'ulom"},
        'Alisher Navoiy': {'uz': 'Alisher Navoiy', 'ru': 'Алишер Навоий', 'en': 'Alisher Navoiy'},
        'Abdulla Qodiriy': {'uz': 'Abdulla Qodiriy', 'ru': 'Абдулла Қодирий', 'en': 'Abdulla Qodiriy'},
        'Pushkin': {'uz': 'Pushkin', 'ru': 'Пушкин', 'en': 'Pushkin'},
        'Buyuk Ipak Yoʻli': {'uz': 'Buyuk Ipak Yoʻli', 'ru': 'Буюк Ипак Йўли', 'en': 'Buyuk Ipak Yoʻli'},
        'Novza': {'uz': 'Novza', 'ru': 'Новза', 'en': 'Novza'},
        'Milliy bogʻ': {'uz': 'Milliy bogʻ', 'ru': 'Миллий боғ', 'en': 'Milliy bogʻ'},
        'Xalqlar doʻstligi': {'uz': 'Xalqlar doʻstligi', 'ru': 'Халқлар дўстлиги', 'en': "Xalqlar doʻstligi"},
        'Chilonzor': {'uz': 'Chilonzor', 'ru': 'Чилонзор', 'en': 'Chilonzor'},
        'Mirzo Ulugʻbek': {'uz': 'Mirzo Ulugʻbek', 'ru': 'Мирзо Улуғбек', 'en': 'Mirzo Ulugʻbek'},
        'Olmazor': {'uz': 'Olmazor', 'ru': 'Олмазор', 'en': 'Olmazor'},
        'Doʻstlik': {'uz': 'Doʻstlik', 'ru': 'Дўстлик', 'en': "Doʻstlik"},
        'Mashinasozlar': {'uz': 'Mashinasozlar', 'ru': 'Машинасозлар', 'en': 'Mashinasozlar'},
        'Toshkent': {'uz': 'Toshkent', 'ru': 'Тошкент', 'en': 'Toshkent'},
        'Oybek': {'uz': 'Oybek', 'ru': 'Ойбек', 'en': 'Oybek'},
        'Kosmonavtlar': {'uz': 'Kosmonavtlar', 'ru': 'Космонавтлар', 'en': 'Kosmonavtlar'},
        'Oʻzbekiston': {'uz': 'Oʻzbekiston', 'ru': 'Ўзбекистон', 'en': "Oʻzbekiston"},
        'Hamid Olimjon': {'uz': 'Hamid Olimjon', 'ru': 'Ҳамид Олимжон', 'en': 'Hamid Olimjon'},
        'Mingoʻrik': {'uz': 'Mingoʻrik', 'ru': 'Мингўрик', 'en': 'Mingoʻrik'},
        'Yunus Rajabiy': {'uz': 'Yunus Rajabiy', 'ru': 'Юнус Раджабий', 'en': 'Yunus Rajabiy'},
        'Shahriston': {'uz': 'Shahriston', 'ru': 'Шахристон', 'en': 'Shahriston'},
        'Bodomzor': {'uz': 'Bodomzor', 'ru': 'Бодомзор', 'en': 'Bodomzor'},
        'Minor': {'uz': 'Minor', 'ru': 'Минор', 'en': 'Minor'},
        'Turkiston': {'uz': 'Turkiston', 'ru': 'Туркистон', 'en': 'Turkiston'},
        'Yunusobod': {'uz': 'Yunusobod', 'ru': 'Юнусобод', 'en': 'Yunusobod'},
        'Tuzel': {'uz': 'Tuzel', 'ru': 'Тузел', 'en': 'Tuzel'},
        'Yashnobod': {'uz': 'Yashnobod', 'ru': 'Яшнобод', 'en': 'Yashnobod'},
        'Texnopark': {'uz': 'Texnopark', 'ru': 'Технопарк', 'en': 'Texnopark'},
        'Sergeli': {'uz': 'Sergeli', 'ru': 'Сергели', 'en': 'Sergeli'},
        'Choshtepa': {'uz': 'Choshtepa', 'ru': 'Чоштепа', 'en': 'Choshtepa'},
        'Turon': {'uz': 'Turon', 'ru': 'Турон', 'en': 'Turon'},
        'Chinor': {'uz': 'Chinor', 'ru': 'Чинор', 'en': 'Chinor'},
        'Yangiobod': {'uz': 'Yangiobod', 'ru': 'Янгиобод', 'en': 'Yangiobod'},
        'Rohat': {'uz': 'Rohat', 'ru': 'Роҳат', 'en': 'Rohat'},
        'Oʻzgarish': {'uz': 'Oʻzgarish', 'ru': 'Ўзгариш', 'en': 'Oʻzgarish'},
        'Yangihayot': {'uz': 'Yangihayot', 'ru': 'Янгихаёт', 'en': 'Yangihayot'},
        'Qoʻyliq': {'uz': 'Qoʻyliq', 'ru': 'Қўйлиқ', 'en': 'Qoʻyliq'},
        'Matonat': {'uz': 'Matonat', 'ru': 'Матонат', 'en': 'Matonat'},
        'Qiyot': {'uz': 'Qiyot', 'ru': 'Қиёt', 'en': 'Qiyot'},
        'Tolariq': {'uz': 'Tolariq', 'ru': 'Толарик', 'en': 'Tolariq'},
        'Xonobod': {'uz': 'Xonobod', 'ru': 'Хонобод', 'en': 'Xonobod'},
        'Quruvchilar': {'uz': 'Quruvchilar', 'ru': 'Қурувчилар', 'en': 'Quruvchilar'},
        'Olmos': {'uz': 'Olmos', 'ru': 'Олмос', 'en': 'Olmos'},
        'Paxtakor': {'uz': 'Paxtakor', 'ru': 'Пахтакор', 'en': 'Paxtakor'},
        'Qipchoq': {'uz': 'Qipchoq', 'ru': 'Қипчоқ', 'en': 'Qipchoq'},
        'Amir Temur xiyoboni': {'uz': 'Amir Temur xiyoboni', 'ru': 'Амир Темур хиёбони', 'en': 'Amir Temur xiyoboni'},
        'Mustaqillik maydoni': {'uz': 'Mustaqillik maydoni', 'ru': 'Мустақиллик майдони', 'en': 'Mustaqillik maydoni'},
    }
    Year_TRANSLATIONS = {
        '2025': {'uz': '2025', 'ru': '2025', 'en': '2025'},
        '2026': {'uz': '2026', 'ru': '2026', 'en': '2026'},
        '2027': {'uz': '2027', 'ru': '2027', 'en': '2027'},
        '2028': {'uz': '2028', 'ru': '2028', 'en': '2028'},
        '2029': {'uz': '2029', 'ru': '2029', 'en': '2029'},
        '2030': {'uz': '2030', 'ru': '2030', 'en': '2030'},
    }

    # Oylik tarjimalar (dict format)
    MONTH_TRANSLATIONS = {
        'Yanvar': {'uz': 'Yanvar', 'ru': 'Январь', 'en': 'January'},
        'Fevral': {'uz': 'Fevral', 'ru': 'Февраль', 'en': 'February'},
        'Mart': {'uz': 'Mart', 'ru': 'Март', 'en': 'March'},
        'Aprel': {'uz': 'Aprel', 'ru': 'Апрель', 'en': 'April'},
        'May': {'uz': 'May', 'ru': 'Май', 'en': 'May'},
        'Iyun': {'uz': 'Iyun', 'ru': 'Июнь', 'en': 'June'},
        'Iyul': {'uz': 'Iyul', 'ru': 'Июль', 'en': 'July'},
        'Avgust': {'uz': 'Avgust', 'ru': 'Август', 'en': 'August'},
        'Sentyabr': {'uz': 'Sentyabr', 'ru': 'Сентябрь', 'en': 'September'},
        'Oktyabr': {'uz': 'Oktyabr', 'ru': 'Октябрь', 'en': 'October'},
        'Noyabr': {'uz': 'Noyabr', 'ru': 'Ноябрь', 'en': 'November'},
        'Dekabr': {'uz': 'Dekabr', 'ru': 'Декабрь', 'en': 'December'},
    }

    STATION_CHOICES = [(key, value['uz']) for key, value in STATION_TRANSLATIONS.items()]
    MONTH_CHOICES = [(key, value['uz']) for key, value in MONTH_TRANSLATIONS.items()]
    YEAR_CHOICES = [(key, value['uz']) for key, value in Year_TRANSLATIONS.items()]

    station_name = models.CharField("Bekat / Станция / Station", max_length=100, choices=STATION_CHOICES)
    year = models.CharField("Yil / Год / Year", max_length=20, choices=YEAR_CHOICES, default='2025')
    month = models.CharField("Oy / Месяц / Month", max_length=20, choices=MONTH_CHOICES, default='Yanvar')
    user_count = models.PositiveIntegerField("Foydalanuvchilar soni / Кол-во пользователей / Users Count", default=0)
    created_at = models.DateTimeField("Qo‘shilgan vaqt / Дата добавления / Created At", auto_now_add=True)

    def __str__(self):
        return f"{self.get_station_name_display()} ({self.get_year_display()}) - ({self.get_month_display()}) - {self.user_count} ta odam"

    def get_station_translation(self, lang):
        translations = self.STATION_TRANSLATIONS.get(self.station_name)
        if not translations:
            return self.station_name 
        return translations.get(lang, self.station_name)

    def get_year_translation(self, lang):
        translations = self.Year_TRANSLATIONS.get(self.year)
        if not translations:
            return self.year
        return translations.get(lang, self.year)

    def get_month_translation(self, lang):
        translations = self.MONTH_TRANSLATIONS.get(self.month)
        if not translations:
            return self.month
        return translations.get(lang, self.month)



# -------------------- LostItemRequest --------------------
class LostItemRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Javob berilmagan'),
        ('answered', 'Javob berilgan'),
    ]
    name = models.CharField("Ism", max_length=100)

    phone = models.CharField("Telefon", max_length=20, )
    email = models.EmailField("Email", )

    address = models.CharField("Manzil", max_length=255, )
    passport = models.CharField("Passport", max_length=9, )

    message = models.TextField("Xabar", )
    created_at = models.DateTimeField("Qo‘shilgan vaqt", auto_now_add=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"Yo‘qolgan buyum: {self.name}"


# -------------------- FoydalanuvchiStatistika --------------------
class FoydalanuvchiStatistika(models.Model):
    jami_kirishlar = models.PositiveIntegerField(default=0)
    oxirgi_faollik = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Jami kirishlar: {self.jami_kirishlar}"

    @staticmethod
    def get_onlayn_foydalanuvchilar():
        # 5 soniya ichida faol bo‘lgan sessiyalar
        vaqt_chegarasi = timezone.now() - timedelta(minutes=1)
        return SessiyaIzlovi.objects.filter(oxirgi_harakat__gte=vaqt_chegarasi).count()


class SessiyaIzlovi(models.Model):
    sessiya_id = models.CharField(max_length=100, unique=True)
    oxirgi_harakat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sessiya: {self.sessiya_id} ({self.oxirgi_harakat})"
 





class Announcement(models.Model):
    LANG_CHOICES = (
        ('uz', 'Uzbek'),
        ('ru', 'Russian'),
        ('en', 'English'),
    )

    lang = models.CharField(
        max_length=2,
        choices=LANG_CHOICES,
        default='uz',
        db_index=True
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)
    views_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)




class AnnouncementImage(models.Model):
    announcement = models.ForeignKey(
        Announcement,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='announcements/', verbose_name="Rasm")
    
    
class AnnouncementComment(models.Model):
    announcement = models.ForeignKey(
        Announcement,
        related_name='comments',
        on_delete=models.CASCADE
    )
    author = models.CharField("Muallif", max_length=100, blank=True, null=True)
    content = models.TextField("Izoh", blank=True, null=True)
    timestamp = models.DateTimeField(
        "Yaratilgan vaqt",
        default=timezone.now
    )


class AnnouncementLike(models.Model):
    announcement = models.ForeignKey(
        Announcement, 
        related_name='likes', 
        on_delete=models.CASCADE
    )
    session_key = models.CharField(
        max_length=40, 
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('announcement', 'session_key')
        verbose_name = "E’lon like"
        verbose_name_plural = "E’lon like-lar"



class AnnouncementView(models.Model):
    announcement = models.ForeignKey(
        Announcement,
        related_name='views',
        on_delete=models.CASCADE
    )
    session_key = models.CharField(max_length=40, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('announcement', 'session_key')


class Korrupsiya(models.Model):
    LANG_CHOICES = (('uz', 'Uz'), ('ru', 'Ru'), ('en', 'En'))
    language = models.CharField(max_length=2, choices=LANG_CHOICES, default='uz',null=True, blank=True)
    
    title = models.CharField("Sarlavha", max_length=255,null=True, blank=True)
    description = models.TextField("Qisqa tavsif",null=True, blank=True)
    fullContent = models.TextField("To‘liq matn",null=True, blank=True)
    category = models.CharField("Kategoriya", max_length=100,null=True, blank=True)
    
    publishedAt = models.DateTimeField(default=timezone.now)
    like_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"[{self.language}] {self.title}"
    
class KorrupsiyaImage(models.Model):
    korrupsiya = models.ForeignKey(
        Korrupsiya,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name="Korrupsiya yangiliklari"
    )
    image = models.ImageField("Rasm", upload_to='korrupsiya_images/', null=True, blank=True)
    
class KorrupsiyaLike(models.Model):
    korrupsiya = models.ForeignKey(
        Korrupsiya,
        related_name='likes',
        on_delete=models.CASCADE
    )
    session_key = models.CharField(
        max_length=40,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('korrupsiya', 'session_key')
        verbose_name = "Korrupsiya Like"
        verbose_name_plural = "Korrupsiya Likes"
        
class KorrupsiyaComment(models.Model):
    korrupsiya = models.ForeignKey(
        Korrupsiya,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name="Korrupsiya yangiliklari"
    )
    author = models.CharField("Muallif", max_length=100, blank=True, null=True)

    content= models.TextField("Izoh", blank=True, null=True)

    timestamp = models.DateTimeField(
        "Yaratilgan vaqt",
        default=timezone.now
    )
    
class KorrupsiyaView(models.Model):
    korrupsiya = models.ForeignKey(
        Korrupsiya,
        related_name='views',
        on_delete=models.CASCADE
    )
    session_key = models.CharField(max_length=40)

    class Meta:
        unique_together = ('korrupsiya', 'session_key')

    
    



class SimpleUser(models.Model):
    first_name = models.CharField("Ism", max_length=50)
    last_name = models.CharField("Familiya", max_length=50)
    phone = models.CharField("Telefon", max_length=20, unique=True)
    is_verified = models.BooleanField(default=False)  # SMS tasdiqlangan bo‘lsa True
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"

# -------------------- Telefon tasdiqlash kodi --------------------
class PhoneVerification(models.Model):
    user = models.ForeignKey(SimpleUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    @staticmethod
    def generate_code():
        return f"{random.randint(100000, 999999)}"
    





class MediaPhoto(models.Model):
    LANG_CHOICES = (('uz', 'Uz'), ('ru', 'Ru'), ('en', 'En'))
    language = models.CharField(max_length=2, choices=LANG_CHOICES, default='uz')
    group_id = models.PositiveIntegerField(verbose_name="Guruh ID (Bir xil rasm uchun)")
    
    image = models.ImageField(upload_to="mediateka/photos/")
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    category = models.CharField(max_length=100, verbose_name="Kategoriya")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "group_id"]
        verbose_name = "Media Foto"
        verbose_name_plural = "Media Fotolar"

    def __str__(self):
        return f"[{self.language}] {self.title}"


class MediaVideo(models.Model):
    LANG_CHOICES = (('uz', 'Uz'), ('ru', 'Ru'), ('en', 'En'))
    language = models.CharField(max_length=2, choices=LANG_CHOICES, default='uz')
    group_id = models.PositiveIntegerField(verbose_name="Guruh ID (Bir xil video uchun)")
    
    video_url = models.URLField(help_text="YouTube embed URL")
    thumbnail = models.ImageField(upload_to="mediateka/videos/thumbnails/")
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    duration = models.CharField(max_length=20, help_text="Masalan: 15:42")
    views = models.CharField(max_length=20, default="0")
    category = models.CharField(max_length=100, verbose_name="Kategoriya")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "group_id"]
        verbose_name = "Media Video"
        verbose_name_plural = "Media Videolar"

    def __str__(self):
        return f"[{self.language}] {self.title}"
   
    


# models.py
class FrontendImage(models.Model):
    section = models.CharField(
        max_length=100,
        help_text="Bo‘lim nomi (masalan: main_page, navbar, footer)"
    )
    image = models.ImageField(upload_to="frontend_images/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["section", "order"]

    def __str__(self):
        return f"{self.section}"
  
   
class StationFront(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Bekat nomi")
    
    # Rasmlar (Admin paneldan fayl sifatida yuklanadi)
    image1 = models.ImageField(upload_to='stations/', verbose_name="Rasm 1")
    image2 = models.ImageField(upload_to='stations/', verbose_name="Rasm 2", blank=True, null=True)
    
    # Video ma'lumotlari
    video_title = models.CharField(max_length=255, verbose_name="Video sarlavhasi")
    video_url = models.URLField(verbose_name="Video Linki (Embed)")
    video_thumbnail = models.ImageField(  # <-- URLField o‘rniga ImageField
        upload_to='stations/video_thumbnails/', 
        verbose_name="Video muqovasi (Fayl)",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Bekat ma'lumoti"
        verbose_name_plural = "Bekat ma'lumotlari"
        
        
        
        
class Management(models.Model):
    LANG_CHOICES = (('uz', 'Uz'), ('ru', 'Ru'), ('en', 'En'))
    language = models.CharField(max_length=2, choices=LANG_CHOICES, default='uz', verbose_name="Til")
    
    # Har xil tillardagi bir xil odamni bog'lash uchun (masalan, 3 ta tilda ham bir xil raqam qo'yiladi)
    group_id = models.PositiveIntegerField(verbose_name="Guruh ID (Bir xil rahbarlar uchun bir xil raqam)")
    
    firstName = models.CharField(max_length=255, verbose_name="Ism")
    middleName = models.CharField(max_length=255, verbose_name="Sharif")
    lastName = models.CharField(max_length=255, verbose_name="Familiya")
    position = models.CharField(max_length=255, verbose_name="Lavozim")
    
    department = models.CharField(max_length=255, verbose_name="Bo'lim")
    phone = models.CharField(max_length=100, verbose_name="Telefon")
    email = models.CharField(max_length=255, verbose_name="Email")
    hours = models.CharField(max_length=255, verbose_name="Qabul vaqti")
    biography = models.TextField(verbose_name="Biografiya")
    
    image = models.ImageField(upload_to='management/', verbose_name="Rasm")
    order = models.IntegerField(default=0, verbose_name="Tartib raqami")

    class Meta:
        ordering = ['order', 'group_id']
        verbose_name = "Rahbar"
        verbose_name_plural = "Rahbarlar"

    def __str__(self):
        return f"[{self.language}] {self.firstName} {self.lastName}"
    
    
class Department(models.Model):
    LANG_CHOICES = (('uz', 'Uz'), ('ru', 'Ru'), ('en', 'En'))
    language = models.CharField(max_length=2, choices=LANG_CHOICES, default='uz', verbose_name="Til")
    
    # Bir xil bo'limlarni tillar kesimida bog'lash uchun
    group_id = models.PositiveIntegerField(verbose_name="Guruh ID")
    
    title = models.CharField(max_length=255, verbose_name="Bo'lim nomi")
    head = models.CharField(max_length=255, verbose_name="Rahbar")
    schedule = models.CharField(max_length=255, verbose_name="Ish tartibi")
    reception = models.CharField(max_length=255, verbose_name="Qabul vaqti")
    
    phone = models.CharField(max_length=100, verbose_name="Telefon")
    email = models.EmailField(verbose_name="Email")
    image = models.ImageField(upload_to='departments/', verbose_name="Rasm")
    order = models.IntegerField(default=0, verbose_name="Tartib raqami")

    class Meta:
        ordering = ['order', 'group_id']
        verbose_name = "Bo'lim"
        verbose_name_plural = "Bo'limlar"

    def __str__(self):
        return f"[{self.language}] {self.title}"