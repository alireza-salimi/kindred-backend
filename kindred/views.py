from kindred.models import ShoppingItem
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CreateLocationSerializer, CreateShoppingItemSerializer, EditShoppingItemSerializer, ListLocationsSerializer, RetrieveLocationSerializer, RetrieveShoppingItemSerializer
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
