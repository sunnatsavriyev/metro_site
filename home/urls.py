from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    NewsViewSet,
    CommentViewSet,
    NewsLikeView,
    JobVacancyViewSet,
    StatisticDataViewSet,
    LostItemRequestCreateViewSet, 
    LostItemRequestSupportViewSet,
    LatestNewsListView,FoydalanuvchiStatistikaView
)

# Router viewset'lar uchun
router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'job-vacancies', JobVacancyViewSet, basename='jobvacancies')
router.register(r'statistics', StatisticDataViewSet, basename='statistics')
router.register(r'lost-item/request', LostItemRequestCreateViewSet, basename='lost-item-create')
router.register(r'lost-item/support', LostItemRequestSupportViewSet, basename='lost-item-support')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),

    # Like uchun alohida endpoint
    path('news/<int:pk>/like/', NewsLikeView.as_view(), name='news-like'),

    # JWT Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Session-based login/logout (browsable API uchun)
    path('auth/session/', include('rest_framework.urls')),

    # dj-rest-auth (login/registration/email verification)
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    path('news/latest/', LatestNewsListView.as_view(), name='latest-news'),
    path('sayt_foydalanuvchilari/', FoydalanuvchiStatistikaView.as_view(), name='foydalanuvchi-statistika'),
    
]
