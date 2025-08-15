from rest_framework import viewsets, permissions, status, mixins,generics,  filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from .models import (
    News, Comment, NewsImage,
    JobVacancy,JobVacancyRequest, StatisticData,
    LostItemRequest,FoydalanuvchiStatistika
)
from .throttles import LostItemBurstRateThrottle
from .serializers import (
    NewsCreateSerializer,
    NewsCreateSerializerRu, NewsCreateSerializerUz, NewsCreateSerializerEn,
    NewsSerializerUz, NewsSerializerRu, NewsSerializerEn,
    LatestNewsSerializerRu, LatestNewsSerializerUz, LatestNewsSerializerEn,
    MainNewsSerializerRu, MainNewsSerializerUz, MainNewsSerializerEn,
    CommentSerializerUz, CommentSerializerRu, CommentSerializerEn,
    NewsImageSerializer,
    JobVacancySerializerUz, JobVacancySerializerRu, JobVacancySerializerEn,
    JobVacancyRequestSerializerUz, JobVacancyRequestSerializerRu, JobVacancyRequestSerializerEn,
    StatisticDataSerializer, StatisticDataWriteSerializer,
    LostItemRequestSerializer, CustomUserSerializer,UserCreateSerializer, UserUpdateSerializer,JobVacancySerializer
)
from rest_framework.decorators import action
from .permissions import (
    IsNewsEditorOrReadOnly, IsHRUserOrReadOnly, IsStatisticianOrReadOnly, IsLostItemSupport
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta ,date
from django.utils import timezone
CACHE_TIMEOUT = 10
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .pagination import StandardResultsSetPagination
from collections import defaultdict
from django.conf import settings




class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
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


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer  
    permission_classes = [IsSuperUser]



# --- News ---

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsCreateSerializer
    permission_classes = [IsNewsEditorOrReadOnly] 

   
    def get_serializer_class(self):
        
        if self.action in ['create', 'update', 'partial_update']:
            return NewsCreateSerializer
        return NewsSerializerUz

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()




class NewsViewSetUz(viewsets.ModelViewSet):
    queryset = News.objects.all()
    permission_classes = [IsNewsEditorOrReadOnly]
    # pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializerUz
        return NewsSerializerUz

    def perform_create(self, serializer):
        serializer.save()


class NewsViewSetRu(viewsets.ModelViewSet):
    queryset = News.objects.all()
    permission_classes = [IsNewsEditorOrReadOnly]
    # pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializerRu
        return NewsSerializerRu

    def perform_create(self, serializer):
        serializer.save()


class NewsViewSetEn(viewsets.ModelViewSet):
    queryset = News.objects.all()
    permission_classes = [IsNewsEditorOrReadOnly]
    # pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializerEn
        return NewsSerializerEn

    def perform_create(self, serializer):
        serializer.save()


# --- News Like ---
class NewsLikeView(APIView):
    permission_classes = [permissions.AllowAny]  

    # Like sonini olish
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def get(self, request, pk):
        news = get_object_or_404(News, pk=pk)
        return Response({
            "like_count": news.like_count
        }, status=status.HTTP_200_OK)

    # Like qo‘shish
    def post(self, request, pk):
        news = get_object_or_404(News, pk=pk)

        news.like_count += 1
        news.save(update_fields=["like_count"])

        return Response({
            "message": "Liked!",
            "like_count": news.like_count
        }, status=status.HTTP_200_OK)


# --- Comments ---
@method_decorator(cache_page(CACHE_TIMEOUT), name='list')
class CommentViewSetUz(viewsets.ModelViewSet):
    serializer_class = CommentSerializerUz
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        news_id = self.request.query_params.get('news_id')
        qs = Comment.objects.all().order_by('-timestamp')
        if news_id:
            qs = qs.filter(news_id=news_id)
        return qs


@method_decorator(cache_page(CACHE_TIMEOUT), name='list')
class CommentViewSetRu(viewsets.ModelViewSet):
    serializer_class = CommentSerializerRu
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        news_id = self.request.query_params.get('news_id')
        qs = Comment.objects.all().order_by('-timestamp')
        if news_id:
            qs = qs.filter(news_id=news_id)
        return qs


@method_decorator(cache_page(CACHE_TIMEOUT), name='list')
class CommentViewSetEn(viewsets.ModelViewSet):
    serializer_class = CommentSerializerEn
    permission_classes = [permissions.AllowAny]

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
    permission_classes = [permissions.IsAdminUser]


# --- Latest News ---
@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class LatestNewsListViewUz(ListAPIView):
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = LatestNewsSerializerUz
    permission_classes = [permissions.AllowAny]


@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class LatestNewsListViewRu(ListAPIView):
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = LatestNewsSerializerRu
    permission_classes = [permissions.AllowAny]


@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class LatestNewsListViewEn(ListAPIView):
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = LatestNewsSerializerEn
    permission_classes = [permissions.AllowAny]


# --- Main News ---
@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class MainNewsListViewUz(ListAPIView):
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = MainNewsSerializerUz
    permission_classes = [permissions.AllowAny]


@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class MainNewsListViewRu(ListAPIView):
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = MainNewsSerializerRu
    permission_classes = [permissions.AllowAny]


@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class MainNewsListViewEn(ListAPIView):
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = MainNewsSerializerEn
    permission_classes = [permissions.AllowAny]


# --- Job Vacancies ---

@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class JobVacancyViewSet(viewsets.ModelViewSet):
    serializer_class = JobVacancySerializer
    permission_classes = [IsHRUserOrReadOnly]

    def get_queryset(self):
        return JobVacancy.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class JobVacancyViewSetUz(viewsets.ModelViewSet):
    serializer_class = JobVacancySerializerUz
    permission_classes = [IsHRUserOrReadOnly]

    def get_queryset(self):
        return JobVacancy.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class JobVacancyViewSetRu(viewsets.ModelViewSet):
    serializer_class = JobVacancySerializerRu
    permission_classes = [IsHRUserOrReadOnly]

    def get_queryset(self):
        return JobVacancy.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class JobVacancyViewSetEn(viewsets.ModelViewSet):
    serializer_class = JobVacancySerializerEn
    permission_classes = [IsHRUserOrReadOnly]

    def get_queryset(self):
        return JobVacancy.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# --- JobVacancyRequest ---
@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class JobVacancyRequestViewSetUz(viewsets.ModelViewSet):
    queryset = JobVacancyRequest.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        return JobVacancyRequestSerializerUz

    def get_permissions(self):
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


@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class JobVacancyRequestViewSetRu(viewsets.ModelViewSet):
    queryset = JobVacancyRequest.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        return JobVacancyRequestSerializerRu

    def get_permissions(self):
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


@method_decorator(cache_page(CACHE_TIMEOUT), name='dispatch')
class JobVacancyRequestViewSetEn(viewsets.ModelViewSet):
    queryset = JobVacancyRequest.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        return JobVacancyRequestSerializerEn

    def get_permissions(self):
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
        return StatisticData.objects.all()

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
        return StatisticData.objects.all()

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
        return StatisticData.objects.all()

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

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') == "Lost Item Support"):
            return LostItemRequest.objects.all().order_by('-created_at')
        return LostItemRequest.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(status='pending')

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_superuser or getattr(user, 'role', '') == "Lost Item Support"):
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

        if user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') == "Lost Item Support"):
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