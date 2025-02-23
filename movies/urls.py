from django.urls import path, include
from movies import views
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)
from rest_framework import routers
from .middlewares import get_request_count, reset_request_count


router = routers.DefaultRouter()
router.register(r'collection', views.CollectionViewSet, basename='collections')

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('movies/', views.list_movies, name='movies-list'),
    path('', include(router.urls)),
    path('request-count/', get_request_count, name='get_request_count'),
    path('request-count/reset/', reset_request_count, name='reset_request_count'),
]