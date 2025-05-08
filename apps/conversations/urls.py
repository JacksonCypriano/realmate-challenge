from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
]
