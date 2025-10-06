from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('update/', views.UserUpdateView.as_view(), name='user-update'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    
    # Utility endpoints
    path('check-email/', views.check_email_exists, name='check-email'),
    path('dashboard/', views.user_dashboard, name='user-dashboard'),
    path('login-history/', views.user_login_history, name='login-history'),
]
