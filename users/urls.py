from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('sign-up', UserSignUpView.as_view(), name='sign-up'),
    path('confirm-signup', UserConfirmSingupView.as_view(), name='confirm-signup'),
    path('complete-profile', UserCompleteProfileView.as_view(), name='complete-profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
