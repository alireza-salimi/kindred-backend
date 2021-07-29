from kindred.views import LocationViewSet, ShoppingItemViewSet
from django.urls import path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('locations', LocationViewSet, basename='location')
router.register('shopping-items', ShoppingItemViewSet, basename='shopping-item')
urlpatterns = [

] + router.urls
