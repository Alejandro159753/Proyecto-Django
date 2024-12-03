from django.shortcuts import render, redirect
from ..forms.forms import PerfilForm
from ..models import APIClient
from django.contrib import messages
from ..models import APIClient, TipoInnovacionAPI, FocoInnovacionAPI
from django.shortcuts import redirect, render


def mostrar_perfil(request):
    # Obtener el email del usuario autenticado desde la sesión
    user_email = request.session.get('user_email')

    # Verificar si el email de usuario está presente en la sesión
    if not user_email:
        # Agregar un mensaje de advertencia y redirigir al inicio de sesión
        messages.warning(request, "Debes iniciar sesión para ver tu perfil.")
        return redirect('login:login')

    # Crear un objeto APIClient para obtener los datos del perfil
    api_client = APIClient(table_name="perfil")
    
    try:
        # Obtener datos del perfil de la API
        perfil_data = api_client.get_data(where_condition=f"usuario_email = '{user_email}'")
    except Exception as e:
        # Si hay un error, mostrar página de error
        return render(request, 'perfil/error_perfil.html')
    
    if perfil_data:
        perfil = perfil_data[0]

        # Obtener el nombre del rol utilizando el valor en la columna 'rol'
        rol_nombre = perfil.get('rol')
        if rol_nombre:
            # Consultar el nombre del rol
            api_client_rol = APIClient(table_name="rol")
            try:
                rol_data = api_client_rol.get_data(where_condition=f"nombre = '{rol_nombre}'")
                perfil['rol_nombre'] = rol_data[0].get('nombre', 'Rol no disponible') if rol_data else 'Rol no encontrado'
            except Exception:
                perfil['rol_nombre'] = 'Rol no encontrado'
        else:
            perfil['rol_nombre'] = 'Rol no asignado'

        # Obtener áreas de expertise
        api_client_areas = APIClient(table_name="areas_expertise")
        try:
            areas_expertise_data = api_client_areas.get_data(where_condition=f"usuario_email = '{user_email}'")
        except Exception:
            areas_expertise_data = []

        # Obtener información adicional
        api_client_info = APIClient(table_name="informacion_adicional")
        try:
            informacion_adicional_data = api_client_info.get_data(where_condition=f"usuario_email = '{user_email}'")
        except Exception:
            informacion_adicional_data = []

        # Obtener tipos de innovación y focos de innovación
        focos = FocoInnovacionAPI.get_focos()
        tipos = TipoInnovacionAPI.get_tipo_innovacion()

        # Crear diccionarios para los focos y tipos de innovación
        focos_dict = {foco['id_foco_innovacion']: foco['name'] for foco in focos}
        tipos_dict = {tipo['id_tipo_innovacion']: tipo['name'] for tipo in tipos}

        # Obtener las ideas del usuario
        client_ideas = APIClient('idea')
        try:
            ideas = client_ideas.get_data()
            # Agregar tipo y foco a cada idea
            for idea in ideas:
                idea['tipo_innovacion_nombre'] = tipos_dict.get(idea.get('id_tipo_innovacion'), 'Desconocido')
                idea['foco_innovacion_nombre'] = focos_dict.get(idea.get('id_foco_innovacion'), 'Desconocido')
        except Exception as e:
            messages.error(request, f'Error al obtener las ideas: {e}')
            ideas = []

        # Filtrar ideas creadas por el usuario
        user_ideas = [idea for idea in ideas if idea.get('creador_por') == user_email]

        # Obtener las oportunidades del usuario
        client_opportunities = APIClient('oportunidad')
        try:
            oportunidades = client_opportunities.get_data(where_condition=f"creador_por = '{user_email}'")
            # Agregar tipo y foco a cada oportunidad
            for oportunidad in oportunidades:
                oportunidad['tipo_innovacion_nombre'] = tipos_dict.get(oportunidad.get('id_tipo_innovacion'), 'Desconocido')
                oportunidad['foco_innovacion_nombre'] = focos_dict.get(oportunidad.get('id_foco_innovacion'), 'Desconocido')

            user_oportunidades = [oportunidad for oportunidad in oportunidades if oportunidad.get('creador_por') == user_email]
        except Exception as e:
            messages.error(request, f'Error al obtener las oportunidades: {e}')
            user_oportunidades = []

        # Verificar si el usuario es un "Experto" y permitirle cambiar el rol
        if perfil['rol'] == 'Experto':
            # Obtener los roles disponibles
            api_client_rol = APIClient(table_name="rol")
            try:
                roles_data = api_client_rol.get_data()
            except Exception:
                roles_data = []

            # Obtener todos los usuarios para la opción de cambiar roles
            try:
                usuarios_data = api_client.get_data()  # Obtener todos los perfiles
            except Exception:
                usuarios_data = []

            # Si el formulario fue enviado, procesamos la actualización
            if request.method == 'POST':
                nuevo_rol = request.POST.get('nuevo_rol')
                usuario_email = request.POST.get('usuario_email')

                if nuevo_rol and usuario_email:
                    # Actualizar el perfil del usuario con el nuevo rol
                    perfil_update_data = {'rol': nuevo_rol}
                    try:
                        perfil_client = APIClient('perfil')
                        perfil_client.update_data(where_condition=f"usuario_email = '{usuario_email}'", json_data=perfil_update_data)
                        messages.success(request, f"El rol del usuario {usuario_email} ha sido actualizado a {nuevo_rol}.")
                    except Exception as e:
                        messages.error(request, f"Error al actualizar el rol del usuario: {e}")

            # Contexto para renderizar en el template para el experto
            context = {
                'perfil': perfil,
                'areas_expertise': areas_expertise_data or [],
                'informacion_adicional': informacion_adicional_data or [],
                'ideas': user_ideas,
                'oportunidades': user_oportunidades,
                'roles': roles_data,
                'usuarios': usuarios_data,  # Pasa los usuarios
                'user_email': user_email
            }
        else:
            # Contexto para renderizar en el template para otros usuarios
            context = {
                'perfil': perfil,
                'areas_expertise': areas_expertise_data or [],
                'informacion_adicional': informacion_adicional_data or [],
                'ideas': user_ideas,
                'oportunidades': user_oportunidades,
                'user_email': user_email
            }

        # Renderizar la página con el contexto
        return render(request, 'perfil/mi_perfil.html', context)
    
    # Si no se encuentra el perfil, mostrar la página de error
    return render(request, 'perfil/error_perfil.html')




