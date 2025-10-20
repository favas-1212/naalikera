from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nal/', views.nal, name='nal'),
    path('hire-now/', views.hire_now, name='hire_now'),
    path('find-workers/', views.find_workers, name='find_workers'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('signup/<str:user_type>/', views.signup_view, name='signup'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    # API views
    path('api/register/', views.register, name='register'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/login/confirm-otp/', views.confirm_login, name='api_confirm_login'),
    path('api/verify-otp/', views.verify_otp, name='api_verify_otp'),
    path('api/forgot-password/', views.forgot_password, name='forgot_password'),
    path('api/logout/', views.logout, name='api_logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/bypass-verification/', views.bypass_verification, name='bypass_verification'),
]