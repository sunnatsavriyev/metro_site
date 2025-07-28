from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    NewsViewSetUz, NewsViewSetRu, NewsViewSetEn,
    CommentViewSetUz, CommentViewSetRu, CommentViewSetEn,
    NewsLikeView,
    JobVacancyViewSetUz, JobVacancyViewSetRu, JobVacancyViewSetEn,
    StatisticDataViewSetUz, StatisticDataViewSetRu, StatisticDataViewSetEn,
    LostItemRequestCreateViewSetUz, LostItemRequestCreateViewSetRu, LostItemRequestCreateViewSetEn,
    LostItemRequestSupportViewSetUz, LostItemRequestSupportViewSetRu, LostItemRequestSupportViewSetEn,
    LatestNewsListViewUz, LatestNewsListViewRu, LatestNewsListViewEn,FoydalanuvchiStatistikaView
)

# Uzbek routes
router_uz = DefaultRouter()
router_uz.register(r'news/uz', NewsViewSetUz, basename='news-uz')
router_uz.register(r'comments/uz', CommentViewSetUz, basename='comments-uz')
router_uz.register(r'job-vacancies/uz', JobVacancyViewSetUz, basename='jobvacancies-uz')
router_uz.register(r'statistics/uz', StatisticDataViewSetUz, basename='statistics-uz')
router_uz.register(r'lost-item/request/uz', LostItemRequestCreateViewSetUz, basename='lost-item-create-uz')
router_uz.register(r'lost-item/support/uz', LostItemRequestSupportViewSetUz, basename='lost-item-support-uz')

# Russian routes
router_ru = DefaultRouter()
router_ru.register(r'news/ru', NewsViewSetRu, basename='news-ru')
router_ru.register(r'comments/ru', CommentViewSetRu, basename='comments-ru')
router_ru.register(r'job-vacancies/ru', JobVacancyViewSetRu, basename='jobvacancies-ru')
router_ru.register(r'statistics/ru', StatisticDataViewSetRu, basename='statistics-ru')
router_ru.register(r'lost-item/request/ru', LostItemRequestCreateViewSetRu, basename='lost-item-create-ru')
router_ru.register(r'lost-item/support/ru', LostItemRequestSupportViewSetRu, basename='lost-item-support-ru')

# English routes
router_en = DefaultRouter()
router_en.register(r'news/en', NewsViewSetEn, basename='news-en')
router_en.register(r'comments/en', CommentViewSetEn, basename='comments-en')
router_en.register(r'job-vacancies/en', JobVacancyViewSetEn, basename='jobvacancies-en')
router_en.register(r'statistics/en', StatisticDataViewSetEn, basename='statistics-en')
router_en.register(r'lost-item/request/en', LostItemRequestCreateViewSetEn, basename='lost-item-create-en')
router_en.register(r'lost-item/support/en', LostItemRequestSupportViewSetEn, basename='lost-item-support-en')

urlpatterns = [
    # Uzbek API endpoints
    path('', include(router_uz.urls)),

    # Russian API endpoints
    path('', include(router_ru.urls)),

    # English API endpoints
    path('', include(router_en.urls)),

    # Like endpoint (tilga bog‘liq emas)
    path('news/<int:pk>/like/', NewsLikeView.as_view(), name='news-like'),

    # JWT Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Session-based login/logout (Browsable API uchun)
    path('auth/session/', include('rest_framework.urls')),

    # dj-rest-auth (login/registration/email verification)
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    # Extra endpoints
    path('news/latest/uz', LatestNewsListViewUz.as_view(), name='latest-news'),
    path('news/latest/ru', LatestNewsListViewRu.as_view(), name='latest-news'),
    path('news/latest/en', LatestNewsListViewEn.as_view(), name='latest-news'),
    path('sayt_foydalanuvchilari/', FoydalanuvchiStatistikaView.as_view(), name='foydalanuvchi-statistika'),
]

