from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    NewsViewSet,
    CommentViewSet,NewsImageViewSet,
    NewsLikeView, JobVacancyViewSet,
    JobVacancyRequestViewSet, 
    StatisticDataViewSetUz, StatisticDataViewSetRu, StatisticDataViewSetEn,
    LostItemRequestViewSet, FoydalanuvchiStatistikaView,
    LatestNewsListViewUz, LatestNewsListViewRu, LatestNewsListViewEn,
    MainNewsListViewUz, MainNewsListViewRu, MainNewsListViewEn,
    StatisticDataListView, CurrentUserView,
    UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView,
    Last6MonthsStatisticDataViewSet, TokenInfoView, TestPingView, APILoginView
)

router = DefaultRouter()
# Asosiy news endpoint
router.register(r'news', NewsViewSet, basename='news')
router.register(r'news-images', NewsImageViewSet, basename='news-images')

# Comments
router.register(r'comments', CommentViewSet, basename='comments')

# Jobs
router.register(r'job-vacancies', JobVacancyViewSet, basename='job-vacancies')

# Job vacancy requests
router.register(r'job-vacancy-requests', JobVacancyRequestViewSet, basename='job-vacancy-requests')

# Statistics
router.register(r'statistics/uz', StatisticDataViewSetUz, basename='statistics-uz')
router.register(r'statistics/ru', StatisticDataViewSetRu, basename='statistics-ru')
router.register(r'statistics/en', StatisticDataViewSetEn, basename='statistics-en')

# Lost items
router.register(r'lost-items', LostItemRequestViewSet, basename='lost-items')


# --- Manual paths for news translations ---
news_list_uz = NewsViewSet.as_view({'get': 'list_uz'})
news_list_ru = NewsViewSet.as_view({'get': 'list_ru'})
news_list_en = NewsViewSet.as_view({'get': 'list_en'})
news_detail_uz = NewsViewSet.as_view({'get': 'retrieve_uz'})
news_detail_ru = NewsViewSet.as_view({'get': 'retrieve_ru'})
news_detail_en = NewsViewSet.as_view({'get': 'retrieve_en'})

# --- Manual paths for job-vacancies translations ---
job_list_uz = JobVacancyViewSet.as_view({'get': 'list_uz'})
job_list_ru = JobVacancyViewSet.as_view({'get': 'list_ru'})
job_list_en = JobVacancyViewSet.as_view({'get': 'list_en'})
job_detail_uz = JobVacancyViewSet.as_view({'get': 'retrieve_uz'})
job_detail_ru = JobVacancyViewSet.as_view({'get': 'retrieve_ru'})
job_detail_en = JobVacancyViewSet.as_view({'get': 'retrieve_en'})


urlpatterns = [
    path('', include(router.urls)),

    # --- News translations ---
    path('news/uz/', news_list_uz, name='news-list-uz'),
    path('news/ru/', news_list_ru, name='news-list-ru'),
    path('news/en/', news_list_en, name='news-list-en'),
    path('news/uz/<int:pk>/', news_detail_uz, name='news-detail-uz'),
    path('news/ru/<int:pk>/', news_detail_ru, name='news-detail-ru'),
    path('news/en/<int:pk>/', news_detail_en, name='news-detail-en'),

    # --- JobVacancy translations ---
    path('job-vacancies/uz/<int:pk>/', job_detail_uz, name='job-detail-uz'),
    path('job-vacancies/ru/<int:pk>/', job_detail_ru, name='job-detail-ru'),
    path('job-vacancies/en/<int:pk>/', job_detail_en, name='job-detail-en'),

    # Likes
    path('news/<int:pk>/like/', NewsLikeView.as_view(), name='news-like'),

    # Statistics by lang
    path('statistics/<str:lang>/<int:year>/<int:period>/', StatisticDataListView.as_view()),
    path('statistics/last6months/<str:lang>/', Last6MonthsStatisticDataViewSet.as_view({'get': 'list'}), name='last6months-stats'),

    # Users CRUD
    path('users/', UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-detail'),

    # Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/session/', include('rest_framework.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    # Latest news by lang
    path('news/latest/uz', LatestNewsListViewUz.as_view(), name='latest-news-uz'),
    path('news/latest/ru', LatestNewsListViewRu.as_view(), name='latest-news-ru'),
    path('news/latest/en', LatestNewsListViewEn.as_view(), name='latest-news-en'),

    # Main news by lang
    path('news/main/uz', MainNewsListViewUz.as_view(), name='main-news-uz'),
    path('news/main/ru', MainNewsListViewRu.as_view(), name='main-news-ru'),
    path('news/main/en', MainNewsListViewEn.as_view(), name='main-news-en'),

    # Extra
    path('api/me/', CurrentUserView.as_view(), name='current-user'),
    path('sayt_foydalanuvchilari/', FoydalanuvchiStatistikaView.as_view(), name='foydalanuvchi-statistika'),
    path('token-info/', TokenInfoView.as_view(), name='token-info'),
    path("test/", TestPingView.as_view(), name="test-ping"),
    path('auth/login/', APILoginView.as_view(), name='api_login'),
]
