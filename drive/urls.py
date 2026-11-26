from django.urls import path
from . import views

app_name = 'drive'

urlpatterns = [
    # ガチャを引く／もう一度引く（部屋画面のボタンから POST される）
    path('gacha/', views.gacha_view, name='gacha'),
]
