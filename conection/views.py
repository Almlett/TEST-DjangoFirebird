"""
    View Conection
"""
import fdb
from rest_framework import viewsets
from rest_framework.response import Response

class UserViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    def list(self, request):
        """
            Metodo para mostrar la lista
        """
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
            for item in range(0, 35):
                result.append(data[item])
        except Exception:
            pass
        return Response(result)

def home(request):
    """
        go to home
    """
    print request
    return Response([])
