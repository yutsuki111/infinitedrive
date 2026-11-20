from django.urls import path
from . import views

app_name = 'master'

urlpatterns = [
    # SCR-14 マスタ管理（/master/）
    path('', views.manage_view, name='manage'),
]
