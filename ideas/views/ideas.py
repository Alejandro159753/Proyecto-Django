from django.shortcuts import render, redirect
from django.contrib import messages
from ideas.models import APIClient, TipoInnovacionAPI, FocoInnovacionAPI, IdeaUsuario
from ideas.forms.ideas_form import IdeasForm
from ideas.forms.ideas_update_form import Ideas_update_Form
import requests
import json
from datetime import datetime
from django.utils import timezone as django_timezone
from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from urllib.parse import unquote
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def list_ideas(request):
    # Obtener el email del usuario desde la sesión
    user_email = request.session.get('user_email')

    if not user_email:
        return redirect('login:login')
    
    # Crear instancia de APIClient para la tabla 'idea'
    client = APIClient('idea')
    
    # Obtener tipos de innovación y focos de innovación usando las clases de API específicas
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()

    # Obtener los valores de los filtros
    selected_tipo = request.GET.get('tipo_innovacion', '')
    selected_foco = request.GET.get('foco_innovacion', '')
    selected_estado = request.GET.get('estado', '')  # Recoger filtro de estado

    # Crear una lista de condiciones WHERE para filtrar las ideas
    where_condition = []

    if selected_tipo:
        where_condition.append(f"id_tipo_innovacion = {selected_tipo}")
    if selected_foco:
        where_condition.append(f"id_foco_innovacion = {selected_foco}")
    if selected_estado != '':
        if selected_estado == 'True':
            where_condition.append("estado = TRUE")
        elif selected_estado == 'False':
            where_condition.append("estado = FALSE")

    where_condition = " AND ".join(where_condition) if where_condition else ""

    try:
        # Obtener las ideas desde la API con los filtros
        ideas = client.get_data(where_condition=where_condition)

        # Crear diccionarios para obtener nombres por ID rápidamente
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

        # Asociar los nombres de tipo y foco a cada idea
        for idea in ideas:
            idea['tipo_innovacion_nombre'] = tipos_dict.get(idea.get('id_tipo_innovacion'), 'Desconocido')
            idea['foco_innovacion_nombre'] = focos_dict.get(idea.get('id_foco_innovacion'), 'Desconocido')

            # Formatear la fecha de creación
            fecha_creacion = idea.get('fecha_creacion')
            if fecha_creacion:
                print(f"Valor de fecha_creacion antes de procesar: '{fecha_creacion}'")  # Depuración

                try:
                    # Intentar quitar cualquier 'Z' al final de la fecha (en caso de estar en UTC)
                    if fecha_creacion.endswith('Z'):
                        fecha_creacion = fecha_creacion[:-1]
                    print(f"Valor de fecha_creacion después de quitar 'Z': '{fecha_creacion}'")  # Depuración

                    # Intentar convertir la fecha al formato sin hora ni zona horaria
                    try:
                        dt = datetime.strptime(fecha_creacion, "%Y-%m-%d").date()  # Solo convertimos a fecha
                        idea['fecha_creacion'] = dt.strftime("%Y-%m-%d")
                    except ValueError:
                        print(f"Error al convertir la fecha con formato esperado: {fecha_creacion}")
                        idea['fecha_creacion'] = "Fecha inválida"

                except Exception as e:
                    # Capturar errores y asignar "Fecha inválida"
                    print(f"Error al procesar la fecha: {e} - Fecha original: {fecha_creacion}")
                    idea['fecha_creacion'] = "Fecha inválida"

        # Verificar si hay ideas y mostrar mensajes
        if not ideas:
            messages.info(request, 'No hay ideas disponibles.')
        else:
            messages.info(request, f'Se obtuvieron {len(ideas)} ideas.')

    except Exception as e:
        messages.error(request, f'Error al obtener las ideas: {e}')
        ideas = []

    # Verificar el rol del usuario logueado consultando la tabla 'perfil'
    api_client_perfil = APIClient(table_name="perfil")
    
    # Obtenemos el perfil del usuario logueado (basado en su email)
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")
    
    # Verificar si el perfil contiene información y si el rol es 'Experto'
    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')  # Obtener el nombre del rol (que es un string)
        is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
    else:
        is_experto = False  # En caso de que no se encuentre el perfil

    # Pasar los datos al contexto
    context = {
        'ideas': ideas,
        'tipos': tipos,
        'focos': focos,
        'selected_tipo': selected_tipo,
        'selected_foco': selected_foco,
        'selected_estado': selected_estado,
        'user_email': user_email,
        'is_experto': is_experto,  # Agregar esta variable al contexto
    }

    return render(request, 'ideas/list.html', context)





