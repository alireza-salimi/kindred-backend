from kindred.models import KindredMember
from .serializers import RetrieveUserSerializer, UserConfirmLoginSerializer, UserConfirmSignupSerializer, UserLogInSerializer, UserSignUpSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from kindred_backend.utils import get_tokens_for_user
from kindred.serializers import RetrieveKindredMemberSerializer


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


class UserLogInView(APIView):
    def post(self, request):
        serializer = UserLogInSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            otp = serializer.save()
            return Response(
                {
                    'message': _('OTP was sent to your phone number.'),
                    'otp': otp
                }
            )
class UserConfirmLoginView(APIView):
    def post(self, request):
        serializer = UserConfirmLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(
                {
                    'message': _('Your login proccess has been completed.'),
                    'tokens': get_tokens_for_user(user),
                    'user': RetrieveUserSerializer(user, context={'request': request}).data
                }
            )