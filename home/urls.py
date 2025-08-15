from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    NewsViewSet,
    CommentViewSetUz, CommentViewSetRu, CommentViewSetEn,
    NewsLikeView, JobVacancyViewSet,
    JobVacancyRequestViewSetUz, JobVacancyRequestViewSetRu, JobVacancyRequestViewSetEn,
    StatisticDataViewSetUz, StatisticDataViewSetRu, StatisticDataViewSetEn,
    LostItemRequestViewSet, FoydalanuvchiStatistikaView,
    LatestNewsListViewUz, LatestNewsListViewRu, LatestNewsListViewEn,
    MainNewsListViewUz, MainNewsListViewRu, MainNewsListViewEn,
    StatisticDataListView, CurrentUserView,
    UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView,
    Last6MonthsStatisticDataViewSet, TokenInfoView
)

router = DefaultRouter()
# Asosiy news endpoint
router.register(r'news', NewsViewSet, basename='news')

# Comments
router.register(r'comments/uz', CommentViewSetUz, basename='comments-uz')
router.register(r'comments/ru', CommentViewSetRu, basename='comments-ru')
router.register(r'comments/en', CommentViewSetEn, basename='comments-en')

# Jobs
router.register(r'job-vacancies', JobVacancyViewSet, basename='job-vacancies')

# Job vacancy requests
router.register(r'job-vacancy-requests/uz', JobVacancyRequestViewSetUz, basename='job-vacancy-requests-uz')
router.register(r'job-vacancy-requests/ru', JobVacancyRequestViewSetRu, basename='job-vacancy-requests-ru')
router.register(r'job-vacancy-requests/en', JobVacancyRequestViewSetEn, basename='job-vacancy-requests-en')

# Statistics
router.register(r'statistics/uz', StatisticDataViewSetUz, basename='statistics-uz')
router.register(r'statistics/ru', StatisticDataViewSetRu, basename='statistics-ru')
router.register(r'statistics/en', StatisticDataViewSetEn, basename='statistics-en')

# Lost items
router.register(r'lost-items', LostItemRequestViewSet, basename='lost-items')



urlpatterns = [
    path('', include(router.urls)),

    

    # Statistics by lang
    path('statistics/<str:lang>/<int:year>/<int:period>/', StatisticDataListView.as_view()),

    # Users CRUD
    path('users/', UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-detail'),

    # Likes
    path('news/<int:pk>/like/', NewsLikeView.as_view(), name='news-like'),

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
    path('statistics/last6months/<str:lang>/', Last6MonthsStatisticDataViewSet.as_view({'get': 'list'}), name='last6months-stats'),
    path('token-info/', TokenInfoView.as_view(), name='token-info'),
]+ router.urls
