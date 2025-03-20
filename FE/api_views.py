from datetime import timedelta
from decimal import ROUND_HALF_UP, ConversionSyntax, Decimal
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import requests
import os, json, uuid
from django.db import transaction
from django.utils import timezone
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from FE.views import enviar_factura_invalidacion_hacienda_view, firmar_factura_anulacion_view, invalidacion_dte_view, generar_json, num_to_letras
from .serializers import ActividadEconomicaSerializer, ReceptorSerializer, FacturaElectronicaSerializer
from .models import (
    ActividadEconomica, Emisor_fe, Receptor_fe, FacturaElectronica, DetalleFactura,
    Ambiente, CondicionOperacion, Modelofacturacion, NumeroControl,
    Tipo_dte, TipoMoneda, TipoUnidadMedida, TiposDocIDReceptor, EventoInvalidacion, 
    Receptor_fe, TipoInvalidacion, TiposEstablecimientos, Token_data, Descuento, FormasPago, TipoGeneracionDocumento, Plazo
)
from INVENTARIO.models import Producto, TipoItem, Tributo


FIRMADOR_URL = "http://192.168.2.25:8113/firmardocumento/"
DJANGO_SERVER_URL = "http://127.0.0.1:8000"

SCHEMA_PATH_fe_fc_v1 = "FE/json_schemas/fe-fc-v1.json"

CERT_PATH = "FE/cert/06142811001040.crt"  # Ruta al certificado

# URLS de Hacienda (Pruebas y Producción)
HACIENDA_URL_TEST = "https://apitest.dtes.mh.gob.sv/fesv/recepciondte"
HACIENDA_URL_PROD = "https://api.dtes.mh.gob.sv/fesv/recepciondte"

# Constantes de configuración
COD_CONSUMIDOR_FINAL = "01"
#BC 04/03/2025: Constantes
COD_CONSUMIDOR_FINAL = "01"
COD_CREDITO_FISCAL = "03"
VERSION_EVENTO_INVALIDACION = 2
AMBIENTE = Ambiente.objects.get(codigo="01")
#AMBIENTE = "01"
COD_FACTURA_EXPORTACION = "11"
COD_TIPO_INVALIDACION_RESCINDIR = 2
COD_NOTA_CREDITO = "05"
COD_NOTA_DEBITO = "06"
COD_COMPROBANTE_LIQUIDACION = "08"
EMI_SOLICITA_INVALIDAR_DTE = "emisor"
REC_SOLICITA_INVALIDAR_DTE = "receptor"
COD_TIPO_ITEM_OTROS = "4"
COD_TRIBUTOS_SECCION_2 = "2"
COD_DOCUMENTO_RELACIONADO_NO_SELEC = "S"
ID_CONDICION_OPERACION = 2

formas_pago = [] #Asignar formas de pago
documentos_relacionados = []

######################################################
# AUTENTICACION
######################################################

