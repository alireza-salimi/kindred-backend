from django.urls import path
from .views import PreviewChatsView, SendMessageView, ListChatMessagesView, DefaultMessageViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('default-messages', DefaultMessageViewSet, basename='default-message')

urlpatterns = [
    path('send-message', SendMessageView.as_view(), name='send-message'),
    path('chat-messages', ListChatMessagesView.as_view(), name='chat-messages'),
    path('chats-preview', PreviewChatsView.as_view(), name='chats-preview')
] + router.urls
