from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register_success/', views.RegisterSuccessView.as_view(), name='register_success'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
]