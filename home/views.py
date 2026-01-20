from rest_framework import viewsets, permissions, status, mixins,generics,  filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from .models import (
    Department, FrontendImage, Management, News, Comment, NewsImage,
    JobVacancy,JobVacancyRequest, StatisticData,
    LostItemRequest,FoydalanuvchiStatistika,Announcement,AnnouncementComment,NewsLike,
    Korrupsiya, KorrupsiyaImage, KorrupsiyaComment, KorrupsiyaLike,
    SimpleUser, PhoneVerification, CustomUser,NewsView,KorrupsiyaView, AnnouncementView,StationFront,
    MediaPhoto, MediaVideo
)
from .throttles import LostItemBurstRateThrottle
from .serializers import (
    DepartmentSerializer, ManagementSerializer, NewsCreateSerializer,NewsSerializer,
    CommentSerializer,
    NewsImageSerializer,
    JobVacancyRequestSerializer, StationFrontSerializer, 
    StatisticDataSerializer, StatisticDataWriteSerializer,
    LostItemRequestSerializer, CustomUserSerializer,UserCreateSerializer, UserUpdateSerializer,JobVacancySerializer,
    AnnouncementImageSerializer,AnnouncementCreateSerializer,
    KorrupsiyaSerializer, KorrupsiyaImageSerializer, KorrupsiyaCreateSerializer,KorrupsiyaCommentSerializer,
    AnnouncementSerializer,AnnouncementLike,AnnouncementCommentSerializer,
    SimpleUserSerializer, VerifyCodeSerializer,LoginByPhoneSerializer,SimplePhoneLoginSerializer,
    MediaPhotoSerializer, MediaVideoSerializer
)
import os
from django.db.models import F
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from .permissions import (
    IsNewsEditorOrReadOnly, IsHRUserOrReadOnly, IsStatisticianOrReadOnly, IsLostItemSupport,IsVerifiedSimpleUser
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta ,date
from django.utils import timezone
CACHE_TIMEOUT = 30 
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .pagination import StandardResultsSetPagination
from collections import defaultdict
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .utils.sms_utils import send_sms_via_eskiz
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
import re
class CurrentUserView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer   
        return CustomUserSerializer       

    def get_object(self):
        return self.request.user


User = get_user_model()

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer  
    permission_classes = [IsSuperUser]


    def get_queryset(self):
        return User.objects.filter(is_superuser=False)


def get_client_ip(request):
    """Foydalanuvchi IP manzilini olish"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsNewsEditorOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    search_fields = [
        "title",
        "description",
        "fullContent",
    ]
    filterset_fields = {    
        "category": ["exact"],     
        "publishedAt": ["gte", "lte"],  
    }
    ordering_fields = [
        "publishedAt",
        "like_count",
        "title",
    ]
    ordering = ["-publishedAt"]
    

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        if lang:
            return News.objects.filter(language=lang)
        return News.objects.all()

    def perform_create(self, serializer):
        lang = self.kwargs.get('lang', 'uz')
        serializer.save(language=lang)
        
        
    def retrieve(self, request, *args, **kwargs):
        """Foydalanuvchi yangilikni ko‘rsa view qo‘shish"""
        instance = self.get_object()
        identifier = get_client_ip(request)  

        NewsView.objects.get_or_create(news=instance, session_key=identifier)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
        
        
        



class NewsLikeView(APIView):
    permission_classes = [IsVerifiedSimpleUser]
    

    def post(self, request, pk):
        news = get_object_or_404(News, pk=pk)

        try:
            simple_user = SimpleUser.objects.get(phone=request.user.username)
        except SimpleUser.DoesNotExist:
            return Response(
                {"error": "Faqat SimpleUser like bosishi mumkin"},
                status=403
            )

        session_key = simple_user.phone

        like, created = NewsLike.objects.get_or_create(
            news=news,
            session_key=session_key
        )

        if created:
            liked = True
        else:
            like.delete()
            liked = False

        news.like_count = news.likes.count()
        news.save(update_fields=['like_count'])

        return Response({
            "liked": liked,
            "like_count": news.like_count
        }, status=200)




# --- Comments ---
@method_decorator(cache_page(CACHE_TIMEOUT), name='list')
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsVerifiedSimpleUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        news_id = self.request.query_params.get('news_id')
        qs = Comment.objects.all().order_by('-timestamp')
        if news_id:
            qs = qs.filter(news_id=news_id)
        return qs
    
    def retrieve(self, request, *args, **kwargs):
        news_id = kwargs.get('pk') 
        
        comments = Comment.objects.filter(news_id=news_id).order_by('-timestamp')
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        try:
            simple_user = SimpleUser.objects.get(phone=self.request.user.username)
            full_name = f"{simple_user.first_name} {simple_user.last_name}"
            serializer.save(author=full_name)
        except SimpleUser.DoesNotExist:
            serializer.save(author=self.request.user.username)



# --- News Images ---
class NewsImageViewSet(viewsets.ModelViewSet):
    queryset = NewsImage.objects.all()
    serializer_class = NewsImageSerializer
    permission_classes = [IsNewsEditorOrReadOnly]

    def create(self, request, *args, **kwargs):
        news_id = request.data.get("news")
        if not news_id:
            return Response({"error": "news id yuborilishi kerak"}, status=status.HTTP_400_BAD_REQUEST)

        news = get_object_or_404(News, pk=news_id)

        # 1) bir nechta rasm yuborilgan bo‘lsa
        images = request.FILES.getlist("images")
        if images:
            created_images = []
            for img in images:
                obj = NewsImage.objects.create(news=news, image=img)
                created_images.append(obj)
            serializer = self.get_serializer(created_images, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # 2) agar bitta rasm "image" bilan yuborilsa
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)





# --- Job Vacancies ---

@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class JobVacancyViewSet(viewsets.ModelViewSet):
    queryset = JobVacancy.objects.all()
    serializer_class = JobVacancySerializer
    permission_classes = [IsHRUserOrReadOnly]

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        if lang:
            return JobVacancy.objects.filter(language=lang)
        return JobVacancy.objects.all()

    def perform_create(self, serializer):
        lang = self.kwargs.get('lang', 'uz')
        serializer.save(language=lang, created_by=self.request.user)


# --- JobVacancyRequest ---
@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class JobVacancyRequestViewSet(viewsets.ModelViewSet):
    serializer_class = JobVacancyRequestSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsVerifiedSimpleUser()]   
        if self.action in ['list', 'retrieve', 'partial_update', 'update', 'destroy']:
            return [IsHRUserOrReadOnly()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return JobVacancyRequest.objects.none()

        # Hamma authenticated foydalanuvchilar uchun barcha murojaatlar
        return JobVacancyRequest.objects.all().order_by('-created_at')


    def perform_create(self, serializer):
        
        user = self.request.user
        try:
            simple_user = SimpleUser.objects.get(phone=user.username)
            full_name = f"{simple_user.first_name} {simple_user.last_name}"
            phone_number = simple_user.phone
        except SimpleUser.DoesNotExist:
            full_name = user.get_full_name() or user.username
            phone_number = user.username

        serializer.save(
            name=full_name,
            phone=phone_number,
            status='pending'
        )


# --- StatisticData ---
@method_decorator(cache_page(CACHE_TIMEOUT), name='list')
@method_decorator(cache_page(CACHE_TIMEOUT), name='retrieve')
class StatisticDataViewSetUz(viewsets.ModelViewSet):
    permission_classes = [IsStatisticianOrReadOnly]

    def get_queryset(self):
        return StatisticData.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StatisticDataWriteSerializer
        return StatisticDataSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = 'uz'
        return context


@method_decorator(cache_page(CACHE_TIMEOUT), name='list')
@method_decorator(cache_page(CACHE_TIMEOUT), name='retrieve')
class StatisticDataViewSetRu(viewsets.ModelViewSet):
    permission_classes = [IsStatisticianOrReadOnly]

    def get_queryset(self):
        return StatisticData.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StatisticDataWriteSerializer
        return StatisticDataSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = 'ru'
        return context


@method_decorator(cache_page(CACHE_TIMEOUT), name='list')
@method_decorator(cache_page(CACHE_TIMEOUT), name='retrieve')
class StatisticDataViewSetEn(viewsets.ModelViewSet):
    permission_classes = [IsStatisticianOrReadOnly]

    def get_queryset(self):
        return StatisticData.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StatisticDataWriteSerializer
        return StatisticDataSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = 'en'
        return context



MONTHS_FIRST_HALF = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun']
MONTHS_SECOND_HALF = ['Iyul', 'Avgust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr']

class StatisticDataListView(ListAPIView):
    serializer_class = StatisticDataSerializer

    def get_queryset(self):
        lang = self.kwargs.get('lang', 'uz')
        year = str(self.kwargs.get('year'))  # CharField bo‘lgani uchun string bo‘lishi kerak
        period = self.kwargs.get('period')

        queryset = StatisticData.objects.filter(year=year)

        if period == 1:
            queryset = queryset.filter(month__in=MONTHS_FIRST_HALF)
        elif period == 2:
            queryset = queryset.filter(month__in=MONTHS_SECOND_HALF)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = self.kwargs.get('lang', 'uz')
        return context



class Last6MonthsStatisticDataViewSet(viewsets.ReadOnlyModelViewSet):
    
    permission_classes = [IsStatisticianOrReadOnly]

    def month_to_number(self, month_name):
        MONTHS = {
            'Yanvar': 1, 'Fevral': 2, 'Mart': 3, 'Aprel': 4, 'May': 5, 'Iyun': 6,
            'Iyul': 7, 'Avgust': 8, 'Sentyabr': 9, 'Oktyabr': 10, 'Noyabr': 11, 'Dekabr': 12
        }
        return MONTHS.get(month_name, 0)

    def get_last_6_months(self):
        # Eng oxirgi 6 (yil, oy) juftligini olish
        months = (
            StatisticData.objects
            .values_list('year', 'month')
            .distinct()
        )
        sorted_months = sorted(
            months,
            key=lambda x: (x[0], self.month_to_number(x[1])),
            reverse=True
        )
        return sorted_months[:6]

    def get_queryset(self):
        last_6_months = self.get_last_6_months()
        years = [y for y, m in last_6_months]
        months = [m for y, m in last_6_months]
        return StatisticData.objects.filter(year__in=years, month__in=months)

    def get_serializer_class(self):
        # faqat o'qish uchun
        return StatisticDataSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = 'en'
        return context



class LostItemRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LostItemRequestSerializer
    throttle_classes = [LostItemBurstRateThrottle]
    parser_classes = [JSONParser, MultiPartParser, FormParser]


    def get_permissions(self):
        if self.action == 'create':
            return [IsVerifiedSimpleUser()]   

        if self.action == 'list':
            return [permissions.AllowAny()]   

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Superuser yoki Lost Item Support → hamma murojaatlar
            if user.is_superuser or getattr(user, 'role', '') == 'lost_item_support':
                return LostItemRequest.objects.all().order_by('-created_at')

            # Oddiy foydalanuvchi → faqat o‘z eng oxirgi murojaati
            try:
                simple_user = SimpleUser.objects.get(phone=user.username)
                phone_number = simple_user.phone
            except SimpleUser.DoesNotExist:
                phone_number = user.username

            last_request = LostItemRequest.objects.filter(phone=phone_number).order_by('-id').first()

            if last_request:
                return LostItemRequest.objects.filter(id=last_request.id)
            return LostItemRequest.objects.none()
    
    
    
    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_superuser or getattr(user, 'role', '') == 'lost_item_support'):
            serializer.validated_data.pop('status', None)
        serializer.save()

    @method_decorator(cache_page(CACHE_TIMEOUT), name='list')
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # Stats → har doim barcha murojaatlar bo‘yicha
        total = LostItemRequest.objects.count()
        answered = LostItemRequest.objects.filter(status='answered').count()
        unanswered = total - answered
        percentage = round((answered / total) * 100, 2) if total > 0 else 0

        stats = {
            "total_requests": total,
            "answered_percentage": percentage,
            "answered_requests": answered,
            "unanswered_requests": unanswered
        }

        return Response({
            "stats": stats,
            "requests": serializer.data  
        })

    



@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class FoydalanuvchiStatistikaView(APIView):
    permission_classes = [permissions.AllowAny]  

    def get(self, request):
        stat = FoydalanuvchiStatistika.objects.first()
        jami = stat.jami_kirishlar if stat else 0
        onlayn = FoydalanuvchiStatistika.get_onlayn_foydalanuvchilar()

        return Response({
            "jami_foydalanuvchilar": jami,
            "onlayn_foydalanuvchilar": onlayn
        })


class IsAdminUserOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff




class TokenInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Foydalanuvchi uchun yangi refresh va access token
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Access tokenning muddati (sekundlarda)
        access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        expires_in = int(access_lifetime.total_seconds())

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "expires_in": expires_in
        })
   
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Access token muddati (soniyada)
        access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        expires_in = int(access_lifetime.total_seconds())

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "expires_in": expires_in,
        }, status=status.HTTP_200_OK)
    




class TestPingView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Cron-job yuborayotgan data {"1": "1"}
        if request.data.get("1") == "1":
            return Response({"pong": 2})
        return Response({"pong": "Xato ma'lumot"})
    
    
    
    

class APILoginView(APIView):
    def post(self, request):
        data = request.data
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })
        return Response({"detail":"Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
    
class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsNewsEditorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    search_fields = [
        "title",
        "description",
        "content",
    ]

    filterset_fields = {
        "lang": ["exact"],                 
        "published_at": ["gte", "lte"],    
    }

    ordering_fields = [
        "published_at",
        "title",
    ]

    ordering = ["-published_at"]
    

    def get_queryset(self):
        lang = self.kwargs.get('lang', 'uz')
        return Announcement.objects.filter(lang=lang)

    def perform_create(self, serializer):
        lang = self.kwargs.get('lang', 'uz')
        serializer.save(lang=lang)
        
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        identifier = get_client_ip(request)

        AnnouncementView.objects.get_or_create(
            announcement=instance,
            session_key=identifier
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)



    
class AnnouncementCommentViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementCommentSerializer
    
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsVerifiedSimpleUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        announcement_id = self.request.query_params.get('announcement_id')
        qs = AnnouncementComment.objects.all()

        if announcement_id:
            qs = qs.filter(announcement_id=announcement_id)

        return qs
    
    def perform_create(self, serializer):
        try:
            simple_user = SimpleUser.objects.get(phone=self.request.user.username)
            full_name = f"{simple_user.first_name} {simple_user.last_name}"
            serializer.save(author=full_name)
        except SimpleUser.DoesNotExist:
            serializer.save(author="Noma'lum foydalanuvchi")

    def retrieve(self, request, *args, **kwargs):
        ann_id = kwargs.get('pk') 
        
        comments = AnnouncementComment.objects.filter(announcement_id=ann_id).order_by('-timestamp')
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
    
class AnnouncementLikeView(APIView):
    permission_classes = [IsVerifiedSimpleUser]

    def post(self, request, pk):
        # 1. Announcementni topamiz
        announcement = get_object_or_404(Announcement, pk=pk)

        # 2. SimpleUser-ni tekshiramiz
        try:
            simple_user = SimpleUser.objects.get(phone=request.user.username)
        except SimpleUser.DoesNotExist:
            return Response(
                {"error": "Faqat SimpleUser like bosishi mumkin"},
                status=403
            )

        session_key = simple_user.phone

        # 3. Like-ni Toggle qilish (get_or_create)
        like, created = AnnouncementLike.objects.get_or_create(
            announcement=announcement,
            session_key=session_key
        )

        if created:
            liked = True
        else:
            like.delete()
            liked = False

        # 4. Like sonini hisoblab modelga saqlaymiz (Xuddi News-dagi kabi)
        announcement.like_count = announcement.likes.count()
        announcement.save(update_fields=['like_count'])

        # 5. Natijani qaytaramiz
        return Response({
            "liked": liked,
            "like_count": announcement.like_count
        }, status=200)


class KorrupsiyaViewSet(viewsets.ModelViewSet):
    serializer_class = KorrupsiyaSerializer
    permission_classes = [IsNewsEditorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    search_fields = [
        "title",
        "description",
        "fullContent",
    ]

    filterset_fields = {
        "category": ["exact"], 
        "title": ["exact"],
        "publishedAt": ["gte", "lte"],        
    }
    
    ordering_fields = [
        "publishedAt",
        "like_count",
        "title",
    ]
       
    

    def get_queryset(self):
        lang = self.kwargs.get('lang', 'uz')
        return Korrupsiya.objects.filter(language=lang)

    def perform_create(self, serializer):
        lang = self.kwargs.get('lang', 'uz')
        serializer.save(language=lang)
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        identifier = get_client_ip(request)

        KorrupsiyaView.objects.get_or_create(
            korrupsiya=instance,
            session_key=identifier
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

        
        
class KorrupsiyaCommentViewSet(viewsets.ModelViewSet):
    serializer_class = KorrupsiyaCommentSerializer
    permission_classes = [IsVerifiedSimpleUser]

    def get_queryset(self):
        korrupsiya_id = self.request.query_params.get('korrupsiya_id')
        qs = KorrupsiyaComment.objects.all()

        if korrupsiya_id:
            qs = qs.filter(korrupsiya_id=korrupsiya_id)

        return qs
    
    
    def perform_create(self, serializer):
        try:
            simple_user = SimpleUser.objects.get(phone=self.request.user.username)
            full_name = f"{simple_user.first_name} {simple_user.last_name}"
            serializer.save(author=full_name)
        except SimpleUser.DoesNotExist:
            serializer.save(author="Noma'lum foydalanuvchi")

    def retrieve(self, request, *args, **kwargs):
        ann_id = kwargs.get('pk') 

        comments = KorrupsiyaComment.objects.filter(korrupsiya_id=ann_id).order_by('-timestamp')
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
    
    
class KorrupsiyaLikeView(APIView):
    permission_classes = [IsVerifiedSimpleUser] # Faqat tasdiqlangan SimpleUser

    def post(self, request, pk):
        korrupsiya = get_object_or_404(Korrupsiya, pk=pk)
        
        try:
            simple_user = SimpleUser.objects.get(phone=request.user.username)
        except SimpleUser.DoesNotExist:
            return Response({"error": "Faqat SimpleUser like bosishi mumkin"}, status=403)

        session_key = simple_user.phone

        # Like toggle
        like, created = KorrupsiyaLike.objects.get_or_create(
            korrupsiya=korrupsiya,
            session_key=session_key
        )

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        # Modelda like_count ni yangilash
        korrupsiya.like_count = korrupsiya.likes.count()
        korrupsiya.save(update_fields=['like_count'])

        return Response({
            "liked": liked,
            "like_count": korrupsiya.like_count
        }, status=200) 
        
        
        
        
        
class SimpleUserViewSet(viewsets.ModelViewSet):
    queryset = SimpleUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'register':
            return SimpleUserSerializer
        elif self.action == 'login_by_phone':
            return LoginByPhoneSerializer
        elif self.action == 'verify_code':
            return VerifyCodeSerializer
        elif self.action == 'login_simple':
            return SimplePhoneLoginSerializer
        if self.action == 'me':
            return SimpleUserSerializer
        return SimpleUserSerializer

    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        try:
            user = SimpleUser.objects.get(phone=request.user.username)
        except SimpleUser.DoesNotExist:
            return Response({"error": "Profil topilmadi"}, status=404)

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            partial = (request.method == 'PATCH')
            serializer = self.get_serializer(user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    # 1. REGISTER
    @action(detail=False, methods=['post'])
    def register(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        phone = request.data.get("phone")

        # 1. Ma'lumotlar to'liqligini tekshirish
        if not (first_name and last_name and phone):
            return Response({"error": "Ma'lumotlar to'liq emas"}, status=400)

        # 2. Telefon raqami formatini tekshirish (+ belgi va 12 ta raqam)
        # Masalan: +998931090509
        phone_pattern = r'^\+\d{12}$'
        if not re.match(phone_pattern, phone):
            return Response({
                "error": "Telefon raqami noto'g'ri formatda. Namuna: +998931234567"
            }, status=400)

        # 3. Bazada bor yoki yo'qligini tekshirish
        if SimpleUser.objects.filter(phone=phone).exists():
            return Response({
                "error": "Bu telefon raqami bilan foydalanuvchi allaqachon ro'yxatdan o'tgan"
            }, status=400)

        # Kod yaratish va SMS yuborish
        code = PhoneVerification.generate_code()
        sms_text = f"uzmetro.uz saytiga ro'yhatdan o'tish uchun tasdiqlash kodi: {code}"
        
        if send_sms_via_eskiz(phone, sms_text):
            # Keshda 'purpose' (maqsad) bilan saqlaymiz
            cache.set(f"sms_auth_{code}", {
                "phone": phone,
                "first_name": first_name,
                "last_name": last_name,
                "action": "register"
            }, timeout=120)
            return Response({"message": "Ro'yxatdan o'tish uchun SMS yuborildi."}, status=200)
        
        return Response({"error": "SMS yuborishda xatolik"}, status=500)

    # 2. LOGIN BY PHONE
    @action(detail=False, methods=['post'])
    def login_by_phone(self, request):
        serializer = LoginByPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        # Bazada borligini tekshirish
        user_exists = SimpleUser.objects.filter(phone=phone, is_verified=True).exists()
        if not user_exists:
            return Response({"error": "Foydalanuvchi topilmadi. Avval ro'yxatdan o'ting."}, status=404)

        code = PhoneVerification.generate_code()
        sms_text = f"uzmetro.uz saytiga kirish uchun tasdiqlash kodi:  {code}"

        if send_sms_via_eskiz(phone, sms_text):
            cache.set(f"sms_auth_{code}", {
                "phone": phone,
                "action": "login"
            }, timeout=600)
            return Response({"message": "Kirish uchun SMS yuborildi."}, status=200)
        
        return Response({"error": "SMS yuborishda xatolik"}, status=500)

    # 3. UNIVERSAL VERIFY (Ikkalasi uchun bitta)
    @action(detail=False, methods=['post'])
    def verify_code(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        data = cache.get(f"sms_auth_{code}")
        if not data:
            return Response({"error": "Kod xato yoki muddati o'tgan"}, status=400)

        phone = data['phone']

        if data['action'] == "register":
            # Ro'yxatdan o'tkazish logikasi
            simple_user, _ = SimpleUser.objects.update_or_create(
                phone=phone,
                defaults={"first_name": data['first_name'], "last_name": data['last_name'], "is_verified": True}
            )
            main_user, created = CustomUser.objects.get_or_create(
                username=phone,
                defaults={"first_name": data['first_name'], "last_name": data['last_name'], "is_verified": True}
            )
            if created:
                main_user.set_password(phone)
                main_user.save()
        else:
            # Login logikasi
            simple_user = SimpleUser.objects.get(phone=phone)
            main_user = CustomUser.objects.get(username=phone)

        # Token yaratish
        refresh = RefreshToken.for_user(main_user)
        
        refresh.access_token.set_exp(lifetime=timedelta(days=60))
        refresh.set_exp(lifetime=timedelta(days=60))
        cache.delete(f"sms_auth_{code}")

        return Response({
            "message": f"Xush kelibsiz, {simple_user.first_name}!",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": SimpleUserSerializer(simple_user).data
        }, status=200)  
        
        
        
    @action(detail=False, methods=['post'], url_path='login-simple')
    def login_simple(self, request):
        serializer = SimplePhoneLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']

        # SimpleUser ni bazadan olamiz
        try:
            simple_user = SimpleUser.objects.get(phone=phone)
        except SimpleUser.DoesNotExist:
            return Response(
                {"error": "Bunday telefon raqam bilan foydalanuvchi topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not simple_user.is_verified:
            return Response(
                {"error": "Telefon raqam tasdiqlanmagan"},
                status=status.HTTP_403_FORBIDDEN
            )

        # CustomUser ni olamiz (token uchun)
        try:
            main_user = CustomUser.objects.get(username=phone)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Asosiy foydalanuvchi topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        # JWT tokenlar
        refresh = RefreshToken.for_user(main_user)
        refresh.access_token.set_exp(lifetime=timedelta(days=60))
        refresh.set_exp(lifetime=timedelta(days=60))

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "first_name": simple_user.first_name,
                "last_name": simple_user.last_name,
                "phone": simple_user.phone,
                "is_verified": simple_user.is_verified
            }
        }, status=status.HTTP_200_OK)

   
class FrontendImagesAPIView(APIView):
    def get(self, request):
        images = FrontendImage.objects.all()

        data = {}

        for img in images:
            if img.section not in data:
                data[img.section] = []

            data[img.section].append(
                request.build_absolute_uri(img.image.url)
            )

        return Response(data)

        
  


class MediaPhotosAPIView(APIView):
    def get(self, request, lang='uz'):
        qs = MediaPhoto.objects.filter(language=lang)
        serializer = MediaPhotoSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

class MediaVideosAPIView(APIView):
    def get(self, request, lang='uz'):
        qs = MediaVideo.objects.filter(language=lang)
        
        # Statistika yangilash (agar kerak bo'lsa)
        stat = FoydalanuvchiStatistika.objects.first()
        jami_kirishlar = str(stat.jami_kirishlar if stat else 0)
        
        # Viewsni avtomatik yangilab chiqish
        qs.update(views=jami_kirishlar)

        serializer = MediaVideoSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)    
    


class StationFrontListAPIView(APIView):
    def get(self, request):
        stations = StationFront.objects.all()
        result = {}
        for station in stations:
            serializer = StationFrontSerializer(station, context={'request': request})
            result[station.name] = serializer.data
        return Response(result)
    



class ManagementListAPIView(generics.ListAPIView):
    serializer_class = ManagementSerializer

    def get_queryset(self):
        # URL'dagi <str:lang> dan qiymatni oladi
        lang = self.kwargs.get('lang', 'uz') 
        return Management.objects.filter(language=lang)
    
    
class DepartmentListAPIView(generics.ListAPIView):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        lang = self.kwargs.get('lang', 'uz')
        return Department.objects.filter(language=lang)
    