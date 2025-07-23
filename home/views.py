# home/views.py

from rest_framework import viewsets, permissions, status, mixins,generics,  filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
 
from .models import (
    News, Comment, NewsImage,
    JobVacancy, StatisticData,
    LostItemRequest, 
)

from .serializers import (
    NewsSerializer,NewsCreateSerializer, CommentSerializer, NewsImageSerializer,
    JobVacancySerializer, StatisticDataSerializer,
    LostItemRequestSerializer
)

from .permissions import (
    IsNewsEditorOrReadOnly, IsHRUser, IsStatistician, IsLostItemSupport
)
from rest_framework.permissions import IsAuthenticated

# --- News ---

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    permission_classes = [IsNewsEditorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializer
        return NewsSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

        
# --- News Like ---
class NewsLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        news = get_object_or_404(News, pk=pk)
        news.likes += 1
        news.save()
        return Response({"message": "Liked!"}, status=status.HTTP_200_OK)


# --- Comments ---
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]


# --- News Images ---
class NewsImageViewSet(viewsets.ModelViewSet):
    queryset = NewsImage.objects.all()
    serializer_class = NewsImageSerializer
    permission_classes = [permissions.IsAdminUser]


# --- Job Vacancies (Kadrlar bo‘limi) ---
class JobVacancyViewSet(viewsets.ModelViewSet):
    serializer_class = JobVacancySerializer
    permission_classes = [IsHRUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_hr or user.is_superuser):
            return JobVacancy.objects.all() if user.is_superuser else JobVacancy.objects.filter(created_by=user)
        return JobVacancy.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# --- Statistic Data (Statistiklar) ---
class StatisticDataViewSet(viewsets.ModelViewSet):
    serializer_class = StatisticDataSerializer
    permission_classes = [IsAuthenticated, IsStatistician]

    def get_queryset(self):
        user = self.request.user
        # Superuser hamma statistikani ko‘radi
        if user.is_authenticated and (user.is_statistician or user.is_superuser):
            return StatisticData.objects.all()
        return StatisticData.objects.none()

    def perform_create(self, serializer):
        # created_by yo‘qligi uchun oddiy saqlash
        serializer.save()



class LostItemRequestCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = LostItemRequest.objects.all()
    serializer_class = LostItemRequestSerializer
    permission_classes = [permissions.AllowAny]  



class LostItemRequestSupportViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LostItemRequest.objects.all().order_by('-created_at')
    serializer_class = LostItemRequestSerializer
    permission_classes = [IsAuthenticated, IsLostItemSupport]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']