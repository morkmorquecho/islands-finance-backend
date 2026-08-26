from django.urls import include, path
from .views import EmailUpdateAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

user_path = ([
    path('me/email/request-change', EmailUpdateAPIView.as_view(), name='request_update_email'),
    path('me/', include(router.urls)),

], 'user')