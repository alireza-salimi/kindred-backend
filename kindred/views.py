from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CreateLocationSerializer, ListLocationsSerializer, RetrieveLocationSerializer
from rest_framework.permissions import IsAuthenticated


class CreateLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateLocationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            location = serializer.save()
            return Response({
                'message': 'Location was created successfully.',
                'location': RetrieveLocationSerializer(location, context={'reuqest': request}).data
            })


class ListLocationsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ListLocationsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            kindred = serializer.save()
            locations = []
            for member in kindred.members.all():
                locations.append(RetrieveLocationSerializer(member.locations.last(), context={'request': request}).data)
            return Response(locations)