#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    View Conection
"""
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from datetime import datetime
import fdb

# pylint: disable=unused-argument
def home(request):
    """
        go to home
    """
    return Response([])

class PaginatedListView(ListAPIView):
    
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100

class ArticulosViewSet(viewsets.ViewSet):
    """
    Articulos viewset
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
                return Response({'result':'La cantidad minima de caracteres es 3'}, status=400)
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
            result = []
            for row in records:
                result.append(dict(zip(columns, row)))
            #try:
            #    for item in range(0, 70):
            #        result.append(data[item])
            #except Exception:
            #    pass
            if not result:
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
        if not pk.isdigit():
            return Response({'result':'El ID tiene que ser un numérico'}, status=404)
        if pk:
            con = fdb.connect(host='localhost',
                              port=3050,
                              database='/home/michel/Downloads/EXCEL.FDB',
                              user='SYSDBA',
                              password='masterkey')
            cursor = con.cursor()
            cursor.execute(self.QUERY_ARTICULOS +
                           "where ARTICULOS.ARTICULO_ID like '{}'".format(pk))
            record = cursor.fetchone()
            if record:
                columns = [column[0] for column in cursor.description]
                cursor.close()
                result = dict(zip(columns, record))
            else:
                return Response({'result':'ID no encontrado'}, status=404)
        return Response(result)

