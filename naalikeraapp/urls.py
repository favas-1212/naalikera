from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', views.index, name='index'),
    path('nal/', views.nal, name='nal'),
    path('login/', views.login_view, name='login'),
    path('signup/<str:user_type>/', views.signup_view, name='signup'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('api/auth/register/', views.register, name='register'),
    path('api/auth/login/', views.login, name='login_api'),
    path('api/auth/verify-otp/', views.verify_otp, name='verify_otp_api'),
    path('api/auth/forgot-password/', views.forgot_password, name='forgot_password'),
    path('api/auth/logout/', views.logout, name='logout'),
    path('api/auth/refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/bypass-verification/', views.bypass_verification, name='bypass_verification'),
]