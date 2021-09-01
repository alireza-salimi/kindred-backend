from kindred_backend.utils import get_tokens_for_user
from kindred.models import Kindred, KindredMember, ShoppingItem
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from .serializers import ChangeKindredAdminSerializer, CreateKindredSerializer, CreateLocationSerializer, CreateShoppingItemSerializer, EditShoppingItemSerializer, InviteMemberSerializer, InvitedMemberConfirmSerializer, ListKindredMembersSerializer, ListLocationsSerializer, ListShoppingItemsSerializer, RemoveKindredMemberSerializer, RetrieveKindredMemberSerializer, RetrieveKindredSerializer, RetrieveLocationSerializer, RetrieveShoppingItemSerializer
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
                'location': RetrieveLocationSerializer(location, context={'request': request}).data
            })
    @action(detail=False, methods=['post'], url_path='last-locations', url_name='last-locations')
    def last_locations(self, request, **kwargs):
        serializer = ListLocationsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            kindred = serializer.save()
            locations = []
            for member in kindred.members.all():
                if member.user.locations.last():
                    locations.append(RetrieveLocationSerializer(member.user.locations.last(), context={'request': request}).data)
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
    def list(self, request):
        kindred = request.GET.get('kindred', None)
        serializer = ListShoppingItemsSerializer(data={'kindred': kindred}, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            shopping_items = serializer.save()
            return Response(RetrieveShoppingItemSerializer(shopping_items, many=True, context={'request': request}).data)


class kindredViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = CreateKindredSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            kindred = serializer.save()
            return Response({
                'message': 'Kindred was created successfully.',
                'kindred': RetrieveKindredSerializer(kindred, context={'request': request}).data
            })
    
    @action(detail=True, methods=['post'], url_path='invite', url_name='invite', permission_classes=[IsAuthenticated])
    def invite(self, request, **kwargs):
        serializer = InviteMemberSerializer(data={**request.data, 'kindred': kwargs['pk']}, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            invitation_code = serializer.save()
            return Response({
                'message': _("Invitation code was sent to the invited users's phone number."),
                'invitation_code': invitation_code
            })

    @action(detail=False, methods=['post'], url_path='confirm-invite', url_name='confirm-invite', permission_classes=[])
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

    @action(detail=True, methods=['get'], url_path='members', url_name='members')
    def list_members(self, request, **kwargs):
        try:
            kindred = Kindred.objects.get(pk=kwargs['pk'])
        except Kindred.DoesNotExist:
            return Response({
                'message': _("Kindred with given id doesn't exist.")
            },
            status=status.HTTP_404_NOT_FOUND
            )
        kindred_member = KindredMember.objects.filter(user=request.user, kindred=kindred)
        if not kindred_member:
            return Response({
                'message': _("You aren't member of this kindred.")
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ListKindredMembersSerializer(
            KindredMember.objects.filter(kindred=kindred),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='change-admin', url_name='change-admin')
    def change_admin(self, request, **kwargs):
        serializer = ChangeKindredAdminSerializer(
            data={'kindred': kwargs['pk'], **request.data}, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            new_admin = serializer.save()
            return Response(
                {
                    'message': _('Admin was changed successfully.'),
                    'kindred_member': RetrieveKindredMemberSerializer(new_admin, context={'request': request}).data
                }
            )
    
    @action(detail=True, methods=['post'], url_path='remove-member', url_name='remove-member')
    def remove_member(self, request, **kwargs):
        serializer = RemoveKindredMemberSerializer(
            data={'kindred': kwargs['pk'], **request.data}, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                'message': _('Kindred member was successfully removed from kindred.')
            })