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
    # pylint: disable=no-self-use
    def list(self, request):
        """
            Metodo para mostrar la lista
        """
        name = request.GET.get('nombre')
        result = []
        if name:
            name = name.upper()
            con = fdb.connect(host='localhost',
                          port=3050,
                          database='/home/michel/Downloads/EXCEL.FDB',
                          user='SYSDBA',
                          password='masterkey')
            cursor = con.cursor()
            cursor.execute("""SELECT ARTICULOS.ARTICULO_ID, LINEAS_ARTICULOS.NOMBRE AS LINEA_ARTICULO,
                            ARTICULOS.NOMBRE  FROM ARTICULOS  JOIN LINEAS_ARTICULOS ON 
                            ARTICULOS.LINEA_ARTICULO_ID = LINEAS_ARTICULOS.LINEA_ARTICULO_ID 
                            where ARTICULOS.NOMBRE like '%{}%' """.format(name))
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
            return Response(result)
        else:
            return Response('Error en parametros recibidos', status=204)

    # pylint: disable=no-self-use
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
            cursor.execute("""SELECT ARTICULOS.ARTICULO_ID, LINEAS_ARTICULOS.NOMBRE AS
                            LINEA_ARTICULO, ARTICULOS.NOMBRE  FROM ARTICULOS 
                            JOIN LINEAS_ARTICULOS ON 
                            ARTICULOS.LINEA_ARTICULO_ID = LINEAS_ARTICULOS.LINEA_ARTICULO_ID 
                            where ARTICULOS.ARTICULO_ID like '{}' """.format(pk))
            
            record = cursor.fetchone()
            if record:
                columns = [column[0] for column in cursor.description]
                cursor.close()
                result = dict(zip(columns, record))
            else:
                return Response('ID no encontrado', status=404)
        return Response(result)

# pylint: disable=unused-argument
def home(request):
    """
        go to home
    """
    return Response([])
