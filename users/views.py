from .serializers import UserConfirmSignupSerializer, UserSignUpSerializer
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
            kindred_member = serializer.save()
            return Response(
                {
                    'message': _('Your signup process has been completed.'),
                    'tokens': get_tokens_for_user(kindred_member.user),
                    'kindred_member': RetrieveKindredMemberSerializer(kindred_member, context={'request': request}).data
                }
            )
