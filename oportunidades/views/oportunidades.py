
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone as django_timezone
from datetime import datetime
from oportunidades.models import APIClient, OportunidadUsuario, TipoInnovacionAPI, FocoInnovacionAPI
import requests
import json
from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from oportunidades.forms.oportunidades_form import OportunidadesForm
from oportunidades.forms.oportunidades_update_form import Oportunidades_Update_Form
import os
from urllib.parse import unquote
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


from datetime import datetime

def list_oportunidades(request):
    user_email = request.session.get('user_email')

    if not user_email:
        return redirect('login:login')

    # Crear instancia de APIClient para la tabla 'oportunidad'
    client = APIClient('oportunidad')

    # Obtener tipos de innovación y focos de innovación usando las clases de API específicas
    try:
        focos = FocoInnovacionAPI.get_focos()
        tipos = TipoInnovacionAPI.get_tipo_innovacion()
    except Exception as e:
        messages.error(request, f"Error al obtener los tipos o focos de innovación: {e}")
        focos = tipos = []

    # Obtener los valores de los filtros desde los parámetros GET
    selected_tipo = request.GET.get('tipo_innovacion', '')
    selected_foco = request.GET.get('foco_innovacion', '')
    selected_estado = request.GET.get('estado', '')  # Recoger filtro de estado

    # Depuración: imprimir los valores de los filtros
    print(f"Filtro tipo_innovacion: {selected_tipo}")
    print(f"Filtro foco_innovacion: {selected_foco}")
    print(f"Filtro estado: {selected_estado}")

    # Crear una lista de condiciones WHERE para filtrar las oportunidades
    where_condition = []

    # Agregar las condiciones de filtro si están presentes
    if selected_tipo:
        where_condition.append(f"id_tipo_innovacion = {selected_tipo}")
    if selected_foco:
        where_condition.append(f"id_foco_innovacion = {selected_foco}")
    if selected_estado != '':
        if selected_estado == 'True':
            where_condition.append("estado = TRUE")
        elif selected_estado == 'False':
            where_condition.append("estado = FALSE")

    # Unir las condiciones para que la consulta sea válida, o dejar la lista vacía si no hay filtros
    where_condition = " AND ".join(where_condition) if where_condition else None

    try:
        # Obtener las oportunidades desde la API con los filtros
        print(f"Consultando la API con los filtros: {where_condition}")  # Depuración
        oportunidades = client.get_data(where_condition=where_condition)

        # Depuración: imprimir las oportunidades obtenidas
        print(f"Oportunidades obtenidas: {oportunidades}")

        # Crear diccionarios para obtener nombres por ID rápidamente
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

        # Añadir nombre de tipo de innovación y foco de innovación a las oportunidades
        for oportunidad in oportunidades:
            oportunidad['tipo_innovacion_nombre'] = tipos_dict.get(oportunidad.get('id_tipo_innovacion'), 'Desconocido')
            oportunidad['foco_innovacion_nombre'] = focos_dict.get(oportunidad.get('id_foco_innovacion'), 'Desconocido')

            # Formatear la fecha de creación
            fecha_creacion = oportunidad.get('fecha_creacion')
            print(f"Fecha original de creación: {fecha_creacion}")  # Depuración

            if fecha_creacion:
                try:
                    # Verificar si la fecha tiene hora, minuto y segundo
                    if 'T' in fecha_creacion:
                        # Eliminar la 'Z' si está presente
                        if fecha_creacion.endswith('Z'):
                            fecha_creacion = fecha_creacion[:-1]
                            print(f"Fecha sin 'Z': {fecha_creacion}")  # Depuración

                        # Convertir la fecha con hora
                        oportunidad['fecha_creacion'] = datetime.strptime(fecha_creacion, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
                        print(f"Fecha convertida: {oportunidad['fecha_creacion']}")  # Depuración
                    else:
                        # Convertir solo la fecha (sin hora)
                        oportunidad['fecha_creacion'] = datetime.strptime(fecha_creacion, "%Y-%m-%d").strftime("%Y-%m-%d")
                        print(f"Fecha convertida (sin hora): {oportunidad['fecha_creacion']}")  # Depuración
                except ValueError as ve:
                    print(f"Error en la conversión de la fecha: {ve}")  # Depuración
                    oportunidad['fecha_creacion'] = "Fecha inválida"

        if not oportunidades:
            messages.info(request, 'No hay oportunidades disponibles con los filtros seleccionados.')
        else:
            messages.info(request, f'Se obtuvieron {len(oportunidades)} oportunidades.')

    except Exception as e:
        messages.error(request, f'Error al obtener las oportunidades: {str(e)}')
        oportunidades = []

    # Verificar el rol del usuario logueado
    api_client_perfil = APIClient(table_name="perfil")
    try:
        perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")
        if perfil_data:
            rol_usuario = perfil_data[0].get('rol', '')
            is_experto = rol_usuario.lower() == 'experto'
        else:
            is_experto = False  # En caso de que no se encuentre el perfil
    except Exception as e:
        is_experto = False  # Si hay un error al obtener el perfil
        messages.error(request, f"Error al obtener el perfil del usuario: {str(e)}")

    # Enviar contexto a la plantilla
    context = {
        'oportunidades': oportunidades,
        'tipos': tipos,
        'focos': focos,
        'selected_tipo': selected_tipo,
        'selected_foco': selected_foco,
        'selected_estado': selected_estado,
        'user_email': user_email,
        'is_experto': is_experto,
    }

    return render(request, 'oportunidades/list_oportunidades.html', context)













# Función para insertar la relación entre el usuario y la oportunidad
def insertar_oportunidad_usuario(user_email, oportunidad_codigo):
    try:
        # Crear la relación entre la oportunidad y el usuario
        OportunidadUsuario.objects.create(email_usuario=user_email, codigo_oportunidad=oportunidad_codigo)
        print(f"Relación creada con éxito: Usuario {user_email} - Oportunidad {oportunidad_codigo}")
    except Exception as e:
        print(f"Error al insertar la relación: {e}")



def create_oportunidad(request):
    print("Iniciando la vista create_oportunidad")
    
    # Verificar si el usuario ha iniciado sesión
    user_email = request.session.get('user_email')
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para crear una oportunidad.')
        return redirect('login')
    
    messages.info(request, f'Usuario logueado: {user_email}')
    print(f'Usuario logueado: {user_email}')  # Depuración adicional

    # Inicializar las variables de focos y tipos de innovación
    focos_innovacion = []
    tipos_innovacion = []

    # Obtener dinámicamente los valores de foco_innovacion y tipo_innovacion desde las APIs
    try:
        print("Llamando a la API de foco de innovación...")
        client = APIClient('foco_innovacion')
        focos_innovacion = client.get_data()
        print("Focos de innovación recibidos:", focos_innovacion)

        if 'result' in focos_innovacion:
            try:
                focos_innovacion = json.loads(focos_innovacion['result'][0]['result'])
                print("Focos de innovación decodificados:", focos_innovacion)
            except json.JSONDecodeError as e:
                messages.error(request, f'Error al decodificar los focos de innovación: {e}')
                print(f'Error al decodificar los focos de innovación: {e}')
        else:
            messages.error(request, 'No se encontraron focos de innovación en la respuesta de la API.')
        
        print("Llamando a la API de tipo de innovación...")
        client = APIClient('tipo_innovacion')
        tipos_innovacion = client.get_data()
        print("Tipos de innovación recibidos:", tipos_innovacion)

        if 'result' in tipos_innovacion:
            try:
                tipos_innovacion = json.loads(tipos_innovacion['result'][0]['result'])
                print("Tipos de innovación decodificados:", tipos_innovacion)
            except json.JSONDecodeError as e:
                messages.error(request, f'Error al decodificar los tipos de innovación: {e}')
                print(f'Error al decodificar los tipos de innovación: {e}')
        else:
            messages.error(request, 'No se encontraron tipos de innovación en la respuesta de la API.')

        if not focos_innovacion or not tipos_innovacion:
            messages.info(request, 'No hay focos o tipos de innovación disponibles.')
            print("No hay focos o tipos de innovación disponibles.")
    except Exception as e:
        messages.error(request, f'Error al obtener los datos: {e}')
        print(f'Error al obtener los datos: {e}')
    
    # Asegurarse de que el formulario se inicialice
    if request.method == 'POST':
        form = OportunidadesForm(request.POST, request.FILES)
        
        # Mostrar los datos del formulario recibido
        messages.info(request, f'Formulario recibido: {request.POST}')
        print(f'Formulario recibido: {request.POST}')  # Depuración adicional

        if form.is_valid():
            print("Formulario válido")
            print(form.cleaned_data)  # Muestra los datos validados
            messages.info(request, f'Formulario válido, procesando datos...')

            try:
                foco_innovacion_name = int(form.cleaned_data['id_foco_innovacion'])
                tipo_innovacion_name = int(form.cleaned_data['id_tipo_innovacion'])
            except ValueError as e:
                messages.error(request, f'Error al convertir los valores a enteros: {e}')
                print(f'Error al convertir los valores a enteros: {e}')
                return redirect('oportunidades:create')

            try:
                foco_innovacion = next((foco for foco in focos_innovacion if foco['id_foco_innovacion'] == foco_innovacion_name), None)
                tipo_innovacion = next((tipo for tipo in tipos_innovacion if tipo['id_tipo_innovacion'] == tipo_innovacion_name), None)

                if foco_innovacion is None:
                    messages.error(request, f'Foco de innovación con ID "{foco_innovacion_name}" no encontrado.')
                    print(f'Foco de innovación con ID "{foco_innovacion_name}" no encontrado.')

                if tipo_innovacion is None:
                    messages.error(request, f'Tipo de innovación con ID "{tipo_innovacion_name}" no encontrado.')
                    print(f'Tipo de innovación con ID "{tipo_innovacion_name}" no encontrado.')

                if foco_innovacion and tipo_innovacion:
                    messages.info(request, f'Foco de Innovación encontrado: {foco_innovacion}, Tipo de Innovación encontrado: {tipo_innovacion}')
                    print(f'Foco de Innovación encontrado: {foco_innovacion}, Tipo de Innovación encontrado: {tipo_innovacion}')

            except Exception as e:
                messages.error(request, f'Error al obtener Foco de Innovación o Tipo de Innovación: {e}')
                print(f'Error al obtener Foco de Innovación o Tipo de Innovación: {e}')
                return redirect('oportunidades:create')
            
            client = APIClient('oportunidad')

            json_data = {
                'titulo': form.cleaned_data['titulo'],
                'descripcion': form.cleaned_data['descripcion'],
                'palabras_claves': form.cleaned_data['palabras_claves'],
                'recursos_requeridos': form.cleaned_data['recursos_requeridos'],
                'fecha_creacion': form.cleaned_data['fecha_creacion'].isoformat(),
                'id_foco_innovacion': foco_innovacion['id_foco_innovacion'] if foco_innovacion else None,
                'id_tipo_innovacion': tipo_innovacion['id_tipo_innovacion'] if tipo_innovacion else None,
                'creador_por': user_email
            }

            messages.info(request, f'Datos preparados para la API: {json_data}')
            print(f'Datos preparados para la API: {json_data}')  # Depuración adicional

            if 'archivo_multimedia' in request.FILES:
                file = request.FILES['archivo_multimedia']
                try:
                    file_name = default_storage.save(file.name, ContentFile(file.read()))
                    file_url = default_storage.url(file_name)
                    json_data['archivo_multimedia'] = file_url
                    messages.info(request, f'Archivo multimedia cargado con éxito: {file.name}')
                    print(f'Archivo multimedia cargado con éxito: {file.name}')  # Depuración adicional
                except Exception as e:
                    messages.error(request, f'Error al leer el archivo multimedia: {e}')
                    print(f'Error al leer el archivo multimedia: {e}')
                    return redirect('oportunidades:create')

            try:
                messages.info(request, f'Enviando datos a la API: {json_data}')
                print(f'Enviando datos a la API: {json_data}')  # Depuración adicional
                response = client.insert_data(json_data=json_data)
                
                if isinstance(response, str):
                    try:
                        response = json.loads(response)
                        messages.info(request, f'Respuesta decodificada: {response}')
                        print("Respuesta de la API:", response)
                    except json.JSONDecodeError as e:
                        messages.error(request, f'Error al decodificar la respuesta de la API: {e}')
                        print(f'Error al decodificar la respuesta de la API: {e}')
                        return redirect('oportunidades:create')

                messages.info(request, f'Respuesta de la API: {response}')
                print(f'Respuesta de la API: {response}')

                if 'outputParams' in response and response['outputParams'].get('mensaje') == "Inserción realizada correctamente.":
                    messages.success(request, '¡Oportunidad creada con éxito!')
                    print('¡Oportunidad creada con éxito!')
                    return redirect('oportunidades:list_oportunidad')
                else:
                    messages.error(request, f'Error al crear la oportunidad: {response.get("message", "No se recibió mensaje de error.")}')
                    print(f'Error al crear la oportunidad: {response.get("message", "No se recibió mensaje de error.")}')
            except Exception as e:
                messages.error(request, f'Error al enviar los datos a la API: {e}')
                print(f'Error al enviar los datos a la API: {e}')
        else:
            messages.error(request, 'Formulario inválido, revisa los datos ingresados.')
            print(f'Formulario inválido: {form.errors}')
            return redirect('oportunidades:create')

    # Si el método es GET o si el formulario no es válido, inicializar el formulario vacío
    form = OportunidadesForm()

    # Retornar el formulario y los datos de las APIs al contexto
    return render(request, 'oportunidades/create.html', {'form': form, 'focos_innovacion': focos_innovacion, 'tipos_innovacion': tipos_innovacion})



def delete_oportunidad(request, codigo_oportunidad):
    # Verifica si el usuario está autenticado
    user_email = request.session.get('user_email')
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para eliminar una oportunidad.')
        return redirect('login:login')

    # Instancia del cliente API
    client = APIClient('oportunidad')

    # Obtener la oportunidad de la API
    oportunidad = client.get_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}")
    
    if not oportunidad:
        messages.error(request, 'Oportunidad no encontrada.')
        return redirect('oportunidades:list_oportunidad')

    oportunidad_data = oportunidad[0]  # Suponemos que `oportunidad` es una lista con un solo elemento

    # Obtener los focos y tipos de innovación desde las APIs correspondientes
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()

    # Crear diccionarios para obtener los nombres por ID
    focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
    tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

    # Añadir nombres de tipo y foco a la oportunidad
    oportunidad_data['tipo_innovacion_nombre'] = tipos_dict.get(oportunidad_data['id_tipo_innovacion'], 'Desconocido')
    oportunidad_data['foco_innovacion_nombre'] = focos_dict.get(oportunidad_data['id_foco_innovacion'], 'Desconocido')

    # Verificar el rol del usuario logueado consultando la tabla 'perfil'
    api_client_perfil = APIClient(table_name="perfil")
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

    # Verificar si el perfil contiene información y si el rol es 'Experto'
    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
        is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
    else:
        is_experto = False  # En caso de que no se encuentre el perfil

    # Si el método es POST, proceder con la eliminación
    if request.method == 'POST':
        mensaje_experto = request.POST.get('mensaje_experto', None)  # Obtener el mensaje opcional

        try:
            # Llamada para eliminar la oportunidad a través de la API
            client.delete_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}")

            # Eliminar el archivo de la carpeta media usando la URL almacenada
            archivo_url = oportunidad_data.get('archivo_multimedia')  # Obtén la URL del archivo de la base de datos

            # Imprimir para depurar la URL obtenida
            print(f"Archivo multimedia URL: {archivo_url}")

            if archivo_url:
                # Decodificar la URL para obtener la ruta correcta del archivo
                archivo_url_decoded = unquote(archivo_url)
                
                # Corregir la construcción de la ruta física del archivo eliminando la duplicación de "media"
                archivo_path = os.path.join(settings.MEDIA_ROOT, archivo_url_decoded.lstrip('/media/'))

                # Imprimir para verificar la ruta física del archivo
                print(f"Ruta física del archivo decodificado: {archivo_path}")

                if os.path.exists(archivo_path):
                    print(f"Archivo encontrado. Procediendo a eliminarlo.")
                    os.remove(archivo_path)
                    messages.success(request, 'Archivo de oportunidad eliminado con éxito.')
                else:
                    print(f"El archivo no existe en la ruta: {archivo_path}")
                    messages.warning(request, 'El archivo no se encontró en la carpeta media.')
            else:
                print("No se encontró la URL del archivo multimedia.")

            # Crear la notificación con el mensaje del experto (si se proporciona)
            create_notification(user_email, 'oportunidad', oportunidad_data['titulo'], 'eliminar', oportunidad_data['creador_por'], mensaje_experto)

            # Mostrar mensaje de éxito
            messages.success(request, 'Oportunidad eliminada con éxito.')
            return redirect('oportunidades:list_oportunidad')

        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP al eliminar la oportunidad: {e}")
            messages.error(request, f'Error HTTP al eliminar la oportunidad: {e}')
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud HTTP: {e}")
            messages.error(request, f'Error en la solicitud HTTP: {e}')
        except Exception as e:
            print(f"Error inesperado al eliminar la oportunidad: {e}")
            messages.error(request, f'Error inesperado al eliminar la oportunidad: {e}')

    # Si no es POST, mostrar la vista de confirmación de eliminación
    return render(request, 'oportunidades/delete_oportunidades.html', {'oportunidad': oportunidad_data, 'is_experto': is_experto})





