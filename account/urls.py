from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from account import views

router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('user/', views.UserView.as_view(), name='login'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),

    path('change-password', views.ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    
    path('current-user/', views.CurrentUserDetailView.as_view(), name='current_user_detail'),

    path('', include(router.urls)),
]