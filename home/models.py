from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


# -------------------- CustomUser --------------------
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



# -------------------- News --------------------
class News(models.Model):
    title_uz = models.CharField("Sarlavha (uz)", max_length=255, blank=True, null=True)
    title_ru = models.CharField("Заголовок (ru)", max_length=255, blank=True, null=True)
    title_en = models.CharField("Title (en)", max_length=255, blank=True, null=True)

    description_uz = models.TextField("Qisqa tavsif (uz)", blank=True, null=True)
    description_ru = models.TextField("Краткое описание (ru)", blank=True, null=True)
    description_en = models.TextField("Short description (en)", blank=True, null=True)

    fullContent_uz = models.TextField("To‘liq matn (uz)", blank=True, null=True)
    fullContent_ru = models.TextField("Полный текст (ru)", blank=True, null=True)
    fullContent_en = models.TextField("Full text (en)", blank=True, null=True)

    publishedAt = models.DateTimeField(
        "E’lon qilingan vaqt / Дата публикации / Published At",
        default=timezone.now
    )

    like_count = models.PositiveIntegerField(default=0, verbose_name="Likes soni")

    category_uz = models.CharField("Kategoriya (uz)", max_length=100, blank=True, null=True)
    category_ru = models.CharField("Категория (ru)", max_length=100, blank=True, null=True)
    category_en = models.CharField("Category (en)", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title_uz or self.title_ru or self.title_en or "No title"



class NewsImage(models.Model):
    news = models.ForeignKey(
        News,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name="Yangilik / Новость / News"
    )
    image = models.ImageField("Rasm / Фото / Image", upload_to='news_images/', null=True, blank=True)


# -------------------- Comment --------------------
class Comment(models.Model):
    news = models.ForeignKey(
        News,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name="Yangilik / Новость / News"
    )
    author_uz = models.CharField("Muallif (uz)", max_length=100, blank=True, null=True)
    author_ru = models.CharField("Автор (ru)", max_length=100, blank=True, null=True)
    author_en = models.CharField("Author (en)", max_length=100, blank=True, null=True)

    content_uz = models.TextField("Izoh (uz)", blank=True, null=True)
    content_ru = models.TextField("Комментарий (ru)", blank=True, null=True)
    content_en = models.TextField("Comment (en)", blank=True, null=True)

    timestamp = models.DateTimeField(
        "Yaratilgan vaqt / Время создания / Created At",
        default=timezone.now
    )

class JobVacancy(models.Model):
    title_uz = models.CharField("Nom (uz)", max_length=255, blank=True, null=True)
    title_ru = models.CharField("Название (ru)", max_length=255, blank=True, null=True)
    title_en = models.CharField("Title (en)", max_length=255, blank=True, null=True)

    requirements_uz = models.TextField("Talablar (uz)", blank=True, null=True)
    requirements_ru = models.TextField("Требования (ru)", blank=True, null=True)
    requirements_en = models.TextField("Requirements (en)", blank=True, null=True)

    mutaxasislik_uz = models.TextField("Mutaxasislik (uz)", blank=True, null=True)
    mutaxasislik_ru = models.TextField("Мутации (ru)", blank=True, null=True)
    mutaxasislik_en = models.TextField("Mutaxasislik (en)", blank=True, null=True)

    CHOOSED_STATUS_UZ = [
        ('oliy', 'Oliy'),
        ("o'rta", "O'rta"),
        ("o'rta mahsus", "O'rta mahsus"),
    ]
    CHOOSED_STATUS_RU = [
        ('oliy', 'Высшее'),
        ("o'rta", "Среднее"),
        ("o'rta mahsus", "Среднее специальное"),
    ]
    CHOOSED_STATUS_EN = [
        ('oliy', 'Higher'),
        ("o'rta", "Secondary"),
        ("o'rta mahsus", "Specialized secondary"),
    ]

    education_status_uz = models.CharField("Ma'lumot (uz)", max_length=20, choices=CHOOSED_STATUS_UZ, blank=True, null=True)
    education_status_ru = models.CharField("Ma'lumot (ru)", max_length=20, choices=CHOOSED_STATUS_RU, blank=True, null=True)
    education_status_en = models.CharField("Ma'lumot (en)", max_length=20, choices=CHOOSED_STATUS_EN, blank=True, null=True)

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Kim tomonidan / Кем создано / Created By"
    )

    # Qo‘lda kiritiladiganlar
    answered_requests = models.PositiveIntegerField(default=0, verbose_name="Qabul qilinganlar")
    rejected_requests = models.PositiveIntegerField(default=0, verbose_name="Rad etilganlar")
    pending_requests = models.PositiveIntegerField(default=0, verbose_name="Ko‘rib chiqilayotganlar")

    def __str__(self):
        return self.title_uz or self.title_ru or self.title_en or "No title"


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
    name_uz = models.CharField("Ism (uz)", max_length=100, blank=True, null=True)
    name_ru = models.CharField("Имя (ru)", max_length=100, blank=True, null=True)
    name_en = models.CharField("Name (en)", max_length=100, blank=True, null=True)
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
        return f"{self.name_uz or self.name_ru or self.name_en} - {self.jobVacancy}"



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
        'Ming Oʻrik': {'uz': 'Ming Oʻrik', 'ru': 'Минг Ўрик', 'en': 'Ming Oʻrik'},
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

    station_name = models.CharField("Bekat / Станция / Station", max_length=100, choices=STATION_CHOICES)
    month = models.CharField("Oy / Месяц / Month", max_length=20, choices=MONTH_CHOICES, default='Yanvar')
    user_count = models.PositiveIntegerField("Foydalanuvchilar soni / Кол-во пользователей / Users Count", default=0)
    created_at = models.DateTimeField("Qo‘shilgan vaqt / Дата добавления / Created At", auto_now_add=True)

    def __str__(self):
        return f"{self.get_station_name_display()} ({self.get_month_display()}) - {self.user_count} ta odam"

    def get_station_translation(self, lang):
        translations = self.STATION_TRANSLATIONS.get(self.station_name)
        if not translations:
            return self.station_name  # yoki ''
        return translations.get(lang, self.station_name)

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
    name = models.CharField("Ism", max_length=100, blank=True, null=True)

    phone = models.CharField("Telefon", max_length=20, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)

    address = models.CharField("Manzil", max_length=255, blank=True, null=True)
    passport = models.CharField("Passport", max_length=9, blank=True, null=True)

    message = models.TextField("Xabar", blank=True, null=True)
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
 


