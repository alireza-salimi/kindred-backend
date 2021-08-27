from kindred.models import Kindred, KindredMember
import kindred_backend
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from .models import Message, DefaultMessage
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateMessageSerializer, RetrieveMessageSerializer, RetrieveChatMessageSerializer
from django.utils.translation import ugettext_lazy as _
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.db.models import Q


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateMessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            message = serializer.save()
            return Response({
                'message': _('Message was successfully sent.'),
                'message_obj': RetrieveMessageSerializer(message, context={'request': request}).data
            })


class ListChatMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        kindred_member = request.data.get('kindred_member', None)
        if not kindred_member:
            return Response({
                'message': _('kindred_member field is required.')
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        kindred_member = KindredMember.objects.filter(pk=request.data['kindred_member']).first()
        if not kindred_member:
            return Response({
                'message': _('There is no kindred member with this id.')
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        user = KindredMember.objects.filter(user=request.user, kindred=kindred_member.kindred.pk).first()
        if not user:
            return Response({
                'message': _("You aren't member of this kindred.")
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        messages = Message.objects.filter(
            Q(sent_from=user, sent_to=kindred_member) | Q(sent_from=kindred_member, sent_to=user)
        ).order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(messages, request)
        serializer = RetrieveChatMessageSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PreviewChatsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        kindred = request.data.get('kindred', None)
        if not kindred:
            return Response({
                'message': _('kindred field is required.')
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        kindred = Kindred.objects.filter(pk=kindred).first()
        if not kindred:
            return Response({
                'message': _('There is no kindred with this id.')
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        kindred_member = KindredMember.objects.filter(user=request.user, kindred=kindred).first()
        if not kindred_member:
            return Response({
                'message': _("You aren't member of this kindred.")
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        kindred_members = KindredMember.objects.filter(kindred=kindred).exclude(user=request.user)
        result = []
        for km in kindred_members:
            messages = Message.objects.filter(
                Q(sent_to=kindred_member, sent_from=km) | Q(sent_to=km, sent_from=kindred_member)
            )
            if messages:
                message = messages.order_by('-created_at').first()
                result.append(
                    RetrieveMessageSerializer(message, context={'request': request}).data
                )
        return Response(sorted(result, key=lambda x: x['created_at'], reverse=True))
