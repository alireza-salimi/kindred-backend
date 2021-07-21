from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('sign-up', UserSignUpView.as_view(), name='sign-up'),
    path('confirm-signup', UserConfirmSingupView.as_view(), name='confirm-signup'),
    path('log-in', UserLogInView.as_view(), name='log-in'),
    path('confirm-login', UserConfirmLoginView.as_view(), name='confirm-login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