# Función para insertar la relación entre el usuario y la idea
def insertar_idea_usuario(user_email, idea_codigo):
    try:
        # Crear la relación entre la idea y el usuario
        IdeaUsuario.objects.create(email_usuario=user_email, codigo_idea=idea_codigo)
    except Exception as e:
        messages.error(requests.request, f'Error al insertar la relación: {e}')

def create_idea(request):
    # Verificar si el usuario ha iniciado sesión
    user_email = request.session.get('user_email')
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para crear una idea.')
        return redirect('login')
    
    messages.info(request, f'Usuario logueado: {user_email}')

    # Obtener dinámicamente los valores de foco_innovacion y tipo_innovacion desde las APIs
    try:
        client = APIClient('foco_innovacion')
        focos_innovacion = client.get_data()

        if 'result' in focos_innovacion:
            try:
                focos_innovacion = json.loads(focos_innovacion['result'][0]['result'])
            except json.JSONDecodeError as e:
                messages.error(request, f'Error al decodificar los focos de innovación: {e}')
        else:
            messages.error(request, 'No se encontraron focos de innovación en la respuesta de la API.')
        
        client = APIClient('tipo_innovacion')
        tipos_innovacion = client.get_data()

        if 'result' in tipos_innovacion:
            try:
                tipos_innovacion = json.loads(tipos_innovacion['result'][0]['result'])
            except json.JSONDecodeError as e:
                messages.error(request, f'Error al decodificar los tipos de innovación: {e}')
        else:
            messages.error(request, 'No se encontraron tipos de innovación en la respuesta de la API.')

        if not focos_innovacion or not tipos_innovacion:
            messages.info(request, 'No hay focos o tipos de innovación disponibles.')
    except Exception as e:
        messages.error(request, f'Error al obtener los datos: {e}')
        focos_innovacion = []
        tipos_innovacion = []

    if request.method == 'POST':
        form = IdeasForm(request.POST, request.FILES)

        # Mostrar los datos del formulario recibido
        messages.info(request, f'Formulario recibido: {request.POST}')

        if form.is_valid():
            messages.info(request, f'Formulario válido, procesando datos...')

            try:
                foco_innovacion_name = int(form.cleaned_data['id_foco_innovacion'])
                tipo_innovacion_name = int(form.cleaned_data['id_tipo_innovacion'])
            except ValueError as e:
                messages.error(request, f'Error al convertir los valores a enteros: {e}')
                return redirect('ideas:create')

            try:
                foco_innovacion = next((foco for foco in focos_innovacion if foco['id_foco_innovacion'] == foco_innovacion_name), None)
                tipo_innovacion = next((tipo for tipo in tipos_innovacion if tipo['id_tipo_innovacion'] == tipo_innovacion_name), None)

                if foco_innovacion is None:
                    messages.error(request, f'Foco de innovación con ID "{foco_innovacion_name}" no encontrado.')
                if tipo_innovacion is None:
                    messages.error(request, f'Tipo de innovación con ID "{tipo_innovacion_name}" no encontrado.')

                if foco_innovacion and tipo_innovacion:
                    messages.info(request, f'Foco de Innovación encontrado: {foco_innovacion}, Tipo de Innovación encontrado: {tipo_innovacion}')

            except Exception as e:
                messages.error(request, f'Error al obtener Foco de Innovación o Tipo de Innovación: {e}')
                return redirect('ideas:create')
            
            client = APIClient('idea')

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

            if 'archivo_multimedia' in request.FILES:
                file = request.FILES['archivo_multimedia']
                try:
                    file_name = default_storage.save(file.name, ContentFile(file.read()))
                    file_url = default_storage.url(file_name)
                    json_data['archivo_multimedia'] = file_url
                    messages.info(request, f'Archivo multimedia cargado con éxito: {file.name}')
                except Exception as e:
                    messages.error(request, f'Error al leer el archivo multimedia: {e}')
                    return redirect('ideas:create')

            try:
                messages.info(request, f'Enviando datos a la API: {json_data}')
                response = client.insert_data(json_data=json_data)
                
                if isinstance(response, str):
                    try:
                        response = json.loads(response)
                        messages.info(request, f'Respuesta decodificada: {response}')
                    except json.JSONDecodeError as e:
                        messages.error(request, f'Error al decodificar la respuesta de la API: {e}')
                        return redirect('ideas:create')

                messages.info(request, f'Respuesta de la API: {response}')

                if 'outputParams' in response and response['outputParams'].get('mensaje') == "Inserción realizada correctamente.":
                    messages.success(request, '¡Idea creada con éxito!')
                    return redirect('ideas:list')
                else:
                    messages.error(request, f'Error al crear la idea: {response.get("message", "No se recibió mensaje de error.")}')
            except Exception as e:
                messages.error(request, f'Error al enviar los datos a la API: {e}')
        else:
            messages.error(request, 'Formulario inválido, revisa los datos ingresados.')
            return redirect('ideas:create')

    form = IdeasForm()
    return render(request, 'ideas/create.html', {'form': form, 'focos_innovacion': focos_innovacion, 'tipos_innovacion': tipos_innovacion})


