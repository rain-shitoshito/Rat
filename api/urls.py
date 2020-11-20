from rest_framework import routers
from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views

app_name = 'api'

router = routers.DefaultRouter()
router.register('command', views.CommandViewSet)
router.register('recipient', views.BotNetViewSet)

router.urls.extend([
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
])