def detail_oportunidad(request, codigo_oportunidad):
    user_email = request.session.get('user_email')

    # Verificar si el email de usuario está presente en la sesión
    if not user_email:
        return redirect('login:login')
    
    try:
        # Obtener la oportunidad desde la API usando la clase OportunidadUsuario
        oportunidad_response = OportunidadUsuario.get_oportunidad_by_codigo(codigo_oportunidad)
        
        # Imprimir la respuesta completa de la API para verificar su estructura

        # Verificar si la respuesta es válida
        if not oportunidad_response:
            return render(request, 'oportunidades/detail_oportunidades.html', {'error': 'Oportunidad no encontrada.'})

        # Verificar que haya datos en la respuesta
        if 'codigo_oportunidad' not in oportunidad_response:
            return render(request, 'oportunidades/detail_oportunidades.html', {'error': 'Datos de la oportunidad no disponibles.'})

        # Datos válidos, extraemos la información
        oportunidad_data = oportunidad_response

        # Extraer los ID de tipo y foco de innovación
        id_tipo_innovacion = oportunidad_data.get('id_tipo_innovacion')
        id_foco_innovacion = oportunidad_data.get('id_foco_innovacion')


        # Obtener focos y tipos de innovación desde las APIs
        focos = FocoInnovacionAPI.get_focos()
        tipos = TipoInnovacionAPI.get_tipo_innovacion()


        # Crear diccionarios para obtener nombres por ID
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

        # Obtener los nombres de tipo y foco por los IDs
        tipo_innovacion_nombre = tipos_dict.get(id_tipo_innovacion, 'Desconocido')
        foco_innovacion_nombre = focos_dict.get(id_foco_innovacion, 'Desconocido')

        # Añadir los nombres de tipo y foco a la oportunidad
        oportunidad_data['tipo_innovacion_nombre'] = tipo_innovacion_nombre
        oportunidad_data['foco_innovacion_nombre'] = foco_innovacion_nombre

        # Pasar todos los datos a la plantilla
        return render(request, 'oportunidades/detail_oportunidades.html', {
            'oportunidad': oportunidad_data,
            'tipo_innovacion': tipo_innovacion_nombre,
            'foco_innovacion': foco_innovacion_nombre,
        })

    except Exception as e:
        print(f"Error inesperado: {e}")
        return render(request, 'oportunidades/detail_oportunidades.html', {'error': f'Error al cargar los detalles: {e}'})




