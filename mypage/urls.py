from django.urls import path
from . import views

app_name = "mypage"

urlpatterns = [
    #SCR-04 プロフィール（/mypage/）
    path("", views.ProfileView.as_view(), name="profile"),
    #SCR-05 ドライブ履歴詳細（/mypage/history/3/ のように履歴のIDを付ける）
    path("history/<int:history_id>/", views.HistoryDetailView.as_view(), name="history_detail"),
]
