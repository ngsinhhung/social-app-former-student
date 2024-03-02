from django.urls import include, path
from rest_framework import routers

from SocialApp import views

r = routers.DefaultRouter()
r.register(r'account', views.AccountViewSet)
r.register(r'user', views.UserViewSet)

urlpatterns = [
    path('', include(r.urls))
]