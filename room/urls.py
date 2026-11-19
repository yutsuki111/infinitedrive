from django.urls import path
from . import views

app_name = 'room'

urlpatterns = [
    path('create/', views.RoomCreateView.as_view(), name='create'),
    # RoomView name='room'
    # path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
]