class AutenticacionAPIView(APIView):
    # Límite de intentos de autenticación permitidos
    max_attempts = 2

    def post(self, request):
        # Inicializar contador de intentos en la sesión si no existe
        if "auth_attempts" not in request.session:
            request.session["auth_attempts"] = 0
        
        # Verificar si se alcanzó el máximo de intentos permitidos
        if request.session["auth_attempts"] >= self.max_attempts:
            return Response({
                "status": "error",
                "message": "Se alcanzó el límite de intentos de autenticación permitidos",
            }, status=status.HTTP_403_FORBIDDEN)  # Código 403: Forbidden

        user = request.data.get("user")  # Usuario enviado desde el cuerpo de la solicitud
        pwd = request.data.get("pwd")    # Contraseña enviada desde el cuerpo de la solicitud

        # URL de autenticación
        auth_url = "https://api.dtes.mh.gob.sv/seguridad/auth"
        
        # Headers para la solicitud
        headers = {
            "User-Agent": "MiAplicacionDjango/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Datos para el cuerpo de la solicitud
        data = {
            "user": user,
            "pwd": pwd,
        }

        try:
            # Realizar solicitud POST a la URL de autenticación
            response = requests.post(auth_url, headers=headers, data=data)
            
            # Intentar convertir la respuesta en JSON
            response_data = response.json()

            # Incrementar el contador de intentos de autenticación
            request.session["auth_attempts"] += 1
            request.session.modified = True  # Asegura que los cambios en la sesión se guarden

            # Procesar respuesta en caso de éxito
            if response.status_code == 200 and response_data.get("status") == "OK":
                # Resetear el contador de intentos si autenticación fue exitosa
                request.session["auth_attempts"] = 0
                token = response_data["body"].get("token")
                roles = response_data["body"].get("roles", [])
                token_type = response_data.get("tokenType", "Bearer")

                return Response({
                    "status": "success",
                    "token": f"{token_type} {token}",
                    "roles": roles,
                })

            else:
                return Response({
                    "status": "error",
                    "message": response_data.get("message", "Error en autenticación"),
                    "error": response_data.get("error", "No especificado"),
                }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            # Error de conexión con el servicio
            return Response({
                "status": "error",
                "message": "Error de conexión con el servicio de autenticación",
                "details": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def autenticacion(request):

    tokens_saves = Token_data.objects.all()

    if request.method == "POST":
        nit_empresa = request.POST.get("user")
        pwd = request.POST.get("pwd")

        auth_url = "https://api.dtes.mh.gob.sv/seguridad/auth"
        headers = {"User-Agent": "MiAplicacionDjango/1.0"}
        data = {"user": nit_empresa, "pwd": pwd}

        try:
            response = requests.post(auth_url, headers=headers, data=data)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("status") == "OK":
                    token_body = response_data["body"]
                    token = token_body.get("token")
                    token_type = token_body.get("tokenType", "Bearer")
                    roles = token_body.get("roles", [])

                    # Guardar o actualizar los datos del token en la base de datos
                    token_data, created = Token_data.objects.update_or_create(
                        nit_empresa=nit_empresa,
                        defaults={
                            'password_hacienda': pwd,
                            'token': token,
                            'token_type': token_type,
                            'roles': roles,
                            'activado': True,
                            'fecha_caducidad': timezone.now() + timedelta(days=1)  # Establecer caducidad para 24 horas después
                        }
                    )

                    # Si el token es nuevo, enviamos un mensaje de éxito
                    if created:
                        messages.success(request, "Autenticación exitosa y token guardado.")
                    else:
                        messages.success(request, "Autenticación exitosa y token actualizado.")

                    return redirect('autenticacion')
                else:
                    messages.error(request, "Error en la autenticación: " + response_data.get("message", "Error no especificado"))
            else:
                messages.error(request, "Error en la autenticación.")
        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexión con el servicio de autenticación.")

    return render(request, "autenticacion.html", {'tokens':tokens_saves})

######################################################
# ACTIVIDADES ECONOMICAS
######################################################

# Vista para obtener el detalle de una Actividad Económica
class ActividadEconomicaDetailAPIView(generics.RetrieveAPIView):
    queryset = ActividadEconomica.objects.all()
    serializer_class = ActividadEconomicaSerializer

# Vista para crear una nueva Actividad Económica
class ActividadEconomicaCreateAPIView(generics.CreateAPIView):
    queryset = ActividadEconomica.objects.all()
    serializer_class = ActividadEconomicaSerializer

# Vista para actualizar una Actividad Económica existente
class ActividadEconomicaUpdateAPIView(generics.UpdateAPIView):
    queryset = ActividadEconomica.objects.all()
    serializer_class = ActividadEconomicaSerializer

# Vista para eliminar una Actividad Económica
class ActividadEconomicaDeleteAPIView(generics.DestroyAPIView):
    queryset = ActividadEconomica.objects.all()
    serializer_class = ActividadEconomicaSerializer

######################################################
# RECEPTOR
######################################################

class ObtenerReceptorAPIView(APIView):
    """
    Devuelve los datos de un receptor en formato JSON.
    """
    def get(self, request, receptor_id):
        try:
            receptor = Receptor_fe.objects.get(id=receptor_id)
            # Si tienes un serializer para Receptor_fe, úsalo:
            serializer = ReceptorSerializer(receptor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Receptor_fe.DoesNotExist:
            return Response({"error": "Receptor no encontrado"}, status=status.HTTP_404_NOT_FOUND)

######################################################
# EMISOR
######################################################


######################################################
# PRODUCTOS Y SERVICIOS
######################################################


######################################################
# GENERACION DE DOCUMENTOS ELECTRONICOS
######################################################

class FacturaListAPIView(APIView):
    """
    Vista API que devuelve un listado de FacturaElectronica con filtros y paginación.
    Parámetros GET:
      - recibido_mh: 'True' o 'False'
      - sello_recepcion: (filtro por coincidencia, icontains)
      - has_sello_recepcion: 'yes' para facturas con sello, 'no' para aquellas sin sello
      - tipo_dte: id del tipo de DTE
      - page: número de página (paginación de 20 registros)
      
    Además se incluye la lista de tipos de DTE.
    """
    def get(self, request):
        # Obtener el queryset base
        queryset = FacturaElectronica.objects.all()
        
        # Aplicar filtros según los parámetros GET
        recibido = request.GET.get('recibido_mh')
        codigo = request.GET.get('sello_recepcion')
        has_codigo = request.GET.get('has_sello_recepcion')
        tipo = request.GET.get('tipo_dte')
        
        if recibido in ['True', 'False']:
            queryset = queryset.filter(recibido_mh=(recibido == 'True'))
        if codigo:
            queryset = queryset.filter(sello_recepcion__icontains=codigo)
        if has_codigo == 'yes':
            queryset = queryset.exclude(sello_recepcion__isnull=True)
        elif has_codigo == 'no':
            queryset = queryset.filter(sello_recepcion__isnull=True)
        if tipo:
            queryset = queryset.filter(tipo_dte__id=tipo)
        
        # Configurar la paginación: 20 registros por página
        paginator = paginator(queryset, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Serializar los datos
        serializer = FacturaElectronicaSerializer(page_obj, many=True)
        
        # Serializar los tipos de DTE para el filtro
        tipos_dte = Tipo_dte.objects.all()
        tipos_dte_data = [{"id": t.id, "codigo": t.codigo, "descripcion": t.descripcion} for t in tipos_dte]
        
        data = {
            "facturas": serializer.data,
            "pagination": {
                "page": page_obj.number,
                "pages": paginator.num_pages,
                "total": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "tipos_dte": tipos_dte_data
        }
        
        return Response(data, status=status.HTTP_200_OK)

class GenerarFacturaAPIView(APIView):
    """
    Vista de API REST para generar facturas.
    Permite obtener datos necesarios mediante GET y generar la factura mediante POST.
    """
    cod_generacion = str(uuid.uuid4()).upper()
    # Puedes agregar permisos o autenticación según tus necesidades:
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        print("Inicio generar dte")
        tipo_dte = request.query_params.get('tipo_dte', '01')
        emisor_obj = Emisor_fe.objects.first()

        if emisor_obj:
            nuevo_numero = NumeroControl.preview_numero_control(tipo_dte)
        else:
            nuevo_numero = ""

        codigo_generacion = self.cod_generacion
        fecha_generacion = timezone.now().date()
        hora_generacion = timezone.now().strftime('%H:%M:%S')

        emisor_data = {
            "nit": emisor_obj.nit if emisor_obj else "",
            "nombre_razon_social": emisor_obj.nombre_razon_social if emisor_obj else "",
            "direccion_comercial": emisor_obj.direccion_comercial if emisor_obj else "",
            "telefono": emisor_obj.telefono if emisor_obj else "",
            "email": emisor_obj.email if emisor_obj else "",
        } if emisor_obj else None

        # Se obtiene la data de otros modelos
        receptores = list(Receptor_fe.objects.values("id", "num_documento", "nombre"))
        # Se convierten los querysets a listas de diccionarios
        productos = list(Producto.objects.all().values())
        tipooperaciones = list(CondicionOperacion.objects.all().values())
        tipoDocumentos = list(Tipo_dte.objects.all().values())
        tipoItems = list(TipoItem.objects.all().values())
        descuentos = list(Descuento.objects.all().values())
        formasPago = list(FormasPago.objects.all().values())
        tipoGeneracionDocumentos = list(TipoGeneracionDocumento.objects.all().values())

        context = {
            "numero_control": nuevo_numero,
            "codigo_generacion": codigo_generacion,
            "fecha_generacion": str(fecha_generacion),
            "hora_generacion": hora_generacion,
            "emisor": emisor_data,
            "receptores": receptores,
            "productos": productos,
            "tipooperaciones": tipooperaciones,
            "tipoDocumentos": tipoDocumentos,
            "tipoItems": tipoItems,
            "descuentos": descuentos,
            "formasPago": formasPago,
            "tipoGenDocumentos": tipoGeneracionDocumentos
            
        }
        return Response(context, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, format=None):
        tipo_dte = request.query_params.get('tipo_dte', '01')
        nuevo_numero = NumeroControl.preview_numero_control(tipo_dte)
        global formas_pago
        try:
            items_permitidos = 2000
            data = request.data
            # Datos básicos
            numero_control = nuevo_numero
            codigo_generacion = self.cod_generacion
            print(f"Numero de control: {numero_control} Codigo generacion: {self.cod_generacion}")
            
            receptor_id = data.get('receptor_id', None)
            receptor = Receptor_fe.objects.get(id=receptor_id)
            nit_receptor = data.get('nit_receptor', receptor.num_documento)
            nombre_receptor = receptor.nombre#data.get('nombre_receptor', '')
            direccion_receptor = receptor.direccion#data.get('direccion_receptor', '')
            telefono_receptor = receptor.telefono#data.get('telefono_receptor', '')
            correo_receptor = receptor.correo#data.get('correo_receptor', '')
            
            observaciones = data.get('observaciones', '')
            tipo_dte = data.get("tipo_documento_seleccionado", None)
            tipo_item = data.get("tipo_item_select", None)
            tipo_doc_relacionar = data.get("documento_seleccionado", None)
            documento_relacionado = data.get("documento_select", None)
            porcentaje_descuento = data.get("descuento_select", "0")
            porcentaje_descuento_item = Decimal(porcentaje_descuento.replace(",", "."))
            print(f"DTE seleccionado desde el form: {tipo_dte}")

            # Configuración adicional
            tipooperacion_id = data.get("condicion_operacion", None)
            porcentaje_retencion_iva = Decimal(data.get("porcentaje_retencion_iva", "0"))
            retencion_iva = data.get("retencion_iva", False)
            productos_retencion_iva = data.get("productos_retencion_iva", [])
            porcentaje_retencion_renta = Decimal(data.get("porcentaje_retencion_renta", "0"))
            retencion_renta = data.get("retencion_renta", False)
            productos_retencion_renta = data.get("productos_retencion_renta", [])
            
            descuento_global = data.get("descuento_global_input", "0")
            saldo_favor = data.get("saldo_favor_input", "0")
            base_imponible_checkbox = data.get("no_gravado", False)
            
            formas_pago_cod = data.get('fp_id', [])
            num_referencia = request.GET.get("num_ref", None)
            #formas_pago = formas_pago_cod
            print("-formas de pago: ", formas_pago_cod)
            producto_id = data.get("producto_id")
            asignar_fp = agregar_formas_pago(formas_pago_cod, num_referencia)
            
            if saldo_favor is not None and saldo_favor !="":
                saldo_f = Decimal(saldo_favor)
                if saldo_f > Decimal("0.00"):
                    saldo_favor = saldo_f * Decimal("-1")
                else:
                    saldo_favor = Decimal("0.00")
            else:
                saldo_favor = Decimal("0.00")

            # Datos de productos
            productos_ids = data.get('productos_ids', [])
            cantidades = data.get('cantidades', [])

            if numero_control:
                print("-Asignar numero control")
                numero_control = NumeroControl.obtener_numero_control(tipo_dte)
                print(numero_control)
            if not codigo_generacion:
                codigo_generacion = str(uuid.uuid4()).upper()
                
            # Obtener emisor
            emisor_obj = Emisor_fe.objects.first()
            if not emisor_obj:
                return Response({"error": "No hay emisores registrados en la base de datos"}, status=status.HTTP_400_BAD_REQUEST)
            emisor = emisor_obj

            # Obtener o asignar receptor
            if receptor_id and receptor_id != "nuevo":
                receptor = Receptor_fe.objects.get(id=receptor_id)
            else:
                tipo_doc, _ = TiposDocIDReceptor.objects.get_or_create(
                    codigo='13', defaults={"descripcion": "DUI/NIT"}
                )
                receptor, _ = Receptor_fe.objects.update_or_create(
                    num_documento=nit_receptor,
                    defaults={
                        'nombre': nombre_receptor,
                        'tipo_documento': tipo_doc,
                        'direccion': direccion_receptor,
                        'telefono': telefono_receptor,
                        'correo': correo_receptor
                    }
                )

            # Configuración por defecto de la factura
            ambiente_obj = Ambiente.objects.get(codigo="01")
            tipo_dte_obj = Tipo_dte.objects.get(codigo=tipo_dte)
            print(f"Tipo de documento a generar = {tipo_dte_obj}")
            tipo_item_obj = TipoItem.objects.get(codigo=tipo_item)

            tipomodelo_obj = Modelofacturacion.objects.get(codigo="1")
            tipooperacion_obj = CondicionOperacion.objects.get(id=tipooperacion_id) if tipooperacion_id else None
            tipo_moneda_obj = TipoMoneda.objects.get(codigo="USD")

            factura = FacturaElectronica.objects.create(
                version="1.0",
                tipo_dte=tipo_dte_obj,
                numero_control=numero_control,
                codigo_generacion=codigo_generacion,
                tipomodelo=tipomodelo_obj,
                tipocontingencia=None,
                motivocontin=None,
                tipomoneda=tipo_moneda_obj,
                dteemisor=emisor,
                dtereceptor=receptor,
                json_original={},
                firmado=False,
                base_imponible = base_imponible_checkbox
            )

            # Inicialización de acumuladores
            total_gravada = Decimal("0.00")
            total_iva = Decimal("0.00")
            total_pagar = Decimal("0.00")
            DecimalRetIva = Decimal("0.00")
            DecimalRetRenta = Decimal("0.00")
            DecimalIvaPerci = Decimal("0.00")
            total_operaciones = Decimal("0.00")
            total_descuento_gravado = Decimal("0.00")
            total_no_gravado = Decimal("0.00")
            total_iva_item = Decimal("0.00")
            
            #Campos DTE
            tributo_valor = None

            # Procesar cada producto
            for index, prod_id in enumerate(productos_ids):
                try:
                    producto = Producto.objects.get(id=prod_id)
                except Producto.DoesNotExist:
                    continue
                
                # Obtener unidad de medida
                #Unidad de medida = 99 cuando el contribuyente preste un servicio
                if base_imponible_checkbox is True or tipo_item_obj.codigo == COD_TIPO_ITEM_OTROS:
                    unidad_medida_obj = TipoUnidadMedida.objects.get(codigo="99")
                else:
                    unidad_medida_obj = TipoUnidadMedida.objects.get(codigo=producto.unidad_medida.codigo)

                #Cantidad = 1, Si se utiliza el campo base imponible, si el tipo de item es 4, ...
                if base_imponible_checkbox is True or tipo_item_obj.codigo == COD_TIPO_ITEM_OTROS:
                    cantidad = 1
                else:
                    cantidad = int(cantidades[index]) if index < len(cantidades) else 1
                    
                precio_incl = producto.preunitario
                
                #Campo tributos
                if (base_imponible_checkbox is False and tipo_item_obj.codigo == COD_TIPO_ITEM_OTROS) or tipo_dte_obj.codigo != COD_CONSUMIDOR_FINAL: #factura.tipo_dte.codigo != COD_CONSUMIDOR_FINAL and
                    # Codigo del tributo (tributos.codigo)
                    tributoIva = Tributo.objects.get(codigo="20")#IVA este codigo solo aplica a ventas gravadas(ya que estan sujetas a iva)
                    tributo_valor = tributoIva.valor_tributo
                    tributos = [str(tributoIva.codigo)]
                else:
                    tributos = None
                    
                if tributo_valor is None:
                    tributo_valor = Decimal("0.00")               
                #Campo precioUni
                # Se asume que el precio ya viene con IVA
                if base_imponible_checkbox is True:
                    precio_neto = float(0.00)
                elif base_imponible_checkbox is False and tipo_dte_obj.codigo == COD_CONSUMIDOR_FINAL : #si es FE agregarle iva al prod
                    precio_neto = (precio_incl * Decimal("1.13") ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    #total_iva_item = ( ( precio_incl * cantidad) / Decimal("1.13") * Decimal("0.13") ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                else:  #Cuando no es FE quitarle iva al precio si se aplico desde el producto
                    precio_neto = (precio_incl / Decimal("1.13")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    #BC: verificar si el precio del prod para ccf ya viene con iva
                    #total_iva_item = ( ( precio_incl * cantidad) / Decimal("1.13") * Decimal("0.13") ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                print(f"Precio Incl = {precio_incl}, Precio neto = {precio_neto}, tipo dte:  {tipo_dte}")
                
                if tipo_item_obj.codigo == COD_TIPO_ITEM_OTROS:
                    print("-Precio neto: ", precio_neto)
                    precio_neto = precio_neto * Decimal(tributo_valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    print("-Precio neto con valor trib: ", precio_neto)
                   
                precio_neto = Decimal(precio_neto)          
                iva_unitario = (precio_incl - precio_neto).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                total_iva_item = ( ( precio_neto * cantidad) / Decimal("1.13") * Decimal("0.13") ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                
                porcentaje_descuento_item = Descuento.objects.get(id=porcentaje_descuento)
                if porcentaje_descuento_item.porcentaje > Decimal("0.00"):
                    descuento_aplicado=True
                else:
                    descuento_aplicado = False
                print("-Descuento por item", porcentaje_descuento_item.porcentaje)
                
                # Totales por ítem
                #Campo Ventas gravadas
                total_neto = ((precio_neto * cantidad) - (porcentaje_descuento_item.porcentaje / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  
                print(f"IVA Item = {total_iva_item}, iva unitario = {iva_unitario}, cantidad = {cantidad}, total neto = {total_neto} ")
                
                #Campo codTributo
                cuerpo_documento_tributos = []
                tributo = None
                if producto.tributo is None:
                    seleccionarTributoMensaje = "Seleccionar tributo para el producto"
                    return Response({"error": "Seleccionar tributo para el producto" })
                
                #Tributo sujeto iva (asociado al prod)
                if tipo_item_obj.codigo == COD_TIPO_ITEM_OTROS:
                    tributo = Tributo.objects.get(codigo=producto.tributo.codigo)
                    precio_neto = (precio_neto * Decimal(tributo.valor_tributo)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    
                print("-Crear detalle factura")
                detalle = DetalleFactura.objects.create(
                    factura=factura,
                    producto=producto,
                    cantidad=cantidad,
                    unidad_medida=unidad_medida_obj,
                    precio_unitario=precio_incl,  # Precio bruto (con IVA)
                    descuento=porcentaje_descuento_item,
                    tiene_descuento = descuento_aplicado,
                    ventas_no_sujetas=Decimal("0.00"),
                    ventas_exentas=Decimal("0.00"),
                    ventas_gravadas=total_neto,
                    pre_sug_venta=precio_incl,
                    no_gravado=Decimal("0.00"),
                    saldo_favor=saldo_favor
                )
                
                total_gravada += total_neto
                
                #Calcular el valor del tributo
                if tipo_dte_obj.codigo == COD_CREDITO_FISCAL:
                    valorTributo = ( Decimal(total_gravada) * Decimal(tributo_valor) ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    total_operaciones = total_gravada + valorTributo
                else:
                    total_operaciones = total_gravada
                print("-Calcular el total de operaciones: ", total_operaciones)
                
                if tipo_dte_obj.codigo == COD_CONSUMIDOR_FINAL:
                    total_con_iva = (precio_neto * cantidad).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                else:
                    #total_con_iva = (precio_neto * cantidad).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    total_con_iva = total_operaciones - DecimalIvaPerci - DecimalRetIva - DecimalRetRenta - total_no_gravado
                    print("-Total pagar: ", total_con_iva)
                    
                if tipo_dte_obj.codigo == COD_NOTA_CREDITO or tipo_dte_obj.codigo == COD_NOTA_DEBITO:
                    total_operaciones = (total_gravada + valorTributo + DecimalIvaPerci) - DecimalRetIva
                
                total_iva += total_iva_item
                total_pagar += total_con_iva
                
                detalle.total_sin_descuento = total_neto
                detalle.iva = total_iva_item
                detalle.total_con_iva = total_con_iva
                detalle.iva_item = total_iva_item
                detalle.save()
                
                print("-Aplicar tributo sujeto iva")
                valor_porcentaje = Decimal(porcentaje_descuento_item.porcentaje)
                
                print("-Validar porcentaje")
                if valor_porcentaje.compare(Decimal("0.00")) > 0:
                    total_descuento_gravado += porcentaje_descuento_item.porcentaje
                print("-Total desc gravado: ", total_descuento_gravado)
                
            # Calcular retenciones si corresponde (globales sobre el total neto de cada detalle)
            if retencion_iva and porcentaje_retencion_iva > 0:
                for detalle in factura.detalles.all():
                    if str(detalle.producto.id) in productos_retencion_iva:
                        DecimalRetIva += (detalle.total_sin_descuento * porcentaje_retencion_iva / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if retencion_renta and porcentaje_retencion_renta > 0:
                for detalle in factura.detalles.all():
                    if str(detalle.producto.id) in productos_retencion_renta:
                        DecimalRetRenta += (detalle.total_sin_descuento * porcentaje_retencion_renta / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
          
            total_iva = total_iva.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total_pagar = total_pagar.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
             #Sino se ha seleccionado ningun documento a relacionar enviar null los campos
            if tipo_doc_relacionar is COD_DOCUMENTO_RELACIONADO_NO_SELEC:
                tipo_doc_relacionar = None
                documento_relacionado = None

            # Actualizar totales en la factura
            factura.total_no_sujetas = Decimal("0.00")
            factura.total_exentas = Decimal("0.00")
            factura.total_gravadas = total_gravada
            factura.sub_total_ventas = total_gravada
            factura.descuen_no_sujeto = Decimal("0.00")
            factura.descuento_exento = Decimal("0.00")
            factura.descuento_gravado = total_descuento_gravado
            factura.por_descuento = descuento_global
            factura.total_descuento = total_descuento_gravado
            factura.sub_total = total_gravada
            factura.iva_retenido = DecimalRetIva
            factura.retencion_renta = DecimalRetRenta
            factura.total_operaciones = total_operaciones
            factura.total_no_gravado = Decimal("0.00")
            factura.total_pagar = total_pagar
            factura.total_letras = num_to_letras(total_pagar)
            factura.total_iva = total_iva
            factura.condicion_operacion = tipooperacion_obj
            factura.iva_percibido = DecimalIvaPerci
            factura.tipo_documento_relacionar = tipo_doc_relacionar
            factura.documento_relacionado = documento_relacionado
            factura.save()

            # Construir el cuerpo del documento para el JSON
            cuerpo_documento = []
            for idx, det in enumerate(factura.detalles.all(), start=1):
                #Items permitidos 2000
                if idx > items_permitidos:
                    return Response({"error": "Cantidad máxima de ítems permitidos " }, {items_permitidos})
                else:
                    codTributo = None 
                    tributo_valor = None
                    
                    #Campo codTributo
                    cuerpo_documento_tributos = []
                    if det.producto.tributo is None:
                        seleccionarTributoMensaje = "Seleccionar tributo para el producto"
                        return Response({"error": "Seleccionar tributo para el producto" })
                    else:
                        if tipo_item_obj.codigo == COD_TIPO_ITEM_OTROS:
                            codTributo = tributo.codigo
                                                           
                            #Si el tributo asociado el prod pertenece a la seccion 2 de la tabla agregar un segundo item
                            if tributo.tipo_tributo.codigo == COD_TRIBUTOS_SECCION_2:
                                print("-Crear nuevo item")
                                #Nuevo item (requerido cuando el tributo es de la seccion 2)
                                cuerpo_documento_tributos.append({
                                    "numItem": idx+1,
                                    "tipoItem": int(tipo_item_obj.codigo),
                                    "numeroDocumento": None,
                                    "codigo": str(det.producto.codigo),
                                    "codTributo": codTributo,
                                    "descripcion": str(tributo.descripcion),
                                    "cantidad": float(cantidad), 
                                    "uniMedida": int(unidad_medida_obj.codigo),
                                    "precioUni": float(precio_neto),
                                    "montoDescu": float(porcentaje_descuento_item.porcentaje),
                                    "ventaNoSuj": float(0.0),
                                    "ventaExenta": float(0.0),
                                    "ventaGravada": float(det.ventas_gravadas),
                                    "tributos": tributos, 
                                    "psv": float(precio_neto), 
                                    "noGravado": float(0.0)
                                })
                    print(f"-Total IVA = {total_iva_item}")

                    cuerpo_documento.append({
                        "numItem": idx,
                        "tipoItem": int(tipo_item),
                        "numeroDocumento": None,
                        "codigo": str(det.producto.codigo),
                        "codTributo": codTributo,
                        "descripcion": str(det.producto.descripcion),
                        "cantidad": float(det.cantidad),
                        "uniMedida": int(unidad_medida_obj.codigo),
                        "precioUni": float(precio_neto),
                        "montoDescu": float(porcentaje_descuento_item.porcentaje),
                        "ventaNoSuj": float(det.ventas_no_sujetas),
                        "ventaExenta": float(det.ventas_exentas),
                        "ventaGravada": float(det.ventas_gravadas),
                        "tributos": tributos,
                        "psv": float(precio_neto),
                        "noGravado": float(det.no_gravado),
                    })
                    
                    if cuerpo_documento_tributos is None:
                        cuerpo_documento.append(cuerpo_documento_tributos)
                    print("-Cuerpo documento: ", cuerpo_documento)
                        
                print(f"Item {idx}: IVA unitario = {iva_unitario}, Total IVA = {total_iva_item}, IVA almacenado = {det.iva_item}")

            # Generar el JSON final de la factura
            factura_json = generar_json(
                ambiente_obj, tipo_dte_obj, factura, emisor, receptor,
                cuerpo_documento, observaciones, Decimal(str(total_iva_item)), base_imponible_checkbox, saldo_favor
            )
            
            factura.json_original = factura_json
            json_prueba = json.dumps(factura_json)
            print("-Json generado: ", json_prueba)
            if formas_pago is not None and formas_pago !=[]:
                factura.formas_Pago = formas_pago
            factura.save()

            # Guardar el JSON en la carpeta "FE/json_facturas"
            json_path = os.path.join("FE/json_facturas", f"{factura.numero_control}.json")
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(factura_json, f, indent=4, ensure_ascii=False)

            return Response({
                "mensaje": "Factura generada correctamente",
                "factura_id": factura.id,
                "numero_control": factura.numero_control,
                "redirect": reverse('detalle_factura', args=[factura.id])
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error al generar la factura: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FirmarFacturaAPIView(APIView):
    """
    Firma la factura y, si ya está firmada, la envía a Hacienda.
    """

    def post(self, request, factura_id, format=None):
        print("-Inicio firma DTE")
        factura = get_object_or_404(FacturaElectronica, id=factura_id)

        token_data = Token_data.objects.filter(activado=True).first()
        if not token_data:
            return Response(
                {"error": "No hay token activo registrado en la base de datos."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not os.path.exists(CERT_PATH):
            return Response(
                {"error": "No se encontró el certificado en la ruta especificada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar y formatear el JSON original de la factura
        try:
            if isinstance(factura.json_original, dict):
                dte_json_str = json.dumps(factura.json_original, separators=(',', ':'))
            else:
                json_obj = json.loads(factura.json_original)
                dte_json_str = json.dumps(json_obj, separators=(',', ':'))
        except Exception as e:
            return Response(
                {"error": "El JSON original de la factura no es válido", "detalle": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Construir el payload con los parámetros requeridos
        payload = {
            "nit": "06142811001040",   # Nit del contribuyente
            "activo": True,            # Indicador activo
            "passwordPri": "3nCr!pT@d0Pr1v@d@",   # Contraseña de la llave privada
            "dteJson": factura.json_original    # JSON del DTE (se envía tal cual)
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(FIRMADOR_URL, json=payload, headers=headers)

            try:
                response_data = response.json()
            except Exception as e:
                response_data = {"error": "No se pudo parsear JSON", "detalle": response.text}

            # Guardar la respuesta en la factura para depuración y marcar como firmado
            factura.json_firmado = response_data
            factura.firmado = True
            factura.save()

            # Verificar si la firma fue exitosa
            if response.status_code == 200 and response_data.get("status") == "OK":
                # (Opcional) Guardar el JSON firmado en un archivo
                json_signed_path = f"FE/json_facturas_firmadas/{factura.codigo_generacion}.json"
                os.makedirs(os.path.dirname(json_signed_path), exist_ok=True)
                with open(json_signed_path, "w", encoding="utf-8") as json_file:
                    json.dump(response_data, json_file, indent=4, ensure_ascii=False)

                return Response({
                    "mensaje": "Factura firmada correctamente",
                    "redirect": reverse('detalle_factura', args=[factura_id])
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Error al firmar la factura",
                    "detalle": response_data
                }, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Error de conexión con el firmador",
                "detalle": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EnviarFacturaHaciendaAPIView(APIView):
    """
    Envía la factura firmada a Hacienda luego de autenticarse en su servicio.
    """

    def post(self, request, factura_id, format=None):
        # Paso 1: Autenticación contra el servicio de Hacienda
        nit_empresa = "06142811001040"
        pwd = "Q#3P9l5&@aF!gT2sA"
        auth_url = "https://api.dtes.mh.gob.sv/seguridad/auth"
        auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "MiAplicacionDjango/1.0"
        }
        auth_data = {"user": nit_empresa, "pwd": pwd}

        try:
            auth_response = requests.post(auth_url, data=auth_data, headers=auth_headers)
            try:
                auth_response_data = auth_response.json()
            except ValueError:
                return Response({
                    "error": "Error al decodificar la respuesta de autenticación",
                    "detalle": auth_response.text
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if auth_response.status_code == 200:
                token_body = auth_response_data.get("body", {})
                token = token_body.get("token")
                token_type = token_body.get("tokenType", "Bearer")
                roles = token_body.get("roles", [])

                # Si el token viene con el prefijo "Bearer " se remueve
                if token and token.startswith("Bearer "):
                    token = token[len("Bearer "):]

                # Actualizamos o creamos el objeto de token
                token_data_obj, created = Token_data.objects.update_or_create(
                    nit_empresa=nit_empresa,
                    defaults={
                        'password_hacienda': pwd,
                        'token': token,
                        'token_type': token_type,
                        'roles': roles,
                        'activado': True,
                        'fecha_caducidad': timezone.now() + timedelta(days=1)
                    }
                )
            else:
                return Response({
                    "error": "Error en la autenticación",
                    "detalle": auth_response_data.get("message", "Error no especificado")
                }, status=auth_response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Error de conexión con el servicio de autenticación",
                "detalle": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Paso 2: Enviar la factura firmada a Hacienda
        factura = get_object_or_404(FacturaElectronica, id=factura_id)
        
        token_data_obj = Token_data.objects.filter(activado=True).first()
        if not token_data_obj or not token_data_obj.token:
            return Response({"error": "No hay token activo para enviar la factura"}, status=status.HTTP_401_UNAUTHORIZED)

        codigo_generacion_str = str(factura.codigo_generacion)

        # Validación y limpieza del documento firmado
        documento_str = factura.json_firmado
        if not isinstance(documento_str, str):
            documento_str = json.dumps(documento_str)
        documento_str = documento_str.lstrip('\ufeff').strip()

        try:
            if isinstance(factura.json_firmado, str):
                firmado_data = json.loads(factura.json_firmado)
            else:
                firmado_data = factura.json_firmado
        except Exception as e:
            return Response({
                "error": "Error al parsear el documento firmado",
                "detalle": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        documento_token = firmado_data.get("body", "")
        if not documento_token:
            return Response({
                "error": "El documento firmado no contiene el token en 'body'"
            }, status=status.HTTP_400_BAD_REQUEST)

        documento_token = documento_token.strip()  # Limpiar espacios innecesarios

        envio_json = {
            "ambiente": "01",  # "00" para Pruebas; "01" para Producción
            "idEnvio": factura.id,
            "version": int(factura.json_original["identificacion"]["version"]),
            "tipoDte": str(factura.json_original["identificacion"]["tipoDte"]),
            "documento": documento_token,  # Enviamos solo el JWT firmado
            "codigoGeneracion": codigo_generacion_str
        }

        envio_headers = {
            "Authorization": f"Bearer {token_data_obj.token}",
            "User-Agent": "DjangoApp",
            "Content-Type": "application/json"
        }

        try:
            envio_response = requests.post(
                "https://api.dtes.mh.gob.sv/fesv/recepciondte",
                json=envio_json,
                headers=envio_headers
            )

            try:
                response_data = envio_response.json() if envio_response.text.strip() else {}
            except ValueError as e:
                response_data = {"raw": envio_response.text or "No content"}

            if envio_response.status_code == 200:
                # Actualizar campos de la factura según la respuesta
                factura.sello_recepcion = response_data.get("selloRecibido", "")
                factura.recibido_mh = True
                # Combinar la respuesta de Hacienda con el JSON original para guardar trazabilidad
                json_response_data = {"jsonRespuestaMh": response_data}
                json_nuevo = factura.json_original | json_response_data
                factura.json_original = json.loads(json.dumps(json_nuevo))
                factura.estado = True
                factura.save()
                return Response({
                    "mensaje": "Factura enviada con éxito",
                    "respuesta": response_data
                }, status=status.HTTP_200_OK)
            else:
                factura.estado = False
                factura.save()
                return Response({
                    "error": "Error al enviar la factura",
                    "status": envio_response.status_code,
                    "detalle": response_data
                }, status=envio_response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Error de conexión con Hacienda",
                "detalle": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

######################################################
# EVENTOS DE INVALIDACION Y CONTINGENCIA
######################################################
class InvalidarDteUnificadoAPIView(APIView):
    """
    Vista API unificada que realiza en un solo paso:
      1. Genera el DTE de invalidación (llama a invalidacion_dte_view)
      2. Firma el DTE de invalidación (llama a firmar_factura_anulacion_view)
      3. Envía el DTE firmado a Hacienda (llama a enviar_factura_invalidacion_hacienda_view)
    
    Se espera que se realice una petición POST a:
      /api/invalidar-firmar-enviar/<factura_id>/
    """
    def post(self, request, factura_id):
        try:
            # Paso 1: Llamar a la función de invalidación
            response_evento = invalidacion_dte_view(request, factura_id)
            if response_evento.status_code != 302:
                # Si el proceso de invalidación falla, retorna el error
                return Response(json.loads(response_evento.content),
                                status=response_evento.status_code)
            
            # Paso 2: Llamar a la función de firma de la factura de invalidación
            response_firma = firmar_factura_anulacion_view(request, factura_id)
            if response_firma.status_code != 302:
                return Response(json.loads(response_firma.content),
                                status=response_firma.status_code)
            
            # Paso 3: Llamar a la función que envía la factura firmada a Hacienda
            response_envio = enviar_factura_invalidacion_hacienda_view(request, factura_id)
            
            # Consultar el estado final del evento
            evento = EventoInvalidacion.objects.filter(factura__id=factura_id).first()
            if evento:
                mensaje = "Factura invalidada con éxito" if evento.estado else "No se pudo invalidar la factura"
            else:
                mensaje = "No se encontró el evento de invalidación para la factura"
            
            try:
                detalle = json.loads(response_envio.content)
            except Exception:
                detalle = response_envio.content.decode()
            
            return Response({
                "mensaje": mensaje,
                "detalle": detalle
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
def agregar_formas_pago(cod_fp, num_referencia, monto_fp, periodo_plazo, condicion_op, saldo_favor):
    print("-Formas de pago url: ", cod_fp)
    global formas_pago
    
    formas_pago = []
    try:
        forma_pago_id = cod_fp#request.GET.get("fp_id")
        num_referencia = num_referencia#request.GET.get("num_ref", None)
        if num_referencia == "":
            num_referencia = None
        monto_fp = monto_fp#request.GET.get("monto_fp")
        periodo_plazo = periodo_plazo#request.GET.get("periodo", None)
        condicion_operacion = condicion_op#request.GET.get("condicion_op", None)

        saldo_favor = saldo_favor#request.GET.get("saldo_favor_r", None)
        tiene_saldoF = False
        
        monto = Decimal("0.00")
        try:
            if saldo_favor is not None and saldo_favor !="":
                saldo = Decimal(saldo_favor)
                if  saldo.compare(Decimal("0.00")) > 0:
                    tiene_saldoF = True
                    codFormaPago = FormasPago.objects.get(codigo="99")
            else:
                saldo_favor = Decimal("0.00")
        except ConversionSyntax:
            print(f"Error: '{saldo}' no es un valor decimal válido.")
        
        if forma_pago_id:
            #formaPago = FormasPago.objects.get(id=forma_pago_id)
            formaPago = FormasPago.objects.get(codigo=forma_pago_id)
            if formaPago is not None:
                formas_pago_json  = {
                    "codigo": str(formaPago.codigo),
                    "montoPago": float(monto_fp),
                    "referencia": str(num_referencia),
                    "plazo": None
                }
        
        if tiene_saldoF:
            formas_pago_json["codigo"] = str(codFormaPago.codigo)
        if int(condicion_operacion) > 0 and int(condicion_operacion) == int(ID_CONDICION_OPERACION):
            formas_pago_json["codigo"] = None
            formas_pago_json["montoPago"] = float(monto)
            formas_pago_json["plazo"] = str(Plazo.objects.get(id=1).codigo) #Plazo por días
            formas_pago_json["periodo"] = int(periodo_plazo)
        else:
            formas_pago_json["periodo"] = None
            
        if formas_pago_json["codigo"] == "01": #Forma d pago billetes y monedas
            formas_pago_json["referencia"] = None
        
        formas_pago.append(formas_pago_json)
        print("-Formas de pago seleccionadas: ", formas_pago)
        
        return Response({'formasPago': formas_pago})
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return None

