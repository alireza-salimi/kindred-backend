from kindred_backend.utils import get_tokens_for_user
from kindred.models import ShoppingItem
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from .serializers import CreateLocationSerializer, CreateShoppingItemSerializer, EditShoppingItemSerializer, InviteMemberSerializer, InvitedMemberConfirmSerializer, ListLocationsSerializer, RetrieveKindredMemberSerializer, RetrieveLocationSerializer, RetrieveShoppingItemSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from rest_framework import status
from django.utils.translation import ugettext_lazy as _


class LocationViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, **kwargs):
        serializer = CreateLocationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            location = serializer.save()
            return Response({
                'message': _('Location was created successfully.'),
                'location': RetrieveLocationSerializer(location, context={'reuqest': request}).data
            })
    @action(detail=False, methods=['post'], url_path='last-locations', url_name='last-locations')
    def last_locations(self, request, **kwargs):
        serializer = ListLocationsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            kindred = serializer.save()
            locations = []
            for member in kindred.members.all():
                locations.append(RetrieveLocationSerializer(member.locations.last(), context={'request': request}).data)
            return Response(locations)


class ShoppingItemViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, **kwargs):
        serializer = CreateShoppingItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            shopping_item = serializer.save()
            return Response(
                {
                    'message': _('Shopping item was created successfully.'),
                    'shopping_item': RetrieveShoppingItemSerializer(shopping_item, context={'request': request}).data
                }
            )
    
    def partial_update(self, request, **kwargs):
        try:
            shopping_item = ShoppingItem.objects.get(pk=kwargs['pk'])
        except ShoppingItem.DoesNotExist:
            return Response(
                {
                    'message': _('There is no shopping item with this id.')
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EditShoppingItemSerializer(shopping_item, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            shopping_item = serializer.save()
            return Response(
                {
                    'message': _('Shopping item was edited successfully.'),
                    'shopping_item': RetrieveShoppingItemSerializer(shopping_item, context={'request': request}).data
                }
            )


class kindredViewSet(ViewSet):
    @action(detail=True, methods=['post'], url_path='invite', url_name='invite', permission_classes=[IsAuthenticated])
    def invite(self, request, **kwargs):
        serializer = InviteMemberSerializer(data={**request.data, 'kindred': kwargs['pk']}, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            otp = serializer.save()
            return Response({
                'message': _("OTP was sent to the invited users's phone number."),
                'otp': otp
            })

    @action(detail=False, methods=['post'], url_path='confirm-invite', url_name='confirm-invite')
    def confirm_invite(self, request):
        serializer = InvitedMemberConfirmSerializer(data=request.data, context={'request'})
        if serializer.is_valid(raise_exception=True):
            kindred_member = serializer.save()
            return Response(
                {
                    'message': _('Your signup process has been completed.'),
                    'tokens': get_tokens_for_user(kindred_member.user),
                    'kindred_member': RetrieveKindredMemberSerializer(kindred_member, context={'request': request}).data
                }
            )