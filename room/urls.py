from django.urls import path
from . import views

app_name = "room"

urlpatterns = [
    #SCR-06 部屋作成
    path("create/", views.RoomCreateView.as_view(), name="create"),
    #SCR-07 部屋参加
    path("join/", views.RoomJoinView.as_view(), name="join"),
    #SCR-09 部屋画面（/room/3/ のように部屋のIDを付ける）
    path("<int:room_id>/", views.RoomView.as_view(), name="top"),
]
