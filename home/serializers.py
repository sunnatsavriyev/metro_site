from rest_framework import serializers
from .models import (
    News, Comment, NewsImage, JobVacancy,JobVacancyRequest,
    StatisticData, LostItemRequest, CustomUser,Announcement,AnnouncementComment,AnnouncementImage,AnnouncementLike,
    Korrupsiya, KorrupsiyaImage, KorrupsiyaComment,SimpleUser, PhoneVerification
)
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.conf import settings   # settings uchun
import requests 
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
        fields = ('username', 
                  'old_password', 'new_password', 'new_password2')

    def update(self, instance, validated_data):
        old_password = validated_data.pop('old_password', None)
        new_password = validated_data.pop('new_password', None)
        new_password2 = validated_data.pop('new_password2', None)

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
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'password']
        extra_kwargs = {
            'role': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Parolni xashlab saqlash
        user.save()
        return user









class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['id', 'news', 'image']


class NewsCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = News
        fields = [
            'id',
            'title',
            'description',
            'fullContent',
            'publishedAt', 'category',
            'images'
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        news = News.objects.create(**validated_data)
        for image in images:
            NewsImage.objects.create(news=news, image=image)
        return news






class NewsSerializer(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = News
        fields = ['id', 'language', 'title', 'description', 'fullContent', 'category', 'publishedAt', 'like_count', 'images']
        read_only_fields = ['language']
        
        
    def get_like_count(self, obj):
        return obj.likes.count()



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'author',
            'content',  'timestamp'
        ]






class JobVacancySerializer(serializers.ModelSerializer):
    total_requests = serializers.ReadOnlyField(source='requests.count')
    # ... boshqa method fieldlarni ham bitta titlega moslab yozasiz
    class Meta:
        model = JobVacancy
        fields = '__all__'
        read_only_fields = ['language', 'created_by']

    def get_total_requests(self, obj):
        return obj.requests.count()

    def get_answered_requests(self, obj):
        return obj.requests.filter(status='answered').count()

    def get_rejected_requests(self, obj):
        return obj.requests.filter(status='rejected').count()

    def get_pending_requests(self, obj):
        return obj.requests.filter(status='pending').count()

    def get_created_by(self, obj):
        user = getattr(obj, 'created_by', None)
        if user:
            full_name = f"{user.first_name} {user.last_name}".strip()
            return full_name if full_name else user.username
        return None




# ----------------- Uzbek -----------------
class JobVacancyRequestSerializer(serializers.ModelSerializer):
    # ID orqali bog‘lash va GETda ID ko‘rsatish
    jobVacancy = serializers.PrimaryKeyRelatedField(
        queryset=JobVacancy.objects.all()
    )
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = JobVacancyRequest
        fields = [
            'id', 'jobVacancy', 'name', 'phone', 'email', 'file',
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
        if not request or not request.user.is_authenticated or (
            not request.user.is_superuser and request.user.role not in ['HR', 'admin']
        ):
            data.pop('status', None)
            data.pop('status_display', None)
        return data





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
            'id', 'name', 'phone', 'email', 'address',
            'passport', 'message', 'created_at', 'status'
        ]
        read_only_fields = ['created_at']  # status endi PUT/PATCH da ko'rinadi

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        # Superuser yoki Lost Item Support bo‘lsa — hamma maydonlar
        if user and user.is_authenticated and (
            user.is_superuser or getattr(user, 'role', '') == "Lost Item Support"
        ):
            return rep

        # Oddiy foydalanuvchiga ham status ko‘rinadi
        return rep
    
    def validate(self, attrs):
        required_fields = [
            'name', 'phone', 'email', 'address', 'passport', 'message'
        ]

        missing_fields = [
            field for field in required_fields
            if not attrs.get(field)
        ]

        if missing_fields:
            raise serializers.ValidationError(
                "E’tiborli bo‘ling, barcha kataklarni to‘ldiring"
            )

        return attrs
    
    
    def validate_phone(self, value):
        if value:
            if len(value) != 13:
                raise serializers.ValidationError(
                    "Telefon raqamni namunadagiday kiriting.Masalan(+998901234567)"
                )
        return value

    #PASSPORT VALIDATION
    def validate_passport(self, value):
        if value:
            if len(value) != 9:
                raise serializers.ValidationError(
                    "Passport raqami aniq 9 ta belgidan iborat bo‘lishi kerak.(Masalan AA1234567)"
                )
        return value
    
    

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        # Agar superuser yoki Lost Item Support bo‘lmasa, status o'zgartirishga ruxsat yo'q
        if not (user and user.is_authenticated and (
            user.is_superuser or getattr(user, 'role', '') == "Lost Item Support"
        )):
            validated_data.pop('status', None)

        return super().update(instance, validated_data)




class AnnouncementImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementImage
        fields = ['id', 'image']




class AnnouncementCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'description', 'content', 'published_at', 'images']
        

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        announcement = Announcement.objects.create(**validated_data)

        for image in images:
            AnnouncementImage.objects.create(
                announcement=announcement,
                image=image
            )
        return announcement



class AnnouncementSerializer(serializers.ModelSerializer):
    images = AnnouncementImageSerializer(many=True, read_only=True)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'description', 'content', 'published_at', 'images']



class AnnouncementCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementComment
        fields = [
            'id',
            'announcement',
            'author',
            'content',
            'timestamp'
        ]
        read_only_fields = ['timestamp']



class KorrupsiyaImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = KorrupsiyaImage
        fields = ['id', 'image']
        
        
class KorrupsiyaCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Korrupsiya
        fields = ['id', 'title', 'description', 'images','FullContent', 'category', 'publishedAt']
        

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        korrupsiya = Korrupsiya.objects.create(**validated_data)

        for image in images:
            KorrupsiyaImage.objects.create(
                korrupsiya=korrupsiya,
                image=image
            )
        return korrupsiya
    
    
class KorrupsiyaSerializer(serializers.ModelSerializer):
    images = KorrupsiyaImageSerializer(many=True, read_only=True)

    class Meta:
        model = Korrupsiya
        fields = ['id', 'title', 'description', 'fullContent', 'category', 'publishedAt', 'images']
        
class KorrupsiyaCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KorrupsiyaComment
        fields = [
            'id',
            'korrupsiya',
            'author',
            'content',
            'timestamp'
        ]
        read_only_fields = ['timestamp']





class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleUser
        fields = ['id', 'first_name', 'last_name', 'phone', 'is_verified']

class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    
    
class LoginByPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, help_text="Ro'yxatdan o'tgan telefon raqami")