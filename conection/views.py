"""
    View Conection
"""
import fdb
from rest_framework import viewsets
from rest_framework.response import Response

class ArticulosViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    QUERY_ARTICULOS = """SELECT
                ARTICULOS.ARTICULO_ID, 
                LINEAS_ARTICULOS.NOMBRE AS LINEA_ARTICULO, 
                ARTICULOS.NOMBRE,
                GRUPOS_LINEAS.NOMBRE AS GRUPO_LINEAS
            FROM ARTICULOS  
            JOIN LINEAS_ARTICULOS ON ARTICULOS.LINEA_ARTICULO_ID = LINEAS_ARTICULOS.LINEA_ARTICULO_ID
            JOIN GRUPOS_LINEAS ON LINEAS_ARTICULOS.GRUPO_LINEA_ID = GRUPOS_LINEAS.GRUPO_LINEA_ID """

    def list(self, request):
        """
            Metodo para mostrar la lista
        """
        name = request.GET.get('nombre')
        result = []
        if name:
            if len(name) < 3:
                return Response({'result':'La cantidad minima de caracteres es 4'}, status=400)
            name = name.upper()
            con = fdb.connect(host='localhost',
                              port=3050,
                              database='/home/michel/Downloads/EXCEL.FDB',
                              user='SYSDBA',
                              password='masterkey')
            cursor = con.cursor()
            cursor.execute(self.QUERY_ARTICULOS + "where ARTICULOS.NOMBRE like '%{}%'".format(name))
            records = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            cursor.close()
            data = []
            for row in records:
                data.append(dict(zip(columns, row)))
            try:
                for item in range(0, 35):
                    result.append(data[item])
            # pylint: disable=broad-except
            except Exception:
                pass
            if not data:
                return Response({'result':'Articulo no encontrado'}, status=404)
            return Response({'data':result}, status=200)
        return Response({'result':'Error en parametros recibidos'}, status=200)

    # pylint: disable=unused-argument
    # pylint: disable=invalid-name
    def retrieve(self, request, pk=None):
        """
            Get
        """
        result = []
        print pk
        if pk:
            con = fdb.connect(host='localhost',
                              port=3050,
                              database='/home/michel/Downloads/EXCEL.FDB',
                              user='SYSDBA',
                              password='masterkey')
            cursor = con.cursor()
            cursor.execute(self.QUERY_ARTICULOS + "where ARTICULOS.ARTICULO_ID like '{}'".format(pk))
            record = cursor.fetchone()
            if record:
                columns = [column[0] for column in cursor.description]
                cursor.close()
                result = dict(zip(columns, record))
            else:
                return Response({'result':'ID no encontrado'}, status=404)
        return Response(result)

# pylint: disable=unused-argument
def home(request):
    """
        go to home
    """
    return Response([])