def update_oportunidad(request, codigo_oportunidad):
    user_email = request.session.get('user_email')  # Obtener el correo electrónico del usuario autenticado
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para actualizar una oportunidad.')
        return redirect('login:login')

    # Verificar si el usuario es experto
    api_client_perfil = APIClient(table_name="perfil")
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
        is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
    else:
        is_experto = False  # En caso de que no se encuentre el perfil

    # Llamada a la API para obtener los datos de la oportunidad
    client = APIClient('oportunidad')
    oportunidad = client.get_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}")

    if not oportunidad:
        messages.error(request, 'Oportunidad no encontrada.')
        return redirect('oportunidades:list_oportunidad')

    oportunidad_data = oportunidad[0]  # Asumimos que es una lista de diccionarios

    # Obtener focos y tipos de innovación
    try:
        focos_innovacion = FocoInnovacionAPI.get_focos()
        tipos_innovacion = TipoInnovacionAPI.get_tipo_innovacion()

        # Crear diccionarios para obtener nombres por ID
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos_innovacion}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos_innovacion}

        # Añadir los nombres de tipo y foco a los datos de la oportunidad
        oportunidad_data['tipo_innovacion_nombre'] = tipos_dict.get(oportunidad_data['id_tipo_innovacion'], 'Desconocido')
        oportunidad_data['foco_innovacion_nombre'] = focos_dict.get(oportunidad_data['id_foco_innovacion'], 'Desconocido')

    except Exception as e:
        messages.error(request, f'Error al obtener datos de innovación: {e}')
        return redirect('oportunidades:list_oportunidad')

    # Procesamiento del formulario
    if request.method == 'POST':
        form = Oportunidades_Update_Form(request.POST, request.FILES)
        if form.is_valid():
            try:
                json_data = {
                    'titulo': form.cleaned_data['titulo'],
                    'descripcion': form.cleaned_data['descripcion'],
                    'palabras_claves': form.cleaned_data['palabras_claves'],
                    'recursos_requeridos': form.cleaned_data['recursos_requeridos'],
                    'fecha_creacion': form.cleaned_data['fecha_creacion'].isoformat(),
                    'id_foco_innovacion': form.cleaned_data['id_foco_innovacion'],
                    'id_tipo_innovacion': form.cleaned_data['id_tipo_innovacion'],
                    'creador_por': oportunidad_data['creador_por']  # Mantener al creador original
                }

                # Adjuntar archivo multimedia si existe
                if 'archivo_multimedia' in request.FILES:
                    file = request.FILES['archivo_multimedia']
                    json_data['archivo_multimedia'] = file.name
                else:
                    json_data['archivo_multimedia'] = oportunidad_data['archivo_multimedia']

                # Actualizar datos en la API
                response = client.auto_update_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}", json_data=json_data)

                if response:
                    # Verificar si se debe agregar un mensaje del experto
                    mensaje_experto = form.cleaned_data.get('mensaje_experto')
                    print(f"mensaje_experto recibido: {mensaje_experto}")  # Agregar print para depurar
                    
                    # Crear notificación después de actualizar la oportunidad
                    create_notification(
                        experto_email=user_email,  # Correo del experto que realizó la actualización
                        tipo_entidad='oportunidad',  # Tipo de entidad
                        entidad_titulo=form.cleaned_data['titulo'],  # Título de la oportunidad
                        accion='editar',  # Acción realizada
                        usuario_email=oportunidad_data['creador_por'],  # Correo del creador original
                        mensaje_experto=mensaje_experto  # Pasar el mensaje del experto
                    )

                    messages.success(request, 'Oportunidad actualizada con éxito.')
                    return redirect('oportunidades:list_oportunidad')
                else:
                    messages.info(request, 'No hubo cambios en los datos.')

            except Exception as e:
                messages.error(request, f'Error al actualizar la oportunidad: {e}')

        else:
            messages.error(request, 'Formulario inválido. Por favor, revisa los datos ingresados.')

    else:
        # Inicializar formulario con datos actuales
        form = Oportunidades_Update_Form(initial=oportunidad_data)

        # Si el usuario no es experto, eliminar el campo 'mensaje_experto'
        if not is_experto:
            form.fields.pop('mensaje_experto', None)

    return render(request, 'oportunidades/update_oportunidades.html', {'form': form, 'is_experto': is_experto})