class ClientesViewSet(viewsets.ViewSet):
    """
        Clientes viewset
    """
    QUERY_CLIENTES = """SELECT
                        CLIENTES.CLIENTE_ID,
                        CLIENTES.NOMBRE
                     FROM CLIENTES """

    def create(self, request):
        """
            Post
        """
        post_data = dict(request.data)
        data = self.validate_client(post_data)
        columns = data['columns_formated']
        values = data['values']
        missing = data['missing']
        wrong = data['wrong']
        if missing:
            return Response({'result': {'Campos faltantes': missing}}, status=400)
        if wrong:
            return Response({'result': wrong}, status=400)
        with fdb.connect(host = 'localhost',
                         port = 3050,
                         database = '/home/michel/Downloads/EXCEL.FDB',
                         user = 'SYSDBA',
                         password = 'masterkey') as con:
            query = "INSERT INTO CLIENTES ({}) VALUES {};".format(columns,values)
            cursor = con.cursor()
            try:
                cursor.execute(query)
                con.commit()
                cursor.close()
                select_cursor = con.cursor()
                select_cursor.execute("SELECT * FROM CLIENTES ORDER BY CLIENTE_ID DESC")
                client = select_cursor.fetchone()
                columns = [column[0] for column in select_cursor.description]
                select_cursor.close()
                con.close()
                if client:
                    result = dict(zip(columns, client))
                    return Response({'result':result}, status=200)
                return Response({'result':'ID no encontrado'}, status=404)
            except fdb.Error, e:
                try:
                    return Response({'result': e.args[0]}, status=400)
                except IndexError:
                    return Response({'result': "MySQL Error: %s" % str(e)}, status=400)

    def update(self, request, pk=None):
        """
        put
        """
        put_data = dict(request.data)
        columns = put_data.keys()
        obligatorios = ["NOMBRE",
                        "SUJETO_IEPS",
                        "DIFERIR_CFDI_COBROS",
                        "LIMITE_CREDITO",
                        "MONEDA_ID",
                        "COND_PAGO_ID"]
        missing = []
        for element in obligatorios:
            if not element in columns or put_data[element][0] in [".",""," ", "  "]:
                missing.append(element)

        if missing:
            return Response({'result': {'Campos faltantes': missing}}, status=400)

        fields = self.fields_updated(put_data)
        if fields['wrong']:
            return Response({'result': fields['wrong']}, status=400)

        with fdb.connect(host = 'localhost',
                         port = 3050,
                         database = '/home/michel/Downloads/EXCEL.FDB',
                         user = 'SYSDBA',
                         password = 'masterkey') as con:
            query = """UPDATE CLIENTES SET {}
                       WHERE CLIENTES.CLIENTE_ID LIKE '{}'""".format(fields['data'], pk)
            try:
                cursor = con.cursor()
                cursor.execute(query)
                con.commit()
                cursor.close()

                select_cursor = con.cursor()
                select_cursor.execute("""SELECT * FROM CLIENTES
                                        where CLIENTES.CLIENTE_ID like '{}'""".format(pk))
                client = select_cursor.fetchone()
                columns = [column[0] for column in select_cursor.description]
                select_cursor.close()
                con.close()
                if client:
                    result = dict(zip(columns, client))
                    return Response({'result':result}, status=200)
                return Response({'result':'ID no encontrado'}, status=404)
            except fdb.Error, e:
                try:
                    return Response({'result': e.args[0]}, status=400)
                except IndexError:
                    return Response({'result': "MySQL Error: %s" % str(e)}, status=400)

    def partial_update(self, request, pk=None):
        """
        patch
        """
        patch_data = dict(request.data)
        fields = self.fields_updated(patch_data)
        if fields['wrong']:
            return Response({'result': fields['wrong']}, status=400)

        with fdb.connect(host = 'localhost',
                         port = 3050,
                         database = '/home/michel/Downloads/EXCEL.FDB',
                         user = 'SYSDBA',
                         password = 'masterkey') as con:
            query = """UPDATE CLIENTES SET {}
                       WHERE CLIENTES.CLIENTE_ID LIKE '{}'""".format(fields['data'], pk)
            try:
                cursor = con.cursor()
                cursor.execute(query)
                con.commit()
                cursor.close()

                select_cursor = con.cursor()
                select_cursor.execute("""SELECT * FROM CLIENTES
                                         where CLIENTES.CLIENTE_ID like '{}'""".format(pk))
                client = select_cursor.fetchone()
                columns = [column[0] for column in select_cursor.description]
                select_cursor.close()
                con.close()
                if client:
                    result = dict(zip(columns, client))
                    return Response({'result':result}, status=200)
                return Response({'result':'ID no encontrado'}, status=404)
            except fdb.Error, e:
                try:
                    return Response({'result': e.args[0]}, status=400)
                except IndexError:
                    return Response({'result': "MySQL Error: %s" % str(e)}, status=400)

    def list(self, request):
        """
            Metodo para mostrar la lista
        """
        name = request.GET.get('nombre')
        result = []
        if name:
            if len(name) < 3:
                return Response({'result':'La cantidad minima de caracteres es 3'}, status=400)
            name = name.upper()
            con = fdb.connect(host='localhost',
                              port=3050,
                              database='/home/michel/Downloads/EXCEL.FDB',
                              user='SYSDBA',
                              password='masterkey')
            cursor = con.cursor()
            cursor.execute(self.QUERY_CLIENTES + "where CLIENTES.NOMBRE like '%{}%'".format(name))
            records = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            cursor.close()
            result = []
            for row in records:
                result.append(dict(zip(columns, row)))
            if not result:
                return Response({'result':'Cliente no encontrado'}, status=404)
            return Response({'data':result}, status=200)
        return Response({'result':'Error en parametros recibidos'}, status=400)

    # pylint: disable=unused-argument
    # pylint: disable=invalid-name
    def retrieve(self, request, pk=None):
        """
            Get
        """
        result = []
        if not pk.isdigit():
            return Response({'result':'El ID tiene que ser un numérico'}, status=404)
        if pk:
            con = fdb.connect(host='localhost',
                              port=3050,
                              database='/home/michel/Downloads/EXCEL.FDB',
                              user='SYSDBA',
                              password='masterkey')
            cursor = con.cursor()
            cursor.execute(self.QUERY_CLIENTES +
                           "where CLIENTES.CLIENTE_ID like '{}'".format(pk))
            record = cursor.fetchone()
            if record:
                columns = [column[0] for column in cursor.description]
                cursor.close()
                result = dict(zip(columns, record))
            else:
                return Response({'result':'ID no encontrado'}, status=404)
        return Response(result)

    @staticmethod
    def validate_client(data):
        """
            Validate data
        """
        result = {
            'columns': [],
            'values': [],
            'missing': [],
            'wrong': [],
        }
        columns = data.keys()
        #OBLIGATORIOS
        obligatorios = ["NOMBRE",
                        "SUJETO_IEPS",
                        "DIFERIR_CFDI_COBROS",
                        "LIMITE_CREDITO",
                        "MONEDA_ID",
                        "COND_PAGO_ID"]
        for element in obligatorios:
            if not element in columns or data[element][0] in [".",""," ", "  "]:
                result['missing'].append(element)
            else:
                data[element][0] = str(data[element][0])

        if not bool(result['missing']):
            #ERRONEOS
            #Foreign Key
            digits = ["MONEDA_ID",
                      "COND_PAGO_ID",
                      "TIPO_CLIENTE_ID",
                      "ZONA_CLIENTE_ID",
                      "COBRADOR_ID",
                      "VENDEDOR_ID"]
            for element in digits:
                if element in columns:
                    if not data[element][0].isdigit():
                        result['wrong'].append('{} necesita ser tipo ID'.format(element))
                    else:
                        data[element][0] = int(data[element][0])
            #Float
            floats = ['LIMITE_CREDITO']
            for element in floats:
                num = data[element][0].split('.')
                if element in columns:
                    if not (num[-1] is not None and num[-1].isdigit()):
                        result['wrong'].append('{} necesita ser un número'.format(element))
                    else:
                        data[element][0] = float(data[element][0])

            #Date
            dates = ['FECHA_SUSP']
            for element in dates:
                try:
                    date = datetime.strptime(data[element][0], '%Y-%m-%d')
                except Exception:
                    date = None
                if element in columns:
                    if 'datetime.datetime' in str(type(date)):
                        data[element][0] = str(data[element][0])
                    else:
                        result['wrong'].append('{} necesita tener formato de fecha (YYYY-MM-DD)'
                                       .format(element))

            #Bool
            bools = ['DIFERIR_CFDI_COBROS']
            for element in bools:
                if element in columns:
                    if data[element][0] == "true":
                        data[element][0] = True
                    else:
                        data[element][0] = False
            #S/N
            lista = ["COBRAR_IMPUESTOS",
                     "RETIENE_IMPUESTOS",
                     "SUJETO_IEPS",
                     "GENERAR_INTERESES",
                     "EMITIR_EDOCTA"]
            for element in lista:
                if element in columns:
                    if data[element][0] in ['s','S',"n","N"]:
                        data[element][0] = str(data[element][0]).upper()
                    else:
                        result['wrong'].append('{} necesita tener el formato S/N'.format(element))

        if not bool(result['missing']) and  not bool(result['wrong']):
            #DEFAULT
            if not "CLIENTE_ID" in columns:
                data['CLIENTE_ID'] = [-1]
            if not "ESTATUS" in columns:
                data['ESTATUS'] = "A"
            if not "COBRAR_IMPUESTOS" in columns:
                data['COBRAR_IMPUESTOS'] = "S"
            if not "RETIENE_IMPUESTOS" in columns:
                data['RETIENE_IMPUESTOS'] = "N"
            if not "SUJETO_IEPS" in columns:
                data['SUJETO_IEPS'] = "N"
            if not "GENERAR_INTERESES" in columns:
                data['GENERAR_INTERESES'] = "S"
            if not "EMITIR_EDOCTA" in columns:
                data['EMITIR_EDOCTA'] = "S"
            if not "DIFERIR_CFDI_COBROS" in columns:
                data['DIFERIR_CFDI_COBROS'] = [False]
            if not "LIMITE_CREDITO" in columns:
                data['LIMITE_CREDITO'] = [0]

        for element in data.keys():
            result['columns'].append(element)
        for element in result['columns']:
            result['values'].append(data[element][0])
        result['columns'] = tuple(result['columns'])
        result['values'] = tuple(result['values'])

        x = result['columns']
        cadena = ""
        for element in x:
            cadena += element + ","
        result['columns_formated'] = cadena[:len(cadena)-1]
        return result

    @staticmethod
    def fields_updated(data):
        """
        checks field for put patch
        """
        result = ""
        wrong = []
        columns = data.keys()
        posible_items = ["NOMBRE", "CONTACTO1", "CONTACTO2", "ESTATUS",
                         "CAUSA_SUSP", "FECHA_SUSP", "COBRAR_IMPUESTOS",
                         "RETIENE_IMPUESTOS", "SUJETO_IEPS", "GENERAR_INTERESES",
                         "EMITIR_EDOCTA", "DIFERIR_CFDI_COBROS", "LIMITE_CREDITO",
                         "MONEDA_ID", "COND_PAGO_ID", "TIPO_CLIENTE_ID", "ZONA_CLIENTE_ID",
                         "COBRADOR_ID", "VENDEDOR_ID", "NOTAS", "CUENTA_CXC",
                         "CUENTA_ANTICIPOS", "FORMATOS_EMAIL", "RECEPTOR_CFD",
                         "NUM_PROV_CLIENTE", "CAMPOS_ADDENDA", "USUARIO_CREADOR",
                         "FECHA_HORA_CREACION", "USUARIO_AUT_CREACION", "USURAIO_ULT_MODIF",
                         "FECHA_HORA_ULTMODIF", "USUARIO_AUT_MODIF"]
        for item in columns:
            if item in posible_items:
                key = item
                val = data[item][0]
                digits = ["MONEDA_ID",
                          "COND_PAGO_ID",
                          "TIPO_CLIENTE_ID",
                          "ZONA_CLIENTE_ID",
                          "COBRADOR_ID",
                          "VENDEDOR_ID"]
                floats = ['LIMITE_CREDITO']
                dates = ['FECHA_SUSP']
                bools = ['DIFERIR_CFDI_COBROS']
                lista = ["COBRAR_IMPUESTOS",
                         "RETIENE_IMPUESTOS",
                         "SUJETO_IEPS",
                         "GENERAR_INTERESES",
                         "EMITIR_EDOCTA"]
                if key in digits:
                    if not str(val).isdigit():
                        wrong.append('{} necesita ser tipo ID'.format(key))
                    else:
                        val = int(val)
                        result += "{} = {}, ".format(key,val)
                elif key in floats:
                    #Float
                    num = val.split('.')
                    if not (num[-1] is not None and num[-1].isdigit()):
                        wrong.append('{} necesita ser un número'.format(key))
                    else:
                        val = float(val)
                        result += "{} = {}, ".format(key,val)
                elif key in dates:
                    #Date
                    try:
                        date = datetime.strptime(val, '%Y-%m-%d')
                    except Exception:
                        date = None
                    if 'datetime.datetime' in str(type(date)):
                        val = str(val)
                        result += "{} = '{}', ".format(key,val)
                    else:
                        wrong.append('{} necesita tener formato de fecha (YYYY-MM-DD)'
                                        .format(key))
                elif key in bools:
                    #Bool
                    if val == "true":
                        val = True
                    else:
                        val = False
                    result += "{} = {}, ".format(key,val)
                elif key in lista:
                    #S/N
                    if val in ['s','S',"n","N"]:
                        val = str(val).upper()
                        result += "{} = '{}', ".format(key,val)
                    else:
                        wrong.append('{} necesita tener el formato S/N'.format(key))
                else:
                    val = str(val)
                    result += "{} = '{}', ".format(key,val)
        result = result[:len(result)-2]
        result = {
            'wrong':wrong,
            'data':result,
        }
        return result