def delete_idea(request, pk):
    # Obtener el correo electrónico del usuario desde la sesión
    user_email = request.session.get('user_email')

    if not user_email:
        return redirect('login:login')

    # Crear cliente para la API de ideas
    client = APIClient('idea')
    
    # Obtener la idea desde la API (cambiado 'id' por 'codigo_idea')
    idea = client.get_data(where_condition=f"codigo_idea = {pk}")
    
    if not idea:
        messages.error(request, 'Idea no encontrada.')
        return redirect('ideas:list')

    idea_data = idea[0]  # Asumimos que idea es una lista de diccionarios

    # Obtener focos y tipos de innovación
    focos = FocoInnovacionAPI.get_focos()
    tipos = TipoInnovacionAPI.get_tipo_innovacion()

    # Crear diccionarios para obtener nombres por ID
    focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
    tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

    # Añadir los nombres de tipo y foco a la idea
    idea_data['tipo_innovacion_nombre'] = tipos_dict.get(idea_data['id_tipo_innovacion'], 'Desconocido')
    idea_data['foco_innovacion_nombre'] = focos_dict.get(idea_data['id_foco_innovacion'], 'Desconocido')

    # Verificar el rol del usuario logueado consultando la tabla 'perfil'
    api_client_perfil = APIClient(table_name="perfil")
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

    # Verificar si el perfil contiene información y si el rol es 'Experto'
    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
        is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
    else:
        is_experto = False  # En caso de que no se encuentre el perfil

    # Si es un POST, proceder con la eliminación
    if request.method == 'POST':
        mensaje_experto = request.POST.get('mensaje_experto', None)  # Obtener el mensaje opcional

        try:
            # Eliminar la idea
            client.delete_data(where_condition=f"codigo_idea = {pk}")

            # Eliminar archivo multimedia asociado si existe
            archivo_url = idea_data.get('archivo_multimedia')  # Obtén la URL del archivo multimedia de la idea

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
                    messages.success(request, 'Archivo de la idea eliminado con éxito.')
                else:
                    print(f"El archivo no existe en la ruta: {archivo_path}")
                    messages.warning(request, 'El archivo no se encontró en la carpeta media.')
            else:
                print("No se encontró la URL del archivo multimedia.")

            # Crear la notificación con el mensaje del experto (si se proporciona)
            create_notification(user_email, 'idea', idea_data['titulo'], 'eliminar', idea_data['creador_por'], mensaje_experto)

            messages.success(request, 'Idea eliminada con éxito.')
            return redirect('ideas:list')

        except requests.exceptions.HTTPError as e:
            messages.error(request, f'Error al eliminar la idea: {e}')
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error en la solicitud HTTP: {e}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {e}')

    return render(request, 'ideas/delete.html', {'idea': idea_data, 'is_experto': is_experto})


