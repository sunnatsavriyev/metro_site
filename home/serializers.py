from rest_framework import serializers
from .models import (
    Department, Management, News, Comment, NewsImage, JobVacancy,JobVacancyRequest,NewsView,NewsLike,
    StatisticData, LostItemRequest, CustomUser,Announcement,AnnouncementComment,AnnouncementImage,AnnouncementLike,
    Korrupsiya, KorrupsiyaImage, KorrupsiyaComment,SimpleUser, PhoneVerification, KorrupsiyaLike, KorrupsiyaView, AnnouncementView,
    MediaPhoto, MediaVideo, FoydalanuvchiStatistika,StationFront
)
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.conf import settings   # settings uchun
import requests 
from home.utils.business_days import add_business_days
from django.utils import timezone
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
    view_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    
    class Meta:
        model = News
        fields = ['id', 'language', 'title', 'description', 'fullContent', 'category', 'publishedAt', 'like_count','liked','view_count', 'images']
        read_only_fields = ['language']
        
        
    def get_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        try:
            simple_user = SimpleUser.objects.get(phone=request.user.username)
        except SimpleUser.DoesNotExist:
            return False

        return NewsLike.objects.filter(
            news=obj,
            session_key=simple_user.phone
        ).exists()

    def get_view_count(self, obj):
            return obj.views.count()

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'author',
            'content',  'timestamp'
        ]
        extra_kwargs = {
            'author': {'read_only': True} ,
            'timestamp': {'read_only': True}
        }






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
    jobVacancy = serializers.PrimaryKeyRelatedField(
        queryset=JobVacancy.objects.all()
    )

    class Meta:
        model = JobVacancyRequest
        fields = [
            'id', 'jobVacancy', 'name', 'phone', 'email', 'file',
            'status', 'created_at'
        ]
        read_only_fields = ['created_at', 'name', 'phone', 'status']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            user = request.user

            # Superuser va HR/ADMIN → hamma ma'lumotlar
            if user.is_superuser or user.role in ['HR', 'admin']:
                return data

            # Oddiy foydalanuvchi → faqat o‘z murojaati uchun status ko‘rsin
            try:
                simple_user = SimpleUser.objects.get(phone=user.username)
                phone_number = simple_user.phone
            except SimpleUser.DoesNotExist:
                phone_number = user.username

            if instance.phone == phone_number:
                return data

            # Boshqa foydalanuvchi murojaati → statusni yashirish
            data.pop('status', None)
            return data

        # Auth bo‘lmagan foydalanuvchi → statusni yashirish
        data.pop('status', None)
        return data

    def validate(self, attrs):
        """
        Oddiy foydalanuvchi uchun tekshiradi:
        - Shu jobVacancy uchun oldingi murojaat pending bo'lsa → xato beradi
        - Boshqa jobVacancy uchun yuborish mumkin
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            try:
                simple_user = SimpleUser.objects.get(phone=user.username)
                phone_number = simple_user.phone
            except SimpleUser.DoesNotExist:
                phone_number = user.username

            # Shu jobVacancy uchun oldingi murojaatni tekshirish
            job_vacancy = attrs.get('jobVacancy')
            existing_request = JobVacancyRequest.objects.filter(
                phone=phone_number,
                jobVacancy=job_vacancy,
                status='pending'
            ).first()

            if existing_request:
                raise serializers.ValidationError(
                    "Siz avval shu ishga murojaat yuborgansiz va u hali ko‘rib chiqilmoqda."
                )

        return super().validate(attrs)






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
    can_send_new_request = serializers.SerializerMethodField()
    deadline = serializers.SerializerMethodField()
    class Meta:
        model = LostItemRequest
        fields = [
            'id', 'name', 'phone', 'email', 'address',
            'passport', 'message', 'created_at', 'status','can_send_new_request', 'deadline'
        ]
        read_only_fields = ['created_at', 'name', 'phone', 'can_send_new_request','deadline']  

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
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        # Ish kunini tekshirish
        if user and user.is_authenticated:
            try:
                simple_user = SimpleUser.objects.get(phone=user.username)
                phone_number = simple_user.phone
            except SimpleUser.DoesNotExist:
                phone_number = user.username

            last_request = LostItemRequest.objects.filter(
                phone=phone_number
            ).order_by('-created_at').first()

            if last_request:
                # Agar status pending bo'lsa, deadline hisoblash
                if last_request.status == 'pending':
                    deadline = add_business_days(last_request.created_at.date(), 5)
                    if timezone.now().date() < deadline:
                        raise serializers.ValidationError(
                            f"Sizning avvalgi murojaatingizga hali javob berilmadi. "
                            f"Yangi murojaatni {deadline} dan keyin yuborishingiz mumkin."
                        )

        return super().validate(attrs)
    
    
    def get_can_send_new_request(self, obj):
        
        deadline = add_business_days(obj.created_at.date(), 5)

        if obj.status == 'answered' or timezone.now().date() >= deadline:
            return True

        return False
    
    def get_deadline(self, obj):
        return add_business_days(obj.created_at.date(), 5)

    #PASSPORT VALIDATION
    def validate_passport(self, value):
        if value:
            if len(value) != 9:
                raise serializers.ValidationError(
                    "Passport raqami aniq 9 ta belgidan iborat bo‘lishi kerak.(Masalan AA1234567)"
                )
        return value
    
    

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            try:
                simple_user = SimpleUser.objects.get(phone=user.username)
                validated_data['name'] = f"{simple_user.first_name} {simple_user.last_name}"
                validated_data['phone'] = simple_user.phone
            except SimpleUser.DoesNotExist:
                # Agar SimpleUser topilmasa, username ni ishlatish
                validated_data['name'] = user.get_full_name() or ""
                validated_data['phone'] = user.username

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
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    liked = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'description', 'content', 'published_at', 'images','like_count', 'liked', 'views_count']
        
        
    def get_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        try:
            # Newsnikidek SimpleUser telefonini olamiz
            simple_user = SimpleUser.objects.get(phone=request.user.username)
        except SimpleUser.DoesNotExist:
            return False

        return AnnouncementLike.objects.filter(
            announcement=obj, 
            session_key=simple_user.phone
        ).exists()
        
    def get_views_count(self, obj):
        return obj.views.count()



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
        read_only_fields = ['timestamp','author']



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
    liked = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    class Meta:
        model = Korrupsiya
        fields = ['id', 'title', 'description', 'fullContent', 'category', 'publishedAt', 'images','like_count', 'views_count', 'liked']
        
        
    def get_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        try:
            # SimpleUser ekanligini telefon raqami orqali tekshiramiz
            simple_user = SimpleUser.objects.get(phone=request.user.username)
            return KorrupsiyaLike.objects.filter(
                korrupsiya=obj, 
                session_key=simple_user.phone
            ).exists()
        except SimpleUser.DoesNotExist:
            return False
        
        
    def get_views_count(self, obj):
        return obj.views.count()
        
        
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
        read_only_fields = ['timestamp','author']
        
        
    





class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleUser
        fields = ['id', 'first_name', 'last_name', 'phone', 'is_verified']

class LoginByPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    
class SimplePhoneLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()






class MediaPhotoSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = MediaPhoto
        fields = ["id", "group_id", "language", "src", "title", "category"]

    def get_src(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class MediaVideoSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="video_url")
    views = serializers.SerializerMethodField()

    class Meta:
        model = MediaVideo
        fields = ["id", "group_id", "language", "url", "thumbnail", "title", "duration", "views", "category"]

    def get_views(self, obj):
        stat = FoydalanuvchiStatistika.objects.first()
        return stat.jami_kirishlar if stat else 0
    
    
         
class StationFrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationFront
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        
        # Rasmlar to'liq URL bo'lishi uchun
        images = []
        if instance.image1:
            images.append(request.build_absolute_uri(instance.image1.url))
        if instance.image2:
            images.append(request.build_absolute_uri(instance.image2.url))

        # Video muqovasi URL sifatida
        video_thumbnail_url = (
            request.build_absolute_uri(instance.video_thumbnail.url)
            if instance.video_thumbnail else None
        )

        # Siz xohlagan formatga o'tkazish
        return {
            "name": instance.name,
            "images": images,
            "videos": [
                {
                    "title": instance.video_title,
                    "url": instance.video_url,
                    "thumbnail": video_thumbnail_url,
                }
            ]
        }
        
        
        
        
class ManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Management
        fields = [
            'id', 'group_id', 'language', 'firstName', 'middleName', 
            'lastName', 'position', 'department', 'phone', 
            'email', 'hours', 'image', 'biography'
        ]
        
        
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            'id', 'group_id', 'language', 'title', 'head', 
            'schedule', 'reception', 'phone', 'email', 'image', 'order'
        ]