class DoctosViewSet(viewsets.ViewSet):
    """
        Doctos viewset
    """
    QUERY_DOCTOS = """SELECT FOLIO, FECHA FROM DOCTOS_VE """

    def list(self, request):
        """
            Metodo para mostrar la lista
        """
        tipo = request.GET.get('tipo')
        q = request.GET.get('q')
        result = []
        #if q:
        #    con = fdb.connect(host='localhost',
        #                      port=3050,
        #                      database='/home/michel/Downloads/EXCEL.FDB',
        #                      user='SYSDBA',
        #                      password='masterkey')
        #    cursor = con.cursor()
        #    cursor.execute(q)
        #    records = cursor.fetchall()
        #    columns = [column[0] for column in cursor.description]
        #    cursor.close()
        #    result = []
        #    for row in records:
        #        result.append(dict(zip(columns, row)))
        #    if not result:
        #        return Response({'result':'Cliente no encontrado'}, status=404)
        #    return Response({'data':result}, status=200)
        if tipo:
            tipo = tipo.upper()
            con = fdb.connect(host='localhost',
                              port=3050,
                              database='/home/michel/Downloads/EXCEL.FDB',
                              user='SYSDBA',
                              password='masterkey')
            cursor = con.cursor()
            cursor.execute(self.QUERY_DOCTOS + "where TIPO_DOCTO like '{}';".format(tipo))
            records = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            cursor.close()
            result = []
            for row in records:
                result.append(dict(zip(columns, row)))
            if not result:
                return Response({'result':'Cliente no encontrado'}, status=404)
            return Response({'data':result}, status=200)
        return Response({'result':'Error en parametros recibidos'}, status=400)

    # pylint: disable=unused-argument
    # pylint: disable=invalid-name
    def retrieve(self, request, pk=None):
        """
            Get
        """
        result = []
        if not pk.isdigit():
            return Response({'result':'El ID tiene que ser un numérico'}, status=404)
        if pk:
            con = fdb.connect(host='localhost',
                              port=3050,
                              database='/home/michel/Downloads/EXCEL.FDB',
                              user='SYSDBA',
                              password='masterkey')
            cursor = con.cursor()
            cursor.execute(self.QUERY_DOCTOS +
                           "where DOCTO_VE_ID like '{}'".format(pk))
            record = cursor.fetchone()
            if record:
                columns = [column[0] for column in cursor.description]
                cursor.close()
                result = dict(zip(columns, record))
            else:
                return Response({'result':'ID no encontrado'}, status=404)
        return Response(result)

    def partial_update(self, request, pk=None):
        """
        patch
        """
        patch_data = dict(request.data)
        fields = self.fields_updated(patch_data)
        if fields['wrong']:
            return Response({'result': fields['wrong']}, status=400)

        with fdb.connect(host = 'localhost',
                         port = 3050,
                         database = '/home/michel/Downloads/EXCEL.FDB',
                         user = 'SYSDBA',
                         password = 'masterkey') as con:
            
            query = """UPDATE DOCTOS_VE SET {}
                       WHERE DOCTOS_VE.DOCTO_VE_ID LIKE '{}'""".format(fields['data'], pk)
            print query
            try:
                cursor = con.cursor()
                cursor.execute(query)
                con.commit()
                cursor.close()

                select_cursor = con.cursor()
                select_cursor.execute("""SELECT * FROM DOCTOS_VE
                                         where DOCTOS_VE.DOCTO_VE_ID like '{}'""".format(pk))
                client = select_cursor.fetchone()
                columns = [column[0] for column in select_cursor.description]
                select_cursor.close()
                con.close()
                if client:
                    result = dict(zip(columns, client))
                    return Response({'result':result}, status=200)
                return Response({'result':'ID no encontrado'}, status=404)
            except fdb.Error, e:
                try:
                    return Response({'result': e.args[0]}, status=400)
                except IndexError:
                    return Response({'result': "MySQL Error: %s" % str(e)}, status=400)

    def create(self, request):
        """
            Post
        """
        post_data = dict(request.data)
        data = self.validate_client(post_data)
        columns = data['columns_formated']
        values = data['values']
        missing = data['missing']
        wrong = data['wrong']
        if missing:
            return Response({'result': {'Campos faltantes': missing}}, status=400)
        if wrong:
            return Response({'result': wrong}, status=400)
        with fdb.connect(host = 'localhost',
                         port = 3050,
                         database = '/home/michel/Downloads/EXCEL.FDB',
                         user = 'SYSDBA',
                         password = 'masterkey') as con:
            query = "INSERT INTO DOCTOS_VE ({}) VALUES {};".format(columns,values)
            cursor = con.cursor()
            try:
                cursor.execute(query)
                con.commit()
                cursor.close()
                select_cursor = con.cursor()
                select_cursor.execute("SELECT * FROM DOCTOS_VE ORDER BY DOCTO_VE_ID DESC")
                client = select_cursor.fetchone()
                columns = [column[0] for column in select_cursor.description]
                select_cursor.close()
                con.close()
                if client:
                    result = dict(zip(columns, client))
                    return Response({'result':result}, status=200)
                return Response({'result':'ID no encontrado'}, status=404)
            except fdb.Error, e:
                try:
                    return Response({'result': e.args[0]}, status=400)
                except IndexError:
                    return Response({'result': "MySQL Error: %s" % str(e)}, status=400)

    @staticmethod
    def validate_client(data):
        """
            Validate data
        """
        result = {
            'columns': [],
            'values': [],
            'missing': [],
            'wrong': [],
        }
        columns = data.keys()
        #OBLIGATORIOS
        obligatorios = ["CARGAR_SUN",
                        "CFDI_CERTIFICADO",
                        "CLIENTE_ID",
                        "COND_PAGO_ID",
                        "DIR_CLI_ID",
                        "DIR_CONSIG_ID",
                        "DSCTO_IMPORTE",
                        "DSCTO_PCTJE",
                        "ENVIADO",
                        "ES_CFD",
                        "FECHA",
                        "FLETES",
                        "FOLIO",
                        "HORA",
                        "IMPORTE_COBRO",
                        "IMPORTE_NETO",
                        "MONEDA_ID",
                        "OTROS_CARGOS",
                        "PCTJE_COMIS",
                        "PCTJE_DSCTO_PPAG",
                        "PESO_EMBARQUE",
                        "SISTEMA_ORIGEN",
                        "TIPO_CAMBIO",
                        "TIPO_DOCTO",
                        "TOTAL_ANTICIPOS",
                        "TOTAL_IMPUESTOS",
                        "TOTAL_RETENCIONES"
                    ]
        for element in obligatorios:
            if not element in columns or data[element][0] in [".",""," ", "  "]:
                result['missing'].append(element)
            else:
                data[element][0] = str(data[element][0])

        if not bool(result['missing']):
            #ERRONEOS
            #Foreign Key
            digits = ["CLIENTE_ID",
                      "COND_PAGO_ID",
                      "DIR_CLI_ID",
                      "DIR_CONSIG_ID",
                      "DOCTO_VE_ID",
                      "MONEDA_ID",
                      "ALMACEN_ID",
                      "CFDI_FACT_DEVUELTA_ID",
                      "IMPUESTO_SUSTITUIDO_ID",
                      "IMPUESTO_SUSTITUTO_ID",
                      "LUGAR_EXPEDICION_ID",
                      "VENDEDOR_ID",
                      "VIA_EMBARQUE_ID"
                    ]
            for element in digits:
                if element in columns:
                    if not data[element][0].isdigit():
                        result['wrong'].append('{} necesita ser tipo ID'.format(element))
                    else:
                        data[element][0] = int(data[element][0])
            #Float
            floats = [
                "DSCTO_IMPORTE",
                "DSCTO_PCTJE",
                "FLETES",
                "IMPORTE_COBRO",
                "IMPORTE_NETO",
                "OTROS_CARGOS",
                "PCTJE_COMIS",
                "PCTJE_DSCTO_PPAG",
                "PESO_EMBARQUE",
                "TIPO_CAMBIO",
                "TOTAL_ANTICIPOS",
                "TOTAL_IMPUESTOS"
            ]
            for element in floats:
                num = data[element][0].split('.')
                if element in columns:
                    if not (num[-1] is not None and num[-1].isdigit()):
                        result['wrong'].append('{} necesita ser un número'.format(element))
                    else:
                        data[element][0] = float(data[element][0])

            #Date
            dates = [
                "FECHA",
                "FECHA_DSCTO_PPAG",
                "FECHA_ORDEN_COMPRA",
                "FECHA_RECIBO_MERCANCIA",
                "FECHA_VIGENCIA_ENTREGA",
                "FECHA_HORA_CANCELACION",
                "FECHA_HORA_CREACION",
                "FECHA_HORA_ENVIO",
                "FECHA_HORA_ULT_MODIF"
            ]
            for element in dates:
                try:
                    date = datetime.strptime(data[element][0], '%Y-%m-%d')
                except Exception:
                    date = None
                if element in columns:
                    if 'datetime.datetime' in str(type(date)):
                        data[element][0] = str(data[element][0])
                    else:
                        result['wrong'].append('{} necesita tener formato de fecha (YYYY-MM-DD)'
                                       .format(element))

            #S/N
            lista = [
                "CFDI_CERTIFICADO",
                "ENVIADO",
                "ES_CFD",
                "ACREDITAR_CXC",
                "CFD_ENVIO_ESPECIAL",
                "CONTABILIZADO",
                "FORMA_EMITIDA",
                "SUBTIPO_DOCTO",
                "CARGAR_SUN",
                "APLICADO"
            ]
            for element in lista:
                if element in columns:
                    if data[element][0] in ['s','S',"n","N"]:
                        data[element][0] = str(data[element][0]).upper()
                    else:
                        result['wrong'].append('{} necesita tener el formato S/N'.format(element))

        if not bool(result['missing']) and  not bool(result['wrong']):
            #DEFAULT
            if not "DOCTO_VE_ID" in columns:
                data['DOCTO_VE_ID'] = [-1]
            if not "TOTAL_RETENCIONES" in columns:
                data['TOTAL_RETENCIONES'] = [0]
            if not "DSCTO_IMPORTE" in columns:
                data['DSCTO_IMPORTE'] = [0]
            if not "DSCTO_PCTJE" in columns:
                data['DSCTO_PCTJE'] = [0]
            if not "FLETES" in columns:
                data['FLETES'] = [0]
            if not "IMPORTE_COBRO" in columns:
                data['IMPORTE_COBRO'] = [0]
            if not "IMPORTE_NETO" in columns:
                data['IMPORTE_NETO'] = [0]
            if not "OTROS_CARGOS" in columns:
                data['OTROS_CARGOS'] = [0]
            if not "PCTJE_COMIS" in columns:
                data['PCTJE_COMIS'] = [0]
            if not "PCTJE_DSCTO_PPAG" in columns:
                data['PCTJE_DSCTO_PPAG'] = [0]
            if not "PESO_EMBARQUE" in columns:
                data['PESO_EMBARQUE'] = [0]
            if not "TIPO_CAMBIO" in columns:
                data['TIPO_CAMBIO'] = [0]
            if not "TOTAL_ANTICIPOS" in columns:
                data['TOTAL_ANTICIPOS'] = [0]
            if not "TOTAL_IMPUESTOS" in columns:
                data['TOTAL_IMPUESTOS'] = [0]
            
            if not "CFDI_CERTIFICADO" in columns:
                data['CFDI_CERTIFICADO'] = "N"
            if not "ENVIADO" in columns:
                data['ENVIADO'] = "N"
            if not "ES_CFD" in columns:
                data['ES_CFD'] = "N"
            if not "ACREDITAR_CXC" in columns:
                data['ACREDITAR_CXC'] = "N"
            if not "CFD_ENVIO_ESPECIAL" in columns:
                data['CFD_ENVIO_ESPECIAL'] = "N"
            if not "CONTABILIZADO" in columns:
                data['CONTABILIZADO'] = "N"
            if not "FORMA_EMITIDA" in columns:
                data['FORMA_EMITIDA'] = "N"
            if not "SUBTIPO_DOCTO" in columns:
                data['SUBTIPO_DOCTO'] = "N"

            if not "CARGAR_SUN" in columns:
                data['CARGAR_SUN'] = "S"
            if not "APLICADO" in columns:
                data['APLICADO'] = "S"
            

        for element in data.keys():
            result['columns'].append(element)
        for element in result['columns']:
            result['values'].append(data[element][0])
        result['columns'] = tuple(result['columns'])
        result['values'] = tuple(result['values'])

        x = result['columns']
        cadena = ""
        for element in x:
            cadena += element + ","
        result['columns_formated'] = cadena[:len(cadena)-1]
        return result

    @staticmethod
    def fields_updated(data):
        """
        checks field for put patch
        """
        result = ""
        wrong = []
        columns = data.keys()
        posible_items = ["TOTAL_RETENCIONES","DSCTO_IMPORTE","USUARIO_CANCELACION",
                         "DSCTO_PCTJE","FLETES","IMPORTE_COBRO","IMPORTE_NETO",
                         "OTROS_CARGOS","PCTJE_COMIS","PCTJE_DSCTO_PPAG","PESO_EMBARQUE",
                         "TIPO_CAMBIO","TOTAL_ANTICIPOS","TOTAL_IMPUESTOS","CFDI_CERTIFICADO",
                         "ENVIADO","ES_CFD","ACREDITAR_CXC","CFD_ENVIO_ESPECIAL",
                         "CONTABILIZADO","FORMA_EMITIDA","SUBTIPO_DOCTO","FECHA_HORA_CREACION",
                         "FECHA_HORA_ENVIO","FECHA_HORA_ULT_MODIF","HORA","CARGAR_SUN",
                         "APLICADO","USUARIO_CREADOR","USUARIO_ULT_MODIF","FOLIO",
                         "SISTEMA_ORIGEN","TIPO_DOCTO","ESTATUS","METODO_PAGO_SAT",
                         "TIPO_DSCTO","FECHA","FECHA_DSCTO_PPAG","FECHA_ORDEN_COMPRA",
                         "FECHA_RECIBO_MERCANCIA","FECHA_VIGENCIA_ENTREGA","FECHA_HORA_CANCELACION","CLIENTE_ID",
                         "COND_PAGO_ID","DIR_CLI_ID","DIR_CONSIG_ID","DOCTO_VE_ID",
                         "MONEDA_ID","ALMACEN_ID","CFDI_FACT_DEVUELTA_ID","IMPUESTO_SUSTITUIDO_ID",
                         "IMPUESTO_SUSTITUTO_ID","LUGAR_EXPEDICION_ID","VENDEDOR_ID","VIA_EMBARQUE_ID",
                         "CLAVE_CLIENTE","DESCRIPCION","DESCRIPCION_COBRO","EMAIL_ENVIO",
                         "FOLIO_RECIBO_MERCANCIA","MODALIDAD_FACTURACION","ORDEN_COMPRA","USO_CFDI",
                         "USUARIO_AUT_CANCELACION","USUARIO_AUT_CREACION","USUARIO_AUT_MODIF"]
        for item in columns:
            if item in posible_items:
                key = item
                val = data[item][0]
                digits = ["CLIENTE_ID",
                      "COND_PAGO_ID",
                      "DIR_CLI_ID",
                      "DIR_CONSIG_ID",
                      "DOCTO_VE_ID",
                      "MONEDA_ID",
                      "ALMACEN_ID",
                      "CFDI_FACT_DEVUELTA_ID",
                      "IMPUESTO_SUSTITUIDO_ID",
                      "IMPUESTO_SUSTITUTO_ID",
                      "LUGAR_EXPEDICION_ID",
                      "VENDEDOR_ID",
                      "VIA_EMBARQUE_ID"
                    ]
                floats = [
                    "DSCTO_IMPORTE",
                    "DSCTO_PCTJE",
                    "FLETES",
                    "IMPORTE_COBRO",
                    "IMPORTE_NETO",
                    "OTROS_CARGOS",
                    "PCTJE_COMIS",
                    "PCTJE_DSCTO_PPAG",
                    "PESO_EMBARQUE",
                    "TIPO_CAMBIO",
                    "TOTAL_ANTICIPOS",
                    "TOTAL_IMPUESTOS"
                ]

                dates = [
                    "FECHA",
                    "FECHA_DSCTO_PPAG",
                    "FECHA_ORDEN_COMPRA",
                    "FECHA_RECIBO_MERCANCIA",
                    "FECHA_VIGENCIA_ENTREGA",
                    "FECHA_HORA_CANCELACION",
                    "FECHA_HORA_CREACION",
                    "FECHA_HORA_ENVIO",
                    "FECHA_HORA_ULT_MODIF"
                ]
                lista = [
                    "CFDI_CERTIFICADO",
                    "ENVIADO",
                    "ES_CFD",
                    "ACREDITAR_CXC",
                    "CFD_ENVIO_ESPECIAL",
                    "CONTABILIZADO",
                    "FORMA_EMITIDA",
                    "SUBTIPO_DOCTO",
                    "CARGAR_SUN",
                    "APLICADO"
                ]
                if key in digits:
                    if not str(val).isdigit():
                        wrong.append('{} necesita ser tipo ID'.format(key))
                    else:
                        val = int(val)
                        result += "{} = {}, ".format(key,val)
                elif key in floats:
                    #Float
                    num = val.split('.')
                    if not (num[-1] is not None and num[-1].isdigit()):
                        wrong.append('{} necesita ser un número'.format(key))
                    else:
                        val = float(val)
                        result += "{} = {}, ".format(key,val)
                elif key in dates:
                    #Date
                    try:
                        date = datetime.strptime(val, '%Y-%m-%d')
                    except Exception:
                        date = None
                    if 'datetime.datetime' in str(type(date)):
                        val = str(val)
                        result += "{} = '{}', ".format(key,val)
                    else:
                        wrong.append('{} necesita tener formato de fecha (YYYY-MM-DD)'
                                        .format(key))
                elif key in lista:
                    #S/N
                    if val in ['s','S',"n","N"]:
                        val = str(val).upper()
                        result += "{} = '{}', ".format(key,val)
                    else:
                        wrong.append('{} necesita tener el formato S/N'.format(key))
                else:
                    val = str(val)
                    result += "{} = '{}', ".format(key,val)
        result = result[:len(result)-2]
        result = {
            'wrong':wrong,
            'data':result,
        }
        return result