def detail_idea(request, codigo_idea):
    user_email = request.session.get('user_email')

    # Verificar si el email de usuario está presente en la sesión
    if not user_email:
        return redirect('login:login')
    try:
        # Obtener la idea desde la API usando la clase IdeaUsuario
        idea_response = IdeaUsuario.get_idea_by_codigo(codigo_idea)
        
        # Imprimir la respuesta completa de la API para verificar su estructura

        # Verificar si la respuesta es válida
        if not idea_response:
            return render(request, 'ideas/detail.html', {'error': 'Idea no encontrada.'})

        # Verificar que haya datos en la respuesta
        if 'codigo_idea' not in idea_response:
            return render(request, 'ideas/detail.html', {'error': 'Datos de la idea no disponibles.'})

        # Datos válidos, extraemos la información
        idea_data = idea_response

        # Extraer los ID de tipo y foco de innovación
        id_tipo_innovacion = idea_data.get('id_tipo_innovacion')
        id_foco_innovacion = idea_data.get('id_foco_innovacion')


        # Obtener focos y tipos de innovación desde las APIs
        focos = FocoInnovacionAPI.get_focos()
        tipos = TipoInnovacionAPI.get_tipo_innovacion()


        # Crear diccionarios para obtener nombres por ID
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

        # Obtener los nombres de tipo y foco por los IDs
        tipo_innovacion_nombre = tipos_dict.get(id_tipo_innovacion, 'Desconocido')
        foco_innovacion_nombre = focos_dict.get(id_foco_innovacion, 'Desconocido')



        # Añadir los nombres de tipo y foco a la idea
        idea_data['tipo_innovacion_nombre'] = tipo_innovacion_nombre
        idea_data['foco_innovacion_nombre'] = foco_innovacion_nombre

        # Pasar todos los datos a la plantilla
        return render(request, 'ideas/detail.html', {
            'idea': idea_data,
            'tipo_innovacion': tipo_innovacion_nombre,
            'foco_innovacion': foco_innovacion_nombre,
        })

    except Exception as e:
        print(f"Error inesperado: {e}")
        return render(request, 'ideas/detail.html', {'error': f'Error al cargar los detalles: {e}'})






