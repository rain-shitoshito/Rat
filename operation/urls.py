from django.urls import path
from . import views

app_name = 'operation'

urlpatterns = [
    path('users/<int:pk>/', views.Top.as_view(), name='top'),
    path('api_manual', views.Api.as_view(), name='api'),
]