import fdb
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
        name = request.GET.get('nombre')
        if name:
            name = name.upper()
        con = fdb.connect(host='localhost', port=3050, database='/home/michel/Downloads/EXCEL.FDB', user='SYSDBA', password='masterkey')
        cursor = con.cursor()
        cursor.execute("SELECT ARTICULOS.ARTICULO_ID, LINEAS_ARTICULOS.NOMBRE AS LINEA_ARTICULO, ARTICULOS.NOMBRE  FROM ARTICULOS  JOIN LINEAS_ARTICULOS ON ARTICULOS.LINEA_ARTICULO_ID = LINEAS_ARTICULOS.LINEA_ARTICULO_ID where ARTICULOS.NOMBRE like '%{}%' ".format(name))
        records = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        cursor.close()
        data = []
        
        for row in records:
            data.append(dict(zip(columns, row)))

        result = []
        try:
            for item in range(0,35):
                result.append(data[item])
        except Exception:
            pass
        
        return Response(result)


    def retrieve(self, request, pk=None):
        #queryset = User.objects.all()
        #user = get_object_or_404(queryset, pk=pk)
        #serializer = UserSerializer(user)
        return []

def home(request):
    return render(request, 'home.html', {})