def update_idea(request, pk):
    user_email = request.session.get('user_email')  # Obtener el correo electrónico del usuario autenticado
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para actualizar una idea.')
        return redirect('login')

    # Llamada a la API para obtener los datos de la idea
    client = APIClient('idea')
    idea = client.get_data(where_condition=f"codigo_idea = {pk}")  # Cambiado 'id' por 'codigo_idea'
    if not idea:
        messages.error(request, 'Idea no encontrada.')
        return redirect('ideas:list')

    idea_data = idea[0]  # Asumimos que idea es una lista de diccionarios

    # Obtener focos y tipos de innovación
    try:
        focos_innovacion = FocoInnovacionAPI.get_focos()  # Usar las APIs adecuadas para obtener los datos
        tipos_innovacion = TipoInnovacionAPI.get_tipo_innovacion()

        # Crear diccionarios para obtener nombres por ID
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos_innovacion}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos_innovacion}

        # Añadir los nombres de tipo y foco a la idea
        idea_data['tipo_innovacion_nombre'] = tipos_dict.get(idea_data['id_tipo_innovacion'], 'Desconocido')
        idea_data['foco_innovacion_nombre'] = focos_dict.get(idea_data['id_foco_innovacion'], 'Desconocido')

    except Exception as e:
        messages.error(request, f'Error al obtener datos de innovación: {e}')
        return redirect('ideas:list')

    # Verificar el rol del usuario (si es Experto o no)
    api_client_perfil = APIClient(table_name="perfil")
    perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

    # Verificar si el perfil contiene información y si el rol es 'Experto'
    if perfil_data:
        rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
        is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
    else:
        is_experto = False  # En caso de que no se encuentre el perfil

    if request.method == 'POST':
        form = IdeasForm(request.POST, request.FILES)

        if form.is_valid():
            # Convertir los valores de id_foco_innovacion y id_tipo_innovacion a enteros
            foco_innovacion_name = int(form.cleaned_data['id_foco_innovacion'])
            tipo_innovacion_name = int(form.cleaned_data['id_tipo_innovacion'])

            try:
                # Buscar los objetos de foco y tipo de innovación usando los valores enteros
                foco_innovacion = next((foco for foco in focos_innovacion if foco['id_foco_innovacion'] == foco_innovacion_name), None)
                tipo_innovacion = next((tipo for tipo in tipos_innovacion if tipo['id_tipo_innovacion'] == tipo_innovacion_name), None)

                if not foco_innovacion or not tipo_innovacion:
                    raise ValueError("Foco o Tipo de Innovación no encontrado en las APIs.")

                json_data = {
                    'titulo': form.cleaned_data['titulo'],
                    'descripcion': form.cleaned_data['descripcion'],
                    'palabras_claves': form.cleaned_data['palabras_claves'],
                    'recursos_requeridos': form.cleaned_data['recursos_requeridos'],
                    'fecha_creacion': form.cleaned_data['fecha_creacion'].isoformat(),
                    'id_foco_innovacion': foco_innovacion['id_foco_innovacion'],  # Usar ID de foco
                    'id_tipo_innovacion': tipo_innovacion['id_tipo_innovacion'],  # Usar ID de tipo
                    'creador_por': idea_data['creador_por']  # Mantener el creador original
                }

                # Adjuntar archivo multimedia si existe
                if 'archivo_multimedia' in request.FILES:
                    file = request.FILES['archivo_multimedia']
                    json_data['archivo_multimedia'] = file.name  # Mantener solo el nombre del archivo si no se debe subir el contenido completo
                else:
                    json_data['archivo_multimedia'] = idea_data['archivo_multimedia']  # Mantener el valor actual si no hay archivo nuevo

                # Llamada a la función auto_update_data
                response = client.auto_update_data(where_condition=f"codigo_idea = {pk}", json_data=json_data)

                if response:
                    # Si es experto, obtener el mensaje adicional del experto
                    mensaje_experto = form.cleaned_data.get('mensaje_experto', None) if is_experto else None

                    # Crear la notificación después de la actualización exitosa
                    create_notification(
                        user_email,
                        'idea',
                        idea_data['titulo'],
                        'actualizar',
                        idea_data['creador_por'],
                        mensaje_experto
                    )

                    # Mensaje por defecto de la acción
                    mensaje_default = "La idea ha sido actualizada correctamente."
                    messages.success(request, mensaje_default)
                    return redirect('ideas:list')
                else:
                    messages.info(request, 'No hubo cambios en los datos.')

                return redirect('ideas:list')
            except ValueError as e:
                messages.error(request, f'Error: {e}')
            except Exception as e:
                messages.error(request, f'Error al actualizar la idea: {e}')

        else:
            messages.error(request, 'Formulario inválido. Por favor, revisa los datos ingresados.')

    else:
        # Inicializa el formulario con los datos de la idea
        form = Ideas_update_Form(initial=idea_data)
        if not is_experto:
            form.fields.pop('mensaje_experto', None)  # Eliminar el campo 'mensaje_experto' si no es experto

    return render(request, 'ideas/update.html', {'form': form})



