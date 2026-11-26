from django.urls import path
from . import views

app_name = 'room'

urlpatterns = [
    path('create/', views.room_create_view, name='create'),   # SCR-06 部屋作成
    path('join/', views.room_join_view, name='join'),         # SCR-07 部屋参加
    path('<int:room_id>/', views.room_view, name='top'),      # SCR-09 部屋画面
]
