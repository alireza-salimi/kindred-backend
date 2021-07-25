from kindred.views import CreateLocationView, ListLocationsView
from django.urls import path


urlpatterns = [
    path('locations', CreateLocationView.as_view(), name='locations'),
    path('list-locations', ListLocationsView.as_view(), name='list-location')
]