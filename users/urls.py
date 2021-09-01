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
    path('profile', UserDataView.as_view(), name='user-data'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
