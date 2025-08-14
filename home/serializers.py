from rest_framework import serializers
from .models import (
    News, Comment, NewsImage, JobVacancy,JobVacancyRequest,
    StatisticData, LostItemRequest, CustomUser
)
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
User = get_user_model()



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role', 'is_staff', 'is_superuser')


class UserUpdateSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'role',
                  'old_password', 'new_password', 'new_password2')

    def update(self, instance, validated_data):
        old_password = validated_data.pop('old_password', None)
        new_password = validated_data.pop('new_password', None)
        new_password2 = validated_data.pop('new_password2', None)

        # Password o'zgartirish
        if old_password or new_password or new_password2:
            if not old_password or not new_password or not new_password2:
                raise serializers.ValidationError("Eski va yangi parollarni to‘liq kiriting.")
            if not instance.check_password(old_password):
                raise serializers.ValidationError({"old_password": "Eski parol noto‘g‘ri."})
            if new_password != new_password2:
                raise serializers.ValidationError({"new_password": "Yangi parol mos kelmadi."})
            instance.set_password(new_password)

        # Boshqa fieldlarni update qilish
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class UserCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role', 'old_password', 'new_password', 'new_password2']
        extra_kwargs = {
            'role': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Password o'zgartirish
        old_password = validated_data.pop('old_password', None)
        new_password = validated_data.pop('new_password', None)
        new_password2 = validated_data.pop('new_password2', None)

        # Agar password update qilinayotgan bo‘lsa
        if old_password or new_password or new_password2:
            if not old_password or not new_password or not new_password2:
                raise serializers.ValidationError("Eski va yangi parollarni to‘liq kiriting.")
            if not instance.check_password(old_password):
                raise serializers.ValidationError({"old_password": "Eski parol noto‘g‘ri."})
            if new_password != new_password2:
                raise serializers.ValidationError({"new_password": "Yangi parol mos kelmadi."})
            instance.set_password(new_password)

        # Boshqa fieldlar update qilinmaydi
        instance.save()
        return instance


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['id', 'image']


class NewsCreateSerializerUz(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = News
        fields = [
            'title_uz',  'description_uz',
            'fullContent_uz',  'publishedAt',
            'category_uz',  'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        news = News.objects.create(**validated_data)
        for image in images:
            NewsImage.objects.create(news=news, image=image)
        return news

class NewsCreateSerializerRu(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = News
        fields = [
            'title_ru',  'description_ru',
            'fullContent_ru',  'publishedAt',
            'category_ru',  'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        news = News.objects.create(**validated_data)
        for image in images:
            NewsImage.objects.create(news=news, image=image)
        return news



class NewsCreateSerializerEn(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = News
        fields = [
            'title_en',  'description_en',
            'fullContent_en',  'publishedAt',
            'category_en',  'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        news = News.objects.create(**validated_data)
        for image in images:
            NewsImage.objects.create(news=news, image=image)
        return news

class LatestNewsSerializerUz(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_uz', 
            'description_uz', 
            'fullContent_uz', 
            'publishedAt', 'category_uz',
            'like_count', 'image'
        ]

    def get_image(self, obj):
        # Birinchi rasmni olish (agar bor bo‘lsa)
        first_image = obj.images.first()  # related_name='images' bo‘lishi kerak
        return first_image.image.url if first_image else None


class LatestNewsSerializerRu(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_ru', 
            'description_ru', 
            'fullContent_ru', 
            'publishedAt', 'category_ru',
            'like_count', 'image'
        ]

    def get_image(self, obj):
        # Birinchi rasmni olish (agar bor bo‘lsa)
        first_image = obj.images.first()  # related_name='images' bo‘lishi kerak
        return first_image.image.url if first_image else None

class LatestNewsSerializerEn(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_en', 
            'description_en', 
            'fullContent_en', 
            'publishedAt', 'category_en',
            'like_count', 'image'
        ]

    def get_image(self, obj):
        # Birinchi rasmni olish (agar bor bo‘lsa)
        first_image = obj.images.first()  # related_name='images' bo‘lishi kerak
        return first_image.image.url if first_image else None



class MainNewsSerializerUz(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title_uz', 
            'image'
        ]

    def get_image(self, obj):
        # Birinchi rasmni olish (agar bor bo‘lsa)
        first_image = obj.images.first()  # related_name='images' bo‘lishi kerak
        return first_image.image.url if first_image else None


class MainNewsSerializerRu(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()


    class Meta:
        model = News
        fields = [
            'id', 'title_ru', 
            'image'
        ]

    def get_image(self, obj):
        # Birinchi rasmni olish (agar bor bo‘lsa)
        first_image = obj.images.first()  # related_name='images' bo‘lishi kerak
        return first_image.image.url if first_image else None


class MainNewsSerializerEn(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()


    class Meta:
        model = News
        fields = [
            'id', 'title_en', 
            'image'
        ]

    def get_image(self, obj):
        # Birinchi rasmni olish (agar bor bo‘lsa)
        first_image = obj.images.first()  # related_name='images' bo‘lishi kerak
        return first_image.image.url if first_image else None



class NewsSerializerUz(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_uz', 
            'description_uz', 
            'fullContent_uz', 
            'publishedAt', 'category_uz',
            'like_count', 'images'
        ]


class NewsSerializerRu(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_ru', 
            'description_ru', 
            'fullContent_ru', 
            'publishedAt', 'category_ru',
            'like_count', 'images'
        ]

class NewsSerializerEn(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title_en', 
            'description_en', 
            'fullContent_en', 
            'publishedAt', 'category_en',
            'like_count', 'images'
        ]


class CommentSerializerUz(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'author_uz',
            'content_uz',  'timestamp'
        ]



class CommentSerializerRu(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'author_ru',
            'content_ru',  'timestamp'
        ]




class CommentSerializerEn(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'author_en',
            'content_en',  'timestamp'
        ]


class JobVacancySerializerUz(serializers.ModelSerializer):
    total_requests = serializers.SerializerMethodField()
    answered_requests = serializers.SerializerMethodField()
    rejected_requests = serializers.SerializerMethodField()
    pending_requests = serializers.SerializerMethodField()

    class Meta:
        model = JobVacancy
        fields = [
            'id', 'title_uz', 'requirements_uz', 'mutaxasislik_uz',
            'education_status_uz', 'created_by',
            'total_requests', 'answered_requests', 'rejected_requests', 'pending_requests'
        ]

    def get_total_requests(self, obj):
        return obj.requests.count()

    def get_answered_requests(self, obj):
        return obj.requests.filter(status='answered').count()

    def get_rejected_requests(self, obj):
        return obj.requests.filter(status='rejected').count()

    def get_pending_requests(self, obj):
        return obj.requests.filter(status='pending').count()



class JobVacancySerializerRu(serializers.ModelSerializer):
    total_requests = serializers.SerializerMethodField()
    answered_requests = serializers.SerializerMethodField()
    rejected_requests = serializers.SerializerMethodField()
    pending_requests = serializers.SerializerMethodField()

    class Meta:
        model = JobVacancy
        fields = [
            'id', 'title_ru', 'requirements_ru', 'mutaxasislik_ru',
            'education_status_ru', 'created_by',
            'total_requests', 'answered_requests', 'rejected_requests', 'pending_requests'
        ]

    def get_total_requests(self, obj):
        return obj.requests.count()

    def get_answered_requests(self, obj):
        return obj.requests.filter(status='answered').count()

    def get_rejected_requests(self, obj):
        return obj.requests.filter(status='rejected').count()

    def get_pending_requests(self, obj):
        return obj.requests.filter(status='pending').count()



class JobVacancySerializerEn(serializers.ModelSerializer):
    total_requests = serializers.SerializerMethodField()
    answered_requests = serializers.SerializerMethodField()
    rejected_requests = serializers.SerializerMethodField()
    pending_requests = serializers.SerializerMethodField()

    class Meta:
        model = JobVacancy
        fields = [
            'id', 'title_en', 'requirements_en', 'mutaxasislik_en',
            'education_status_en', 'created_by',
            'total_requests', 'answered_requests', 'rejected_requests', 'pending_requests'
        ]

    def get_total_requests(self, obj):
        return obj.requests.count()

    def get_answered_requests(self, obj):
        return obj.requests.filter(status='answered').count()

    def get_rejected_requests(self, obj):
        return obj.requests.filter(status='rejected').count()

    def get_pending_requests(self, obj):
        return obj.requests.filter(status='pending').count()

# serializers.py


# ----------------Uzbek----------------
class JobVacancyRequestSerializerUz(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = JobVacancyRequest
        fields = [
            'id', 'jobVacancy', 'name_uz', 'phone', 'email', 'file',
            'status', 'status_display', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_status_display(self, obj):
        mapping = {
            'pending': "Ko'rilmoqda",
            'answered': "Javob berilgan",
            'rejected': "Rad etilgan",
        }
        return mapping.get(obj.status, obj.status)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Agar foydalanuvchi HR yoki Admin bo‘lmasa — status yashiriladi
        if not request or not request.user.is_authenticated or (
            not request.user.is_superuser and request.user.role not in ['HR', 'admin']
        ):
            data.pop('status', None)
            data.pop('status_display', None)

        return data

    def get_fields(self):
        """Browsable API formasi uchun statusni yashirish"""
        fields = super().get_fields()
        request = self.context.get('request')

        if not request or not request.user.is_authenticated or (
            not request.user.is_superuser and request.user.role not in ['HR', 'admin']
        ):
            fields.pop('status', None)
        return fields


# ----------------Ruscha----------------
class JobVacancyRequestSerializerRu(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = JobVacancyRequest
        fields = [
            'id', 'jobVacancy', 'name_ru', 'phone', 'email', 'file',
            'status', 'status_display', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_status_display(self, obj):
        mapping = {
            'pending': "Рассматривается",
            'answered': "Ответ дан",
            'rejected': "Отклонено",
        }
        return mapping.get(obj.status, obj.status)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Agar foydalanuvchi HR yoki Admin bo‘lmasa — status yashiriladi
        if not request or not request.user.is_authenticated or (
            not request.user.is_superuser and request.user.role not in ['HR', 'admin']
        ):
            data.pop('status', None)
            data.pop('status_display', None)

        return data

    def get_fields(self):
        """Browsable API formasi uchun statusni yashirish"""
        fields = super().get_fields()
        request = self.context.get('request')

        if not request or not request.user.is_authenticated or (
            not request.user.is_superuser and request.user.role not in ['HR', 'admin']
        ):
            fields.pop('status', None)
        return fields



# ---------------- Inglizcha ----------------
class JobVacancyRequestSerializerEn(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = JobVacancyRequest
        fields = [
            'id', 'jobVacancy', 'name_en', 'phone', 'email', 'file',
            'status', 'status_display', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_status_display(self, obj):
        mapping = {
            'pending': "pending",
            'answered': "answered",
            'rejected': "rejected",
        }
        return mapping.get(obj.status, obj.status)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Agar foydalanuvchi HR yoki Admin bo‘lmasa — status yashiriladi
        if not request or not request.user.is_authenticated or (
            not request.user.is_superuser and request.user.role not in ['HR', 'admin']
        ):
            data.pop('status', None)
            data.pop('status_display', None)

        return data

    def get_fields(self):
        """Browsable API formasi uchun statusni yashirish"""
        fields = super().get_fields()
        request = self.context.get('request')

        if not request or not request.user.is_authenticated or (
            not request.user.is_superuser and request.user.role not in ['HR', 'admin']
        ):
            fields.pop('status', None)
        return fields




class StatisticDataSerializer(serializers.ModelSerializer):
    station_name = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    class Meta:
        model = StatisticData
        fields = ['id', 'station_name', 'user_count','year', 'month', 'created_at']
        read_only_fields = ['created_at']

    # --- O‘qish uchun tarjima ---
    def get_station_name(self, obj):
        lang = self.context.get('lang', 'uz')  
        return obj.get_station_translation(lang)

    def get_year(self, obj):
        return obj.year

    def get_month(self, obj):
        lang = self.context.get('lang', 'uz')
        return obj.get_month_translation(lang)

class StatisticDataWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatisticData
        fields = ['station_name', 'user_count', 'year','month']
        extra_kwargs = {
            'station_name': {'required': True},
            'month': {'required': True},
            'year': {'required': True},
        }

class LostItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostItemRequest
        fields = [
            'id',
            'name',
            'phone',
            'email',
            'address',
            'passport',
            'message',
            'created_at',
            'status',
        ]
        read_only_fields = ['created_at']

    def get_fields(self):
        """Anonimuslar va oddiy userlar POST qilganda status maydonini olib tashlaymiz"""
        fields = super().get_fields()
        request = self.context.get('request')

        # Faqat superadmin va Lost Item Support uchun statusni ko‘rsatamiz (POST/PUT uchun)
        if not request or not request.user.is_authenticated or not (
            request.user.is_superuser or getattr(request.user, 'role', '') == "Lost Item Support"
        ):
            fields.pop('status', None)

        return fields

    def to_representation(self, instance):
        """Requestlar ro‘yxati qaytganda status faqat superadmin va Lost Item Support uchun ko‘rinadi"""
        rep = super().to_representation(instance)
        request = self.context.get('request')

        if not request or not request.user.is_authenticated or not (
            request.user.is_superuser or getattr(request.user, 'role', '') == "Lost Item Support"
        ):
            rep.pop('status', None)

        return rep

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)

    def validate(self, attrs):
        request = self.context.get('request')
        if 'status' in attrs and (not request.user.is_authenticated or not (
            request.user.is_superuser or getattr(request.user, 'role', '') == "Lost Item Support"
        )):
            attrs.pop('status', None)
        return attrs


# class LostItemRequestSerializer(serializers.ModelSerializer):
#     recaptcha_token = serializers.CharField(write_only=True)

#     class Meta:
#         model = LostItemRequest
#         fields = [
#             'id',
#             'name_uz', 'name_ru', 'name_en',
#             'phone', 'email',
#             'message_uz', 'message_ru', 'message_en',
#             'created_at',
#             'recaptcha_token'
#         ]
#         read_only_fields = ['created_at']

#     def validate_recaptcha_token(self, value):
#         """Google reCAPTCHA v3 tokenini tekshirish"""
#         url = "https://www.google.com/recaptcha/api/siteverify"
#         data = {
#             'secret': settings.RECAPTCHA_SECRET_KEY,
#             'response': value
#         }

#         try:
#             r = requests.post(url, data=data, timeout=5)
#             result = r.json()
#         except Exception:
#             raise serializers.ValidationError("reCAPTCHA serveriga ulanib bo‘lmadi.")

#         # Tekshirish natijasi
#         if not result.get('success'):
#             raise serializers.ValidationError("reCAPTCHA tasdiqlanmadi.")

#         score = result.get('score', 0)
#         if score < getattr(settings, 'RECAPTCHA_MIN_SCORE', 0.5):
#             raise serializers.ValidationError("So‘rov shubhali (score past).")

#         return value

#     def create(self, validated_data):
#         validated_data.pop('recaptcha_token', None)  # DB ga saqlanmasin
#         return super().create(validated_data)