def obtener_datos_perfil(api_client, user_email):
    try:
        return api_client.get_data(where_condition=f"usuario_email = '{user_email}'")
    except Exception as e:
        return None

def obtener_datos_adicionales(user_email, table_name):
    # Crea una instancia del cliente API para la tabla correspondiente
    api_client = APIClient(table_name=table_name)
    
    try:
        # Realiza la consulta para obtener los datos según el correo del usuario
        data = api_client.get_data(where_condition=f"usuario_email = '{user_email}'")
        
        # Verifica si se obtuvieron datos, si no, retorna una lista vacía
        if data:
            return data
        else:
            return []  # Si no hay datos, se retorna una lista vacía
    
    except Exception as e:
        # Maneja cualquier error que ocurra al obtener los datos
        return []  # Retorna una lista vacía en caso de error





def editar_perfil(request):
    # Obtener el email del usuario desde la sesión
    user_email = request.session.get('user_email')
    
    # Si no se encuentra el email en la sesión, redirigir al inicio de sesión
    if not user_email:
        return redirect('login:login')

    # Crear una instancia del cliente API para acceder a la tabla "perfil"
    api_client = APIClient(table_name="perfil")
    
    # Obtener los datos del perfil del usuario
    perfil_data = obtener_datos_perfil(api_client, user_email)
    
    if perfil_data:
        perfil = perfil_data[0]  # Se supone que siempre obtienes solo un perfil

        # Obtener los datos adicionales relacionados con el perfil (áreas de expertise e información adicional)
        areas_expertise_data = obtener_datos_adicionales(user_email, "areas_expertise")
        informacion_adicional_data = obtener_datos_adicionales(user_email, "informacion_adicional")
        
        # Inicializar el formulario con los valores obtenidos del perfil y los datos adicionales
        form = PerfilForm(initial={
            'nombre': perfil.get('nombre', ''),
            'direccion': perfil.get('direccion', ''),
            'descripcion': perfil.get('descripcion', ''),
            'fecha_nacimiento': perfil.get('fecha_nacimiento', ''),
            'area_expertise': areas_expertise_data[0].get('area', '') if areas_expertise_data else '',
            'info_adicional': informacion_adicional_data[0].get('info', '') if informacion_adicional_data else '',
        })

        # Procesar el formulario cuando se envía una solicitud POST
        if request.method == 'POST':
            form = PerfilForm(request.POST)
            
            if form.is_valid():
                # Preparar los datos actualizados para la base de datos
                updated_data = {
                    'nombre': form.cleaned_data['nombre'],
                    'direccion': form.cleaned_data['direccion'],
                    'descripcion': form.cleaned_data['descripcion'],
                    'fecha_nacimiento': form.cleaned_data['fecha_nacimiento'].strftime('%Y-%m-%d') if form.cleaned_data['fecha_nacimiento'] else '',
                }

                try:
                    # Intentar actualizar los datos en la tabla "perfil"
                    update_response_perfil = api_client.update_data(
                        where_condition=f"usuario_email = '{user_email}'", 
                        json_data=updated_data
                    )
                    
                    if update_response_perfil:
                        # Actualizar o crear las áreas de expertise
                        if form.cleaned_data['area_expertise']:
                            api_client_areas = APIClient(table_name="areas_expertise")
                            if areas_expertise_data:  # Si ya existe, actualizamos
                                update_response_area = api_client_areas.update_data(
                                    where_condition=f"usuario_email = '{user_email}'",
                                    json_data={'area': form.cleaned_data['area_expertise']}
                                )
                            else:  # Si no existe, creamos un nuevo registro
                                insert_response_area = api_client_areas.insert_data(json_data={
                                    'usuario_email': user_email,
                                    'area': form.cleaned_data['area_expertise']
                                })
                        
                        # Actualizar o crear la información adicional
                        if form.cleaned_data['info_adicional']:
                            api_client_info = APIClient(table_name="informacion_adicional")
                            if informacion_adicional_data:  # Si ya existe, actualizamos
                                update_response_info = api_client_info.update_data(
                                    where_condition=f"usuario_email = '{user_email}'",
                                    json_data={'info': form.cleaned_data['info_adicional']}
                                )
                            else:  # Si no existe, creamos un nuevo registro
                                insert_response_info = api_client_info.insert_data(json_data={
                                    'usuario_email': user_email,
                                    'info': form.cleaned_data['info_adicional']
                                })
                        
                        # Si todo fue exitoso, mostrar mensaje de éxito
                        messages.success(request, "Perfil actualizado con éxito.")
                        return redirect('perfil:mi_perfil')  # Redirigir al perfil después de actualizar
                    else:
                        # Si la respuesta no es exitosa, mostrar un error
                        form.add_error(None, "Error al actualizar el perfil. Inténtalo de nuevo.")
                except Exception as e:
                    # Si ocurre una excepción, mostrar el error
                    form.add_error(None, f"Error al actualizar el perfil: {e}")

        # Pasar el formulario y el perfil a la plantilla para renderizar
        context = {'form': form, 'perfil': perfil}
        return render(request, 'perfil/editar_perfil.html', context)

    # Si no se encuentra el perfil, mostrar una página de error
    return render(request, 'perfil/error_perfil.html')



