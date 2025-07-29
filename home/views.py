# home/views.py
from rest_framework import viewsets, permissions, status, mixins,generics,  filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from .models import (
    News, Comment, NewsImage,
    JobVacancy, StatisticData,
    LostItemRequest,FoydalanuvchiStatistika 
)

from .serializers import (
    NewsCreateSerializerRu, NewsCreateSerializerUz, NewsCreateSerializerEn,
    NewsSerializerUz, NewsSerializerRu, NewsSerializerEn,
    CommentSerializerUz, CommentSerializerRu, CommentSerializerEn,
    NewsImageSerializer,
    JobVacancySerializerUz, JobVacancySerializerRu, JobVacancySerializerEn,
    StatisticDataSerializer, StatisticDataWriteSerializer,
    LostItemRequestSerializer,
)

from .permissions import (
    IsNewsEditorOrReadOnly, IsHRUserOrReadOnly, IsStatisticianOrReadOnly, IsLostItemSupport
)
from rest_framework.permissions import IsAuthenticated

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



        
# --- News Like ---
class NewsLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        news = get_object_or_404(News, pk=pk)
        news.likes += 1
        news.save()
        return Response({"message": "Liked!"}, status=status.HTTP_200_OK)


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