def create_notification(experto_email, tipo_entidad, entidad_titulo, accion, usuario_email, mensaje_experto=None):
    try:
        # Crear el mensaje por defecto
        if accion == 'eliminar':
            mensaje_default = f"El experto ha eliminado tu {tipo_entidad}: {entidad_titulo}"
        elif accion == 'editar':
            mensaje_default = f"El experto ha editado tu {tipo_entidad}: {entidad_titulo}"
        elif accion == 'confirmar':
            mensaje_default = f"El experto ha confirmado tu {tipo_entidad}: {entidad_titulo}"
        elif accion == 'actualizar':  # Añadir el caso para 'actualizar'
            mensaje_default = f"El experto ha actualizado tu {tipo_entidad}: {entidad_titulo}"
        else:
            mensaje_default = "Acción desconocida"

        # Si el experto proporciona un mensaje, usarlo, sino el mensaje por defecto
        print(f"mensaje_experto recibido en create_notification: {mensaje_experto}")  # Agregar print para depurar
        mensaje_final = mensaje_experto if mensaje_experto else mensaje_default

        # Crear los datos de la notificación
        notificacion_data = {
            'usuario_email': usuario_email,  # Correo del creador de la entidad
            'tipo_entidad': tipo_entidad,  # Tipo de entidad (idea u oportunidad)
            'entidad_titulo': entidad_titulo,  # Título de la entidad
            'mensaje_default': mensaje_default,
            'mensaje_experto': mensaje_final,  # Usar el mensaje_final para el experto (puede ser el proporcionado o el default)
            'experto_email': experto_email,  # Correo del experto que realizó la acción
            'fecha_creacion': datetime.now().isoformat(),  # Convertir la fecha a formato ISO
            'leida': False,  # Inicialmente la notificación no ha sido leída
            'accion': accion  # Acción realizada: eliminar, editar, confirmar
        }

        # Crear el cliente de la API con el nombre de la tabla 'notificaciones'
        client = APIClient('notificaciones')

        # Insertar la notificación
        response = client.insert_data(json_data=notificacion_data)

        # Verificar si la notificación fue creada correctamente
        if response:
            print("Notificación creada con éxito.")
        else:
            print("Error al crear la notificación.")
    
    except Exception as e:
        print(f"Error al crear la notificación: {e}")


