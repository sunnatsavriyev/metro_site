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
    NewsCreateSerializerRu, NewsCreateSerializerUz, NewsCreateSerializerEn,
    NewsSerializerUz, NewsSerializerRu, NewsSerializerEn,
    LatestNewsSerializerRu, LatestNewsSerializerUz, LatestNewsSerializerEn,
    MainNewsSerializerRu, MainNewsSerializerUz, MainNewsSerializerEn,
    CommentSerializerUz, CommentSerializerRu, CommentSerializerEn,
    NewsImageSerializer,
    JobVacancySerializerUz, JobVacancySerializerRu, JobVacancySerializerEn,
    JobVacancyRequestSerializerUz, JobVacancyRequestSerializerRu, JobVacancyRequestSerializerEn,
    StatisticDataSerializer, StatisticDataWriteSerializer,
    LostItemRequestSerializer, CustomUserSerializer,ChangePasswordSerializer,UserCreateSerializer
)
from rest_framework.decorators import action
from .permissions import (
    IsNewsEditorOrReadOnly, IsHRUserOrReadOnly, IsStatisticianOrReadOnly, IsLostItemSupport
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta ,date
from django.utils import timezone
CACHE_TIMEOUT = 60
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .pagination import StandardResultsSetPagination
from collections import defaultdict

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Yangi parol muvaffaqiyatli o'rnatildi"}, status=status.HTTP_200_OK)




class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


User = get_user_model()

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAdminUser]



# --- News ---
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



class AllStationsLast6MonthsView(APIView):

    def get_last_6_months(self):
        """
        Ma'lumotlar bazasida mavjud eng oxirgi 6 oy (year, month) ni aniqlash
        """
        months = (
            StatisticData.objects
            .values_list('year', 'month')
            .distinct()
        )

        # (year, month) ni sanaga aylantirib tartiblash
        month_pairs = sorted(
            [(y, m) for y, m in months],
            key=lambda x: (x[0], self.month_to_number(x[1])),
            reverse=True
        )

        return month_pairs[:6]  # eng oxirgi 6 oy

    def month_to_number(self, month_name):
        MONTHS = {
            'Yanvar': 1, 'Fevral': 2, 'Mart': 3, 'Aprel': 4, 'May': 5, 'Iyun': 6,
            'Iyul': 7, 'Avgust': 8, 'Sentyabr': 9, 'Oktyabr': 10, 'Noyabr': 11, 'Dekabr': 12
        }
        return MONTHS.get(month_name, 0)

    def get_queryset_last_6_months(self):
        last_6_months = self.get_last_6_months()

        # Filtrlash
        queryset = StatisticData.objects.filter(
            **{
                'year__in': [y for y, m in last_6_months],
                'month__in': [m for y, m in last_6_months]
            }
        )

        result = defaultdict(list)
        all_stations = queryset.values_list('station_name', flat=True).distinct()

        # Oylarni eng eski -> eng yangi tartibda olish
        last_6_months_sorted = sorted(last_6_months, key=lambda x: (x[0], self.month_to_number(x[1])))

        for year, month in last_6_months_sorted:
            month_data = queryset.filter(year=year, month=month) \
                                 .values('station_name') \
                                 .annotate(total=Sum('user_count'))
            for station in all_stations:
                entry = next((item for item in month_data if item['station_name'] == station), None)
                result[station].append({
                    'month': f"{month} {year}",
                    'total': entry['total'] if entry else 0
                })

        return result

    def get(self, request, *args, **kwargs):
        data = self.get_queryset_last_6_months()
        return Response(data)




class LostItemRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LostItemRequestSerializer
    throttle_classes = [LostItemBurstRateThrottle]

    @method_decorator(cache_page(CACHE_TIMEOUT), name='list')
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') == "Lost Item Support"):
            return LostItemRequest.objects.all().order_by('-created_at')
        return LostItemRequest.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_superuser or getattr(user, 'role', '') == "Lost Item Support"):
            serializer.validated_data.pop('status', None)
        serializer.save()

    @method_decorator(cache_page(CACHE_TIMEOUT), name='list')
    def list(self, request, *args, **kwargs):
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

        if request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, 'role', '') == "Lost Item Support"):
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "stats": stats,
                "requests": serializer.data
            })

        return Response({"stats": stats})


# --- Foydalanuvchi Statistika ---
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
