from django.urls import path
from . import views

app_name = 'room'

urlpatterns = [
    path('<int:room_id>/', views.RoomView.as_view(), name='top'),
    path('create/', views.RoomCreateView.as_view(), name='create'),
    # path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
]
