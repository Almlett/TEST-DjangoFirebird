from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

#from rest_framework import viewsets
from rest_framework import viewsets
from rest_framework.response import Response

class UserViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    def list(self, request):
        #queryset = User.objects.all()
        #serializer = UserSerializer(queryset, many=True)
        data = {}
        data['id'] = 1
        data['Nombre'] = "Nombre"
        return Response(data)


    def retrieve(self, request, pk=None):
        #queryset = User.objects.all()
        #user = get_object_or_404(queryset, pk=pk)
        #serializer = UserSerializer(user)
        return []

def home(request):
    return render(request, 'home.html', {})

