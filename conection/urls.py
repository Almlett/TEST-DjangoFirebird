# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url, include
from .views import *

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'user_viewset', UserViewSet, base_name='User_Viewset')

urlpatterns = patterns(
    url(r'^home/$', home, name='home'),
)
urlpatterns += router.urls
