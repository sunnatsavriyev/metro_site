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
    StatisticDataListView, CurrentUserView,
    UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView,
    Last6MonthsStatisticDataViewSet, TokenInfoView, TestPingView, APILoginView,
    AnnouncementViewSet,AnnouncementCommentViewSet,AnnouncementLikeToggleView,AnnouncementLikeCountView,
    KorrupsiyaViewSet, KorrupsiyaCommentViewSet, KorrupsiyaLikeToggleView, KorrupsiyaLikeCountView,SimpleUserViewSet
)

router = DefaultRouter()
# Asosiy news endpoint
# router.register(r'news', NewsViewSet, basename='news')
router.register(r'news-images', NewsImageViewSet, basename='news-images')

# Comments
router.register(r'comments', CommentViewSet, basename='comments')

# Jobs
# router.register(r'job-vacancies', JobVacancyViewSet, basename='job-vacancies')

# Job vacancy requests
router.register(r'job-vacancy-requests', JobVacancyRequestViewSet, basename='job-vacancy-requests')

# Statistics
router.register(r'statistics/uz', StatisticDataViewSetUz, basename='statistics-uz')
router.register(r'statistics/ru', StatisticDataViewSetRu, basename='statistics-ru')
router.register(r'statistics/en', StatisticDataViewSetEn, basename='statistics-en')

# Lost items
router.register(r'lost-items', LostItemRequestViewSet, basename='lost-items')
# router.register(r'announcements', AnnouncementViewSet, basename='announcements')
router.register(
    r'announcement-comments',
    AnnouncementCommentViewSet,
    basename='announcement-comments'
)

router.register(r'simpleuser', SimpleUserViewSet, basename='simpleuser')
router.register(
    r'korrupsiya-comments',
    KorrupsiyaCommentViewSet,
    basename='korrupsiya-comments'
)
# --- Manual paths for news translations ---
news_actions = NewsViewSet.as_view({'get': 'list', 'post': 'create'})
news_detail_actions = NewsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

job_actions = JobVacancyViewSet.as_view({'get': 'list', 'post': 'create'})
job_detail_actions = JobVacancyViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})


announcement_list = AnnouncementViewSet.as_view({'get': 'list', 'post': 'create'})
announcement_detail = AnnouncementViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'})

korrupsiya_list = KorrupsiyaViewSet.as_view({'get': 'list', 'post': 'create'})
korrupsiya_detail = KorrupsiyaViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'})


urlpatterns = [
    path('', include(router.urls)),

    # --- News translations ---
    path('news/<str:lang>/', news_actions, name='news-lang-list'),
    path('news/<str:lang>/<int:pk>/', news_detail_actions, name='news-lang-detail'),
    
    # Jobs
    path('job-vacancies/<str:lang>/', job_actions, name='job-lang-list'),
    path('job-vacancies/<str:lang>/<int:pk>/', job_detail_actions, name='job-lang-detail'),

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


    # Extra
    path('api/me/', CurrentUserView.as_view(), name='current-user'),
    path('sayt_foydalanuvchilari/', FoydalanuvchiStatistikaView.as_view(), name='foydalanuvchi-statistika'),
    path('token-info/', TokenInfoView.as_view(), name='token-info'),
    path("test/", TestPingView.as_view(), name="test-ping"),
    path('auth/login/', APILoginView.as_view(), name='api_login'),
    
    
    path('announcements/<str:lang>/', announcement_list),
    path('announcements/<str:lang>/<int:pk>/', announcement_detail),
    
    
    path(
        'announcements/<int:pk>/like/',
        AnnouncementLikeToggleView.as_view(),
        name='announcement-like-toggle'
    ),
    path(
        'announcements/<int:pk>/like-count/',
        AnnouncementLikeCountView.as_view(),
        name='announcement-like-count'
    ),
    
    path('korrupsiya/<str:lang>/', korrupsiya_list),
    path('korrupsiya/<str:lang>/<int:pk>/', korrupsiya_detail),
    path(
        'korrupsiya/<int:pk>/like/',
        KorrupsiyaLikeToggleView.as_view(),
        name='korrupsiya-like-toggle'
    ),
    path(
        'korrupsiya/<int:pk>/like-count/',
        KorrupsiyaLikeCountView.as_view(),
        name='korrupsiya-like-count'
    ),
]