def create_notification(experto_email, tipo_entidad, entidad_titulo, accion, usuario_email, mensaje_experto=None):
    try:
        # Crear el mensaje por defecto
        if accion == 'eliminar':
            mensaje_default = f"El experto ha eliminado tu {tipo_entidad}: {entidad_titulo}"
        elif accion == 'editar':
            mensaje_default = f"El experto ha editado tu {tipo_entidad}: {entidad_titulo}"
        elif accion == 'confirmar':
            mensaje_default = f"El experto ha confirmado tu {tipo_entidad}: {entidad_titulo}"
        else:
            mensaje_default = "Acción desconocida"

        # Si el experto proporciona un mensaje, usarlo, sino el mensaje por defecto
        mensaje_final = mensaje_experto if mensaje_experto else mensaje_default

        # Crear los datos de la notificación
        notificacion_data = {
            'usuario_email': usuario_email,  # Correo del creador de la entidad
            'tipo_entidad': tipo_entidad,  # Tipo de entidad (idea u oportunidad)
            'entidad_titulo': entidad_titulo,  # Título de la entidad
            'mensaje_default': mensaje_default,
            'mensaje_experto': mensaje_final,  # Mensaje del experto (puede ser el proporcionado o el default)
            'experto_email': experto_email,  # Correo del experto que realizó la acción
            'fecha_creacion': py_datetime.now().isoformat(),  # Convertir la fecha a formato ISO
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



# def confirmar_idea(request, codigo_idea):
#     user_email = request.session.get('user_email')  # Obtener el correo electrónico del usuario autenticado
#     if not user_email:
#         messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para confirmar la idea.')
#         return redirect('login:login')

#     # Verificar si el usuario es experto
#     api_client_perfil = APIClient(table_name="perfil")
#     perfil_data = api_client_perfil.get_data(where_condition=f"usuario_email = '{user_email}'")

#     if perfil_data:
#         rol_usuario = perfil_data[0].get('rol')  # Obtener el rol del usuario
#         is_experto = (rol_usuario == 'Experto')  # Verificar si el rol es 'Experto'
#     else:
#         is_experto = False  # En caso de que no se encuentre el perfil

#     # Llamada a la API para obtener los datos de la idea
#     client = APIClient('idea')
#     idea = client.get_data(where_condition=f"codigo_idea = {codigo_idea}")

#     if not idea:
#         messages.error(request, 'Idea no encontrada.')
#         return redirect('ideas:list')

#     idea_data = idea[0]  # Asumimos que es una lista de diccionarios

#     # Verificación de creador_por (en lugar de usuario_email)
#     usuario_email = idea_data.get('creador_por')
#     if not usuario_email:
#         print(f"Error: 'creador_por' no encontrado en los datos de la idea: {idea_data}")
#         messages.error(request, 'No se encontró el correo del usuario asociado a esta idea.')
#         return redirect('ideas:list')

#     # Procesamiento del formulario
#     if request.method == 'POST':
#         # Verificar si el usuario está en el segundo paso (confirmar)
#         if 'confirmar' in request.POST:
#             try:
#                 # Obtener el mensaje del experto, si no está presente asignar un valor por defecto
#                 mensaje_experto = request.POST.get('mensaje_experto', "¡Idea confirmada exitosamente!")

#                 # Cambiar el estado de la idea a True (confirmada)
#                 json_data = {
#                     'estado': True
#                 }

#                 # Actualizar datos en la API
#                 response = client.auto_update_data(where_condition=f"codigo_idea = {codigo_idea}", json_data=json_data)

#                 if response:
#                     # Crear la notificación después de confirmar la idea
#                     experto_email = user_email  # Asumimos que el experto es el usuario actual
#                     tipo_entidad = "idea"
#                     entidad_titulo = idea_data.get('titulo')  # Título de la idea
#                     accion = 'confirmar'

#                     # Llamada a la función para crear la notificación
#                     create_notification(
#                         experto_email=experto_email,
#                         tipo_entidad=tipo_entidad,
#                         entidad_titulo=entidad_titulo,
#                         accion=accion,
#                         usuario_email=usuario_email,
#                         mensaje_experto=mensaje_experto  # Pasar el mensaje_experto aquí
#                     )

#                     messages.success(request, 'La idea ha sido confirmada exitosamente.')
#                     return redirect('ideas:list')
#                 else:
#                     messages.error(request, 'Hubo un error al confirmar la idea.')

#             except Exception as e:
#                 messages.error(request, f'Error al confirmar la idea: {e}')
#         else:
#             # Si no es el segundo paso, mostrar el formulario de confirmación
#             return render(request, 'ideas/confirmar_ideas.html', {'idea': idea_data, 'is_experto': is_experto})

#     # Si no es POST, mostrar la vista de confirmación
#     return render(request, 'ideas/confirmar_ideas.html', {'idea': idea_data, 'is_experto': is_experto})



def confirmar_idea(request, codigo_idea):
    print("Inicio de la función confirmar_idea")
    
    user_email = request.session.get('user_email')  # Obtener el correo electrónico del usuario autenticado
    print(f"Correo electrónico del usuario: {user_email}")
    if not user_email:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión para confirmar la idea.')
        print("Usuario no autenticado, redirigiendo a login")
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
        print("No se encontraron datos de perfil, el usuario no es experto.")

    # Llamada a la API para obtener los datos de la idea
    try:
        print(f"Consultando idea con código: {codigo_idea}...")
        client = APIClient('idea')
        idea = client.get_data(where_condition=f"codigo_idea = {codigo_idea}")
        print(f"Idea obtenida: {idea}")
    except Exception as e:
        print(f"Error al consultar la idea: {e}")
        idea = []

    if not idea:
        messages.error(request, 'Idea no encontrada.')
        print("No se encontró la idea, redirigiendo a lista de ideas")
        return redirect('ideas:list')

    idea_data = idea[0]  # Asumimos que es una lista de diccionarios
    print(f"Datos de la idea: {idea_data}")

    # Verificación de creador_por (en lugar de usuario_email)
    usuario_email = idea_data.get('creador_por')
    print(f"Correo del creador de la idea: {usuario_email}")
    if not usuario_email:
        messages.error(request, 'No se encontró el correo del usuario asociado a esta idea.')
        print("Correo del creador no encontrado, redirigiendo a lista de ideas")
        return redirect('ideas:list')

    # Procesamiento del formulario
    if request.method == 'POST' and 'confirmar' in request.POST:
        print("Formulario POST recibido, procesando confirmación de la idea...")
        try:
            # Cambiar el estado de la idea a True
            json_data = {'estado': True}
            print(f"Actualizando estado de la idea a: {json_data}")
            response = client.auto_update_data(where_condition=f"codigo_idea = {codigo_idea}", json_data=json_data)
            print(f"Respuesta de actualización: {response}")

            if response:
                # Transferir idea a proyecto si se confirma
                print("Confirmación exitosa, transfiriendo idea a proyecto...")
                proyecto_client = APIClient('proyecto')
                fecha_aprobacion = django_timezone.now().isoformat()

                proyecto_data = {
                    "tipo_origen": "idea",
                    "id_origen": codigo_idea,
                    "titulo": idea_data.get('titulo'),
                    "descripcion": idea_data.get('descripcion'),
                    "fecha_creacion": idea_data.get('fecha_creacion'),
                    "palabras_claves": idea_data.get('palabras_claves'),
                    "recursos_requeridos": idea_data.get('recursos_requeridos'),
                    "archivo_multimedia": idea_data.get('archivo_multimedia'),
                    "creador_por": idea_data.get('creador_por'),
                    "id_tipo_innovacion": idea_data.get('id_tipo_innovacion'),
                    "id_foco_innovacion": idea_data.get('id_foco_innovacion'),
                    "estado": True,
                    "fecha_aprobacion": fecha_aprobacion,
                    "aprobado_por": user_email,
                }
                print(f"Datos del proyecto a insertar: {proyecto_data}")

                proyecto_response = proyecto_client.insert_data(json_data=proyecto_data)
                print(f"Respuesta de inserción de proyecto: {proyecto_response}")

                if proyecto_response:
                    messages.success(request, 'La idea ha sido confirmada y transferida a proyecto exitosamente.')
                    return redirect('ideas:list')
                else:
                    messages.error(request, 'La idea fue confirmada, pero hubo un error al crear el proyecto.')
                    print("Error al crear el proyecto.")

            else:
                messages.error(request, 'Hubo un error al confirmar la idea.')
                print("Error al confirmar la idea.")

        except Exception as e:
            print(f"Excepción durante la confirmación de la idea: {e}")
            messages.error(request, f'Error al confirmar la idea: {e}')

    print("Renderizando plantilla para confirmar ideas.")
    return render(request, 'ideas/confirmar_ideas.html', {'idea': idea_data, 'is_experto': is_experto})