def confirmar_oportunidad(request, codigo_oportunidad):
    print("Inicio de la función confirmar_oportunidad")
    
    user_email = request.session.get('user_email')  # Obtener el correo electrónico del usuario autenticado
    print(f"Correo electrónico del usuario: {user_email}")
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para confirmar la oportunidad.')
        return redirect('login:login')

    # Verificar si el usuario es experto
    try:
        print("Consultando datos del perfil del usuario...")
        api_client_perfil = APIClient(table_name="perfil")
        perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")
        print(f"Datos del perfil obtenidos: {perfil_data}")
    except Exception as e:
        print(f"Error al consultar perfil: {e}")
        perfil_data = []

    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
        is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
        print(f"Rol del usuario: {rol_usuario}, ¿Es experto?: {is_experto}")
    else:
        is_experto = False

    # Llamada a la API para obtener los datos de la oportunidad
    try:
        print(f"Consultando oportunidad con código: {codigo_oportunidad}...")
        client = APIClient('oportunidad')
        oportunidad = client.get_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}")
        print(f"Oportunidad obtenida: {oportunidad}")
    except Exception as e:
        print(f"Error al consultar la oportunidad: {e}")
        oportunidad = []

    if not oportunidad:
        messages.error(request, 'Oportunidad no encontrada.')
        return redirect('oportunidades:list_oportunidad')

    oportunidad_data = oportunidad[0]  # Asumimos que es una lista de diccionarios
    print(f"Datos de la oportunidad: {oportunidad_data}")

    # Verificación de creador_por
    usuario_email = oportunidad_data.get('creador_por')
    if not usuario_email:
        messages.error(request, 'No se encontró el correo del usuario asociado a esta oportunidad.')
        return redirect('oportunidades:list_oportunidad')

    # Procesamiento del formulario
    if request.method == 'POST' and 'confirmar' in request.POST:
        print("Formulario POST recibido, procesando confirmación de la oportunidad...")
        try:
            # Cambiar el estado de la oportunidad a True
            json_data = {'estado': True}
            print(f"Actualizando estado de la oportunidad a: {json_data}")
            response = client.auto_update_data(where_condition=f"codigo_oportunidad = {codigo_oportunidad}", json_data=json_data)
            print(f"Respuesta de actualización: {response}")

            if response:
                # Transferir oportunidad a proyecto si se confirma
                print("Confirmación exitosa, transfiriendo oportunidad a proyecto...")
                proyecto_client = APIClient('proyecto')
                fecha_aprobacion = django_timezone.now().isoformat()

                proyecto_data = {
                    "tipo_origen": "oportunidad",
                    "id_origen": codigo_oportunidad,
                    "titulo": oportunidad_data.get('titulo'),
                    "descripcion": oportunidad_data.get('descripcion'),
                    "fecha_creacion": oportunidad_data.get('fecha_creacion'),
                    "palabras_claves": oportunidad_data.get('palabras_claves'),
                    "recursos_requeridos": oportunidad_data.get('recursos_requeridos'),
                    "archivo_multimedia": oportunidad_data.get('archivo_multimedia'),
                    "creador_por": oportunidad_data.get('creador_por'),
                    "id_tipo_innovacion": oportunidad_data.get('id_tipo_innovacion'),
                    "id_foco_innovacion": oportunidad_data.get('id_foco_innovacion'),
                    "estado": True,
                    "fecha_aprobacion": fecha_aprobacion,
                    "aprobado_por": user_email,
                }
                print(f"Datos del proyecto a insertar: {proyecto_data}")

                proyecto_response = proyecto_client.insert_data(json_data=proyecto_data)
                print(f"Respuesta de inserción de proyecto: {proyecto_response}")

                if proyecto_response:
                    messages.success(request, 'La oportunidad ha sido confirmada y transferida a proyecto exitosamente.')
                    return redirect('oportunidades:list_oportunidad')
                else:
                    messages.error(request, 'La oportunidad fue confirmada, pero hubo un error al crear el proyecto.')

            else:
                messages.error(request, 'Hubo un error al confirmar la oportunidad.')

        except Exception as e:
            print(f"Excepción durante la confirmación de la oportunidad: {e}")
            messages.error(request, f'Error al confirmar la oportunidad: {e}')

    return render(request, 'oportunidades/confirmar_oportunidades.html', {'oportunidad': oportunidad_data, 'is_experto': is_experto})
