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
    StatisticDataSerializerUz, StatisticDataSerializerRu, StatisticDataSerializerEn,
    LostItemRequestSerializerUz, LostItemRequestSerializerRu, LostItemRequestSerializerEn,
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
        serializer.save(created_by=self.request.user)


class NewsViewSetRu(viewsets.ModelViewSet):
    queryset = News.objects.all()
    permission_classes = [IsNewsEditorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializerRu
        return NewsSerializerRu

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class NewsViewSetEn(viewsets.ModelViewSet):
    queryset = News.objects.all()
    permission_classes = [IsNewsEditorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializerEn
        return NewsSerializerEn

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



# --- Statistic Data (Statistiklar) ---
class StatisticDataViewSetUz(viewsets.ModelViewSet):
    serializer_class = StatisticDataSerializerUz
    permission_classes = [ IsStatisticianOrReadOnly]

    def get_queryset(self):
        # Hamma ko‘ra oladi
        return StatisticData.objects.all()

    def perform_create(self, serializer):
        serializer.save()



class StatisticDataViewSetRu(viewsets.ModelViewSet):
    serializer_class = StatisticDataSerializerRu
    permission_classes = [IsStatisticianOrReadOnly]

    def get_queryset(self):
        return StatisticData.objects.all()

    def perform_create(self, serializer):
        serializer.save()


class StatisticDataViewSetEn(viewsets.ModelViewSet):
    serializer_class = StatisticDataSerializerEn
    permission_classes = [IsStatisticianOrReadOnly]

    def get_queryset(self):
        return StatisticData.objects.all()

    def perform_create(self, serializer):
        serializer.save()




class LostItemRequestCreateViewSetUz(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = LostItemRequest.objects.all()
    serializer_class = LostItemRequestSerializerUz
    permission_classes = [permissions.AllowAny]  



class LostItemRequestCreateViewSetRu(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = LostItemRequest.objects.all()
    serializer_class = LostItemRequestSerializerRu
    permission_classes = [permissions.AllowAny]


class LostItemRequestCreateViewSetEn(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = LostItemRequest.objects.all()
    serializer_class = LostItemRequestSerializerEn
    permission_classes = [permissions.AllowAny]




class LostItemRequestSupportViewSetUz(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LostItemRequest.objects.all().order_by('-created_at')
    serializer_class = LostItemRequestSerializerUz
    permission_classes = [IsAuthenticated, IsLostItemSupport]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class LostItemRequestSupportViewSetRu(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LostItemRequest.objects.all().order_by('-created_at')
    serializer_class = LostItemRequestSerializerRu
    permission_classes = [IsAuthenticated, IsLostItemSupport]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_ru']


class LostItemRequestSupportViewSetEn(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LostItemRequest.objects.all().order_by('-created_at')
    serializer_class = LostItemRequestSerializerEn
    permission_classes = [IsAuthenticated, IsLostItemSupport]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_en']



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