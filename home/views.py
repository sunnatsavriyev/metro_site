# home/views.py
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
    CommentSerializerUz, CommentSerializerRu, CommentSerializerEn,
    NewsImageSerializer,
    JobVacancySerializerUz, JobVacancySerializerRu, JobVacancySerializerEn,
    JobVacancyRequestSerializerUz, JobVacancyRequestSerializerRu, JobVacancyRequestSerializerEn,
    StatisticDataSerializer, StatisticDataWriteSerializer,
    LostItemRequestSerializer
)

from .permissions import (
    IsNewsEditorOrReadOnly, IsHRUserOrReadOnly, IsStatisticianOrReadOnly, IsLostItemSupport
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
# --- News ---

class NewsViewSetUz(viewsets.ModelViewSet):
    queryset = News.objects.all()
    permission_classes = [IsNewsEditorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializerUz
        return NewsSerializerUz

    def perform_create(self, serializer):
        serializer.save()


class NewsViewSetRu(viewsets.ModelViewSet):
    queryset = News.objects.all()
    permission_classes = [IsNewsEditorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializerRu
        return NewsSerializerRu

    def perform_create(self, serializer):
        serializer.save()


class NewsViewSetEn(viewsets.ModelViewSet):
    queryset = News.objects.all()
    permission_classes = [IsNewsEditorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializerEn
        return NewsSerializerEn

    def perform_create(self, serializer):
        serializer.save()



        
# --- News Like ---class 
class NewsLikeView(APIView):
    permission_classes = [permissions.AllowAny]  

    # Like sonini olish
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
class CommentViewSetUz(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerUz
    permission_classes = [permissions.AllowAny]


class CommentViewSetRu(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerRu
    permission_classes = [permissions.AllowAny]


class CommentViewSetEn(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerEn
    permission_classes = [permissions.AllowAny]




# --- News Images ---
class NewsImageViewSet(viewsets.ModelViewSet):
    queryset = NewsImage.objects.all()
    serializer_class = NewsImageSerializer
    permission_classes = [permissions.IsAdminUser]

class LatestNewsListViewUz(ListAPIView):
   
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = NewsSerializerUz
    permission_classes = [permissions.AllowAny]

 
class LatestNewsListViewRu(ListAPIView):
   
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = NewsSerializerRu
    permission_classes = [permissions.AllowAny]


class LatestNewsListViewEn(ListAPIView):
   
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = NewsSerializerEn
    permission_classes = [permissions.AllowAny]


# --- Job Vacancies (Kadrlar bo‘limi) ---
class JobVacancyViewSetUz(viewsets.ModelViewSet):
    serializer_class = JobVacancySerializerUz
    permission_classes = [IsHRUserOrReadOnly]

    def get_queryset(self):
        return JobVacancy.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class JobVacancyViewSetRu(viewsets.ModelViewSet):
    serializer_class = JobVacancySerializerRu
    permission_classes = [IsHRUserOrReadOnly]

    def get_queryset(self):
        return JobVacancy.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class JobVacancyViewSetEn(viewsets.ModelViewSet):
    serializer_class = JobVacancySerializerEn
    permission_classes = [IsHRUserOrReadOnly]

    def get_queryset(self):
        return JobVacancy.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# views.py
# ------- Uzbekcha Viewset -------
class JobVacancyRequestViewSetUz(viewsets.ModelViewSet):
    queryset = JobVacancyRequest.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        return JobVacancyRequestSerializerUz

    def get_permissions(self):
        # GET/PATCH/DELETE faqat HR yoki Admin uchun
        if self.action in ['list', 'retrieve', 'partial_update', 'update', 'destroy']:
            return [IsHRUserOrReadOnly()]
        # POST hammaga ruxsat
        return [permissions.AllowAny()]

    def get_queryset(self):
        # Login qilmaganlar va oddiy userlar ko‘ra olmaydi
        if not self.request.user.is_authenticated:
            return JobVacancyRequest.objects.none()
        if self.request.user.is_superuser or self.request.user.role in ['HR', 'admin']:
            return JobVacancyRequest.objects.all().order_by('-created_at')
        return JobVacancyRequest.objects.none()

    def perform_create(self, serializer):
        serializer.save(status='pending')


# ------- Ruscha Viewset -------
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


# ------- Inglizcha Viewset -------
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


# Uzbek view
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


# Russian view
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


# English view
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




class LostItemRequestViewSet(viewsets.ModelViewSet):
    queryset = LostItemRequest.objects.all().order_by('-created_at')
    serializer_class = LostItemRequestSerializer
    throttle_classes = [LostItemBurstRateThrottle]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]




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
