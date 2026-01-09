from rest_framework import viewsets, permissions, status, mixins,generics,  filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from .models import (
    News, Comment, NewsImage,
    JobVacancy,JobVacancyRequest, StatisticData,
    LostItemRequest,FoydalanuvchiStatistika,Announcement,AnnouncementComment,NewsLike,
    Korrupsiya, KorrupsiyaImage, KorrupsiyaComment, KorrupsiyaLike,
    SimpleUser, PhoneVerification
)
from .throttles import LostItemBurstRateThrottle
from .serializers import (
    NewsCreateSerializer,NewsSerializer,
    CommentSerializer,
    NewsImageSerializer,
    JobVacancyRequestSerializer, 
    StatisticDataSerializer, StatisticDataWriteSerializer,
    LostItemRequestSerializer, CustomUserSerializer,UserCreateSerializer, UserUpdateSerializer,JobVacancySerializer,
    AnnouncementImageSerializer,AnnouncementCreateSerializer,
    KorrupsiyaSerializer, KorrupsiyaImageSerializer, KorrupsiyaCreateSerializer,KorrupsiyaCommentSerializer,
    AnnouncementSerializer,AnnouncementLike,AnnouncementCommentSerializer,
    SimpleUserSerializer, VerifyCodeSerializer
)
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from .permissions import (
    IsNewsEditorOrReadOnly, IsHRUserOrReadOnly, IsStatisticianOrReadOnly, IsLostItemSupport,IsVerifiedSimpleUser
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
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


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def get_queryset(self):
        lang = self.kwargs.get('lang')
        if lang:
            return News.objects.filter(language=lang)
        return News.objects.all()

    def perform_create(self, serializer):
        lang = self.kwargs.get('lang', 'uz')
        serializer.save(language=lang)
        
        
        

def get_client_ip(request):
    """Foydalanuvchi IP manzilini olish"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class NewsLikeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        news = get_object_or_404(News, pk=pk)
        
        identifier = get_client_ip(request)

        like, created = NewsLike.objects.get_or_create(
            news=news,
            session_key=identifier  
        )

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        news.like_count = news.likes.count()
        news.save() 

        return Response({
            "liked": liked,
            "like_count": news.like_count
        }, status=status.HTTP_200_OK)



# --- Comments ---
@method_decorator(cache_page(CACHE_TIMEOUT), name='list')
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        news_id = self.request.query_params.get('news_id')
        qs = Comment.objects.all().order_by('-timestamp')
        if news_id:
            qs = qs.filter(news_id=news_id)
        return qs



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
    queryset = JobVacancyRequest.objects.all()

    def get_serializer_class(self):
        return JobVacancyRequestSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]   

        if self.action in ['list', 'retrieve', 'partial_update', 'update', 'destroy']:
            return [IsHRUserOrReadOnly()]

        return [permissions.AllowAny()]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return JobVacancyRequest.objects.none()
        if self.request.user.is_superuser or self.request.user.role in ['HR', 'admin']:
            return JobVacancyRequest.objects.all().order_by('-created_at')
        return JobVacancyRequest.objects.none()

    def perform_create(self, serializer):
        serializer.save(status='pending')


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

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') == 'lost_item_support'):
            return LostItemRequest.objects.all().order_by('-created_at')
        return LostItemRequest.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]   

        if self.action == 'list':
            return [permissions.AllowAny()]   

        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(status='pending')

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_superuser or getattr(user, 'role', '') == 'lost_item_support'):
            serializer.validated_data.pop('status', None)
        serializer.save()

    @method_decorator(cache_page(CACHE_TIMEOUT), name='list')
    def list(self, request, *args, **kwargs):
        user = request.user
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

        if user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') == 'lost_item_support'):
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "stats": stats,
                "requests": serializer.data
            })

        return Response({"stats": stats})
  



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

    def get_queryset(self):
        lang = self.kwargs.get('lang', 'uz')
        return Announcement.objects.filter(lang=lang)

    def perform_create(self, serializer):
        lang = self.kwargs.get('lang', 'uz')
        serializer.save(lang=lang)


    
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
    
    
class AnnouncementLikeToggleView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)

        # session yo‘q bo‘lsa yaratamiz
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        like, created = AnnouncementLike.objects.get_or_create(
            announcement=announcement,
            session_key=session_key
        )

        if not created:
            # Like bor edi → o‘chiramiz
            like.delete()
            liked = False
        else:
            liked = True

        return Response({
            "liked": liked,
            "like_count": AnnouncementLike.objects.filter(
                announcement=announcement
            ).count()
        }, status=status.HTTP_200_OK)
        
        
class AnnouncementLikeCountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        return Response({
            "like_count": announcement.likes.count()
        })




class KorrupsiyaViewSet(viewsets.ModelViewSet):
    serializer_class = KorrupsiyaSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        lang = self.kwargs.get('lang', 'uz')
        return Korrupsiya.objects.filter(language=lang)

    def perform_create(self, serializer):
        lang = self.kwargs.get('lang', 'uz')
        serializer.save(language=lang)
        
        
class KorrupsiyaCommentViewSet(viewsets.ModelViewSet):
    serializer_class = KorrupsiyaCommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        korrupsiya_id = self.request.query_params.get('korrupsiya_id')
        qs = KorrupsiyaComment.objects.all()

        if korrupsiya_id:
            qs = qs.filter(korrupsiya_id=korrupsiya_id)

        return qs
    
class KorrupsiyaLikeToggleView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        korrupsiya = get_object_or_404(Korrupsiya, pk=pk)

        # session yo‘q bo‘lsa yaratamiz
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        like, created = KorrupsiyaLike.objects.get_or_create(
            korrupsiya=korrupsiya,
            session_key=session_key
        )

        if not created:
            # Like bor edi → o‘chiramiz
            like.delete()
            liked = False
        else:
            liked = True

        return Response({
            "liked": liked,
            "like_count": KorrupsiyaLike.objects.filter(
                korrupsiya=korrupsiya
            ).count()
        }, status=status.HTTP_200_OK)
        
class KorrupsiyaLikeCountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        korrupsiya = get_object_or_404(Korrupsiya, pk=pk)
        return Response({
            "like_count": korrupsiya.likes.count()
        })
        
        
        
        
        
        
        
class SimpleUserViewSet(viewsets.ModelViewSet):
    queryset = SimpleUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'verify_code':
            return VerifyCodeSerializer
        return SimpleUserSerializer

    # 1-QADAM: Ro'yxatdan o'tish
    @action(detail=False, methods=['post'])
    def register(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        phone = request.data.get("phone")

        if not (first_name and last_name and phone):
            return Response(
                {"error": "Ma'lumotlar to'liq emas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Telefon bazada bormi tekshirish
        existing_user = SimpleUser.objects.filter(phone=phone).first()
        if existing_user and existing_user.is_verified:
            return Response(
                {
                    "message": "Siz allaqachon ro'yxatdan o'tgansiz",
                    "user": SimpleUserSerializer(existing_user).data
                },
                status=status.HTTP_200_OK
            )

        # 2. AVVAL KODNI GENERATSIYA QILAMIZ
        code = PhoneVerification.generate_code()

        # 3. ENDI KODNI SMS ORQALI YUBORAMIZ
        sms_text = f"uzmetro.uz saytiga ro'yhatdan o'tish uchun tasdiqlash kodi: {code}"
        sms_response = send_sms_via_eskiz(phone, sms_text)

        if not sms_response:
            return Response(
                {"error": "SMS yuborishda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 4. KESHGA SAQLASH (10 daqiqa)
        cache.set(
            f"sms_verify_{code}",
            {
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone
            },
            timeout=600
        )

        return Response(
            {
                "message": "SMS yuborildi. Kodni tasdiqlang.",
                # "code_for_test": code 
            },
            status=status.HTTP_200_OK
        )


    # 2-QADAM: Tasdiqlash
    @action(detail=False, methods=['post'])
    def verify_code(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        user_data = cache.get(f"sms_verify_{code}")

        if not user_data:
            return Response({"error": "Kod xato yoki muddati o'tgan"}, status=400)

        # 1. Bazaga saqlash yoki yangilash
        user, created = SimpleUser.objects.update_or_create(
            phone=user_data['phone'],
            defaults={
                "first_name": user_data['first_name'],
                "last_name": user_data['last_name'],
                "is_verified": True
            }
        )

        # 2. TOKEN GENERATSIYA QILISH
        # Bu qism foydalanuvchini har safar qayta login qildirmaslik uchun kerak
        refresh = RefreshToken.for_user(user)

        # 3. Keshni o'chirish
        cache.delete(f"sms_verify_{code}")

        return Response({
            "message": "Tabriklaymiz, ro'yxatdan o'tdingiz!",
            "access": str(refresh.access_token),  # Frontend buni saqlab qo'yadi
            "refresh": str(refresh),               # Tokenni yangilash uchun
            "user": SimpleUserSerializer(user).data
        }, status=status.HTTP_201_CREATED)