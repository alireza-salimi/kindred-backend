from kindred.views import LocationViewSet, ShoppingItemViewSet, kindredViewSet
from django.urls import path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('locations', LocationViewSet, basename='location')
router.register('shopping-items', ShoppingItemViewSet, basename='shopping-item')
router.register('', kindredViewSet, basename='kindred')
urlpatterns = [

] + router.urls
