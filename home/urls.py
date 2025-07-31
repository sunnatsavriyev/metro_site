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
    JobVacancyRequestViewSetUz, JobVacancyRequestViewSetRu, JobVacancyRequestViewSetEn,
    StatisticDataViewSetUz, StatisticDataViewSetRu, StatisticDataViewSetEn,
    LostItemRequestViewSet,FoydalanuvchiStatistikaView, LatestNewsListViewUz, LatestNewsListViewRu, LatestNewsListViewEn,
    StationViewSet
)


router = DefaultRouter()
# News / Comments / Vacancies / Statistics
router.register(r'news/uz', NewsViewSetUz, basename='news-uz')
router.register(r'news/ru', NewsViewSetRu, basename='news-ru')
router.register(r'news/en', NewsViewSetEn, basename='news-en')
router.register(r'comments/uz', CommentViewSetUz, basename='comments-uz')
router.register(r'comments/ru', CommentViewSetRu, basename='comments-ru')
router.register(r'comments/en', CommentViewSetEn, basename='comments-en')
router.register(r'job-vacancies/uz', JobVacancyViewSetUz, basename='job-vacancies-uz')
router.register(r'job-vacancies/ru', JobVacancyViewSetRu, basename='job-vacancies-ru')
router.register(r'job-vacancies/en', JobVacancyViewSetEn, basename='job-vacancies-en')
router.register(r'job-vacancy-requests/uz', JobVacancyRequestViewSetUz, basename='job-vacancy-requests-uz')
router.register(r'job-vacancy-requests/ru', JobVacancyRequestViewSetRu, basename='job-vacancy-requests-ru')
router.register(r'job-vacancy-requests/en', JobVacancyRequestViewSetEn, basename='job-vacancy-requests-en')
router.register(r'statistics/uz', StatisticDataViewSetUz, basename='statistics-uz')
router.register(r'statistics/ru', StatisticDataViewSetRu, basename='statistics-ru')
router.register(r'statistics/en', StatisticDataViewSetEn, basename='statistics-en')
router.register(r'stations', StationViewSet, basename='stations')

# Lost items
router.register(r'lost-items', LostItemRequestViewSet, basename='lost-items')

urlpatterns = [
    # Uzbek API endpoints

    path('', include(router.urls)),

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

