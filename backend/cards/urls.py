from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardViewSet, LabelViewSet, search_users
from .auth_views import login_view, logout_view, check_auth, register_view, get_csrf_token

router = DefaultRouter()
router.register(r'cards', CardViewSet)
router.register(r'labels', LabelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/csrf/', get_csrf_token, name='csrf'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/check/', check_auth, name='check_auth'),
    path('auth/register/', register_view, name='register'),
    path('users/search/', search_users, name='search_users'),
]
