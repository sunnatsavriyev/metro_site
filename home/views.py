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
    NewsSerializer,NewsCreateSerializer, CommentSerializer, NewsImageSerializer,
    JobVacancySerializer, StatisticDataSerializer,
    LostItemRequestSerializer
)

from .permissions import (
    IsNewsEditorOrReadOnly, IsHRUserOrReadOnly, IsStatisticianOrReadOnly, IsLostItemSupport
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

class LatestNewsListView(ListAPIView):
   
    queryset = News.objects.all().order_by('-publishedAt')[:5]
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]

 

# --- Job Vacancies (Kadrlar bo‘limi) ---
class JobVacancyViewSet(viewsets.ModelViewSet):
    serializer_class = JobVacancySerializer
    permission_classes = [IsHRUserOrReadOnly]

    def get_queryset(self):
        return JobVacancy.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# --- Statistic Data (Statistiklar) ---
class StatisticDataViewSet(viewsets.ModelViewSet):
    serializer_class = StatisticDataSerializer
    permission_classes = [ IsStatisticianOrReadOnly]

    def get_queryset(self):
        # Hamma ko‘ra oladi
        return StatisticData.objects.all()

    def perform_create(self, serializer):
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