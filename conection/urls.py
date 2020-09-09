# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url, include
from .views import ArticulosViewSet, ClientesViewSet, DoctosViewSet, home

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'articulos', ArticulosViewSet, base_name='articulos_vs')
router.register(r'clientes', ClientesViewSet, base_name='clientes_vs')
router.register(r'doctos', DoctosViewSet, base_name='doctos_vs')



urlpatterns = patterns(
    url(r'^home/$', home, name='home'),
)
urlpatterns += router.urls
