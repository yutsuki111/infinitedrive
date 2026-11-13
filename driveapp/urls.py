from django.urls import path
from . import views

app_name = 'driveapp'

urlpatterns = [
    # --- フロント①担当（SCR-01〜05：認証・ホーム・履歴） ---
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('history/detail/', views.history_detail_view, name='history_detail'),

    # --- フロント②担当（SCR-06〜09：部屋管理・役割・メイン部屋画面） ---
    path('room/create/', views.room_create_view, name='room_create'),
    path('room/join/', views.room_join_view, name='room_join'),
    path('room/role/', views.role_select_view, name='role_select'),
    path('room/', views.room_view, name='room'),

    # --- フロント③担当（SCR-10〜14：評価・リザルト・電卓・共有・マスタ管理） ---
    path('drive/evaluation/', views.evaluation_view, name='evaluation'),
    path('drive/result/', views.result_view, name='result'),
    path('drive/calculator/', views.calculator_view, name='calculator'),
    path('drive/share/', views.share_view, name='share'),
    path('master/', views.master_manage_view, name='master_manage'),
]