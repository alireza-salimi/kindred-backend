from .serializers import RetrieveUserSerializer, UserCompleteProfileSerializer, UserConfirmSignupSerializer, UserSignUpSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from kindred_backend.utils import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated


class UserSignUpView(APIView):
    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            otp = serializer.save()
            return Response({
                'message': _('OTP was sent to your phone number.'),
                'otp': otp
            })


class UserConfirmSingupView(APIView):
    def post(self, request):
        serializer = UserConfirmSignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(
                {
                    'message': _('Your signup process has been completed.'),
                    'tokens': get_tokens_for_user(user),
                    'user': RetrieveUserSerializer(user, context={'request': request}).data
                }
            )


class UserCompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserCompleteProfileSerializer(request.user, request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({
                'message': _('User profile was completed successfully.'),
                'user': RetrieveUserSerializer(user, context={'request': request}).data
            })


class UserDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = RetrieveUserSerializer(user, context={'request': request})
        return Response(serializer.data)
