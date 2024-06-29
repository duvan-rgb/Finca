from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader, RequestContext
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.urls import reverse
from random import randrange
from .models import User, Trabajador, Animal, Suministro, Produccion
from django.db.models import Q
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from functools import wraps
from datetime import datetime
import json
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

from django.core.serializers.json import DjangoJSONEncoder
import json

def home(request):
    return render(request, 'granja/home.html')

# Vista para el login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Verifica el rol del user
            trabajador = Trabajador.objects.get(cc=username)
            if trabajador.rol == 'administrador':
                return redirect('administrador')
            elif trabajador.rol == 'trabajador':
                return redirect('worker')
            elif trabajador.rol == 'veterinario':
                return redirect('vet')
        else:
            print('error')
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        # Verifica si hay una sesión iniciada y redirige a la pagina segun el rol
        if request.user.is_authenticated:
            trabajador = Trabajador.objects.get(cc=request.user.username)
            if trabajador.rol == 'administrador':
                return redirect('administrador')
            elif trabajador.rol == 'trabajador':
                return redirect('worker')
            elif trabajador.rol == 'veterinario':
                return redirect('vet')
    return render(request, 'granja/log_in.html')

# Decorador para restringir el acceso a paginas de otros roles
def rol_required(rol):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                trabajador = Trabajador.objects.get(cc=request.user.username)
                if trabajador.rol == rol:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'Acceso denegado.')
                    return redirect('home')
            else:
                # Si no esta autenticado lo manda a la pagina del login
                return redirect('login_view')
        return wrapped_view
    return decorator

# Vista del logout
def log_out(request):
    logout(request)
    return redirect('login')

# ADMINISTRADOR
@login_required
@rol_required('administrador')
def administrador(request):
    return render(request, 'granja/administrador.html')

# Tabla administrador/animales
@login_required
@rol_required('administrador')
def animals(request):
    db_data = Animal.objects.all()
    context = {
        'db_data': db_data[::-1],
        'update': None,
        'Animal': Animal,
    }
    return render(request, 'granja/animales.html', context)

# Insertar un animal
@login_required
@rol_required('administrador')
def insert_animal(request):
    if request.method == 'GET' and 'num_id' in request.GET:
        num_id = request.GET.get('num_id')
        existe = Animal.objects.filter(num_id=num_id).exists()
        return JsonResponse({'existe': existe})
    elif request.method == 'POST':
        try:
            num_id = request.POST['num_identificacion']
            birth_str = request.POST['birthdate']
            birth = datetime.strptime(birth_str, '%Y-%m-%d').date()
            breed = request.POST['breeds']
            color = request.POST['colors']
            sex = request.POST['sexos']
            type = request.POST['tipos']
            if type == 'otro':
                type = request.POST['otro_tipo']
            health = request.POST['health_status']
            if health == 'otro':
                health = request.POST['otro_estatus']
            aditional = request.POST['aditional_info']
            
            if 'imagen_cow' in request.FILES:
                imagen_cow = request.FILES['imagen_cow']
            else:
                imagen_cow = None
            
            db_data = Animal(
                num_id=num_id, 
                birth=birth, 
                breed=breed, 
                color=color, 
                sex=sex, 
                type=type,
                health=health, 
                img_cow=imagen_cow, 
                aditional=aditional, 
                encargado_insert=request.user,
                encargado_update=request.user
            )
            db_data.save()
            messages.success(request, 'Registro guardado exitosamente.')
            return  HttpResponseRedirect(reverse('animals'))
        except ValueError as error:
            print(error)
            return HttpResponseRedirect(reverse('animals'))

def update_edad(request):
    animals = Animal.objects.all()
    for animal in animals:
        actualizar_edad = animal.calcular_edad()
        print(actualizar_edad)
        animal.edad = actualizar_edad
        animal.save()
    return JsonResponse({'mensaje': 'Edades actualizadas correctamente'})
"""def update_edad(request):
    num_id = request.POST.get('num_id')

    try:
        animal = Animal.objects.get(num_id=num_id)
        actualizar_edad = animal.calcular_edad()
        print(actualizar_edad)
        animal.edad = actualizar_edad
        animal.save()
        return JsonResponse({'edad': actualizar_edad})
    except Animal.DoesNotExist:
        print(f'Animal con num_id={num_id} no encontrado.')
        return JsonResponse({'error': 'Animal no encontrado'}, status=404)
    except Exception as e:
        print('Error en la vista update_edad:', str(e))
        return JsonResponse({'error': 'Error interno'}, status=500)"""

# Actualizar un animal
@login_required
@rol_required('administrador')
def update_animal(request):
    if request.method == 'POST':
        animal_id = request.POST['id']
        num_id = request.POST['num_identificacion']
        birth_str = request.POST['birthdate']
        birth = datetime.strptime(birth_str, '%Y-%m-%d').date()
        breed = request.POST['breeds']
        color = request.POST['colors']
        sex = request.POST['sexos']
        type = request.POST['tipos']
        if type == 'otro':
            type = request.POST['otro_tipo']
        health = request.POST['health_status']
        if health == 'otro':
            health = request.POST['otro_estatus']
        aditional = request.POST['aditional_info']
        
        animal = get_object_or_404(Animal, pk=animal_id)

        # Actualización de campos
        animal.num_id = num_id
        animal.birth = birth
        animal.breed = breed
        animal.color = color
        animal.sex = sex
        animal.type = type
        animal.health = health
        animal.aditional = aditional
        
        # Manejo de la imagen
        if 'imagen_cow' in request.FILES:
            animal.img_cow = request.FILES['imagen_cow']

        animal.save()
        messages.success(request, 'Registro actualizado exitosamente.')
        return HttpResponseRedirect(reverse('animals'))

# Habilitar el formulario de edición
@login_required
@rol_required('administrador')
def update_form_animal(request, animal_id):
    db_data = Animal.objects.all()
    db_data_only = Animal.objects.get(pk=animal_id)
    context = {
        "db_data": db_data,
        "update": db_data_only,
        'Animal': Animal,
    }
   
    return render(request, 'granja/animales.html', context)

# Borrar animal
@login_required
@rol_required('administrador')
def delete_animal(request, animal_id):
    db_data = Animal.objects.filter(id=animal_id)
    db_data.delete()
    messages.success(request, 'El registro ha sido eliminado.')
    return HttpResponseRedirect(reverse('animals'))

# Listar animales con la barra de busqueda
@login_required
@rol_required('administrador')
def lista_animales(request):
    search_term = request.GET.get('search', None)
    db_data = Animal.objects.all()
   
    if search_term:
        db_data = db_data.filter(
            Q(num_id__icontains=search_term) |
            Q(breed__icontains=search_term) |
            Q(birth__icontains=search_term) |
            Q(type__icontains=search_term)
        )
    
    context = {
        'db_data': db_data[::-1],
        'update': None,
        'Animal': Animal,
        'search_term': search_term
    }
       
    return render(request, 'granja/animales.html', context)

# Tabla administrador/trabajadores
@login_required
@rol_required('administrador')
def workers(request):
    db_data = Trabajador.objects.all()
    context = {
        'db_data': db_data[::-1],
        'update': None,
        'Trabajador': Trabajador,
    }
    return render(request, 'granja/trabajadores.html', context)

# Insertar trabajador
@login_required
@rol_required('administrador')
def insert_worker(request):
    if request.method == 'GET' and 'cc' in request.GET:
        cc = request.GET.get('cc')
        existe = Trabajador.objects.filter(cc=cc).exists()
        return JsonResponse({'existe': existe})
    elif request.method == 'POST':
        try:
            name = request.POST['nombre_trabajador']
            cc = request.POST['num_identificacion']
            rol = request.POST['rol']
            direction = request.POST['direccion_residencia']
            tel = request.POST['telefono_contacto']
            email = request.POST['correo_electronico']

            if name == '' or cc == '' or rol == '':
                raise ValueError('Error')
            
            db_data = Trabajador(name = name, cc = cc, rol = rol, direction = direction, tel = tel, email = email)
            db_data.save()
            messages.success(request, 'Registro insertado con exito.')
            correo_bienvenida(name, cc, cc, email)

            return HttpResponseRedirect(reverse('workers'))
        except ValueError as error:
            print(error)
            return HttpResponseRedirect(reverse('workers'))

def correo_bienvenida(nombre, username, password, email_trabajador):
    subject = 'Credenciales Trabajador de la Granja "El Manantial"'
    html_content = render_to_string('granja/welcome_email.html',
                                    {'nombre': nombre, 'username': username, 'password': password})
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email_trabajador])
    email.attach_alternative(html_content, "text/html")
    email.send()

# Actualizar trabajador
@login_required
@rol_required('administrador')
def update_worker(request):
    worker_id = request.POST['id']
    name = request.POST['nombre_trabajador']
    cc = request.POST['num_identificacion']
    rol = request.POST['rol']
    direction = request.POST['direccion_residencia']
    tel = request.POST['telefono_contacto']
    email = request.POST['correo_electronico']
    db_data = Trabajador.objects.get(pk=worker_id)
    db_data.name = name
    db_data.cc = cc
    db_data.rol = rol
    db_data.direction = direction
    db_data.tel = tel
    db_data.email = email
    db_data.save()
    messages.success(request, 'Registro actualizado con exito.')
    return HttpResponseRedirect(reverse('workers')) 

# Formulario para actualizar trabajador
@login_required
@rol_required('administrador')
def update_form_worker(request, worker_id):
    db_data = Trabajador.objects.all()
    db_data_only = Trabajador.objects.get(pk=worker_id)
    context = {
        "db_data": db_data,
        "update": db_data_only
    }
    
    return render(request, 'granja/trabajadores.html', context)

# Eliminar trabajador
@login_required
@rol_required('administrador')
def delete_worker(request, worker_id):
    trabajador = Trabajador.objects.get(id=worker_id)
    User.objects.filter(username=trabajador.cc).delete()
    Trabajador.objects.filter(id=worker_id).delete()
    messages.success(request, 'El trabajador ha sido eliminado.')
    return HttpResponseRedirect(reverse('workers'))

# Lista de trabajadores
@login_required
@rol_required('administrador')
def lista_trabajadores(request):
    search_term = request.GET.get('search', None)
    db_data = Trabajador.objects.all()
    
    if search_term:
        db_data = db_data.filter(
            Q(name__icontains=search_term) |
            Q(cc__icontains=search_term) |
            Q(rol__icontains=search_term)
        )
    
    context = {
        'db_data': db_data,
        'update': None,
        'Trabajador': Trabajador,
        'search_term': search_term
    }
    return render(request, 'granja/trabajadores.html', context)

# Tabla administrador/suministros
@login_required
@rol_required('administrador')
def supplies(request):
    db_data = Suministro.objects.all()
    suministros = Suministro.objects.values_list('name', flat=True).distinct() #Esto es para guardar los nombres de los suministros y llamarlos en los graficos
    animales = Animal.objects.values_list('num_id', flat=True).distinct()
    context = {
        'db_data': db_data[::-1],
        'update': None,
        'Suministro': Suministro,
        'suministros': suministros,
        'animales': animales
    }
    return render(request, 'granja/suministros.html', context)

@login_required
@rol_required('administrador')
def insert_supplie(request):
    if request.method == 'GET' and 'lote' in request.GET:
        lote = request.GET.get('lote')
        existe = Suministro.objects.filter(lote=lote).exists()
        return JsonResponse({'existe': existe})
    elif request.method == 'POST':
        try:
            tipo = request.POST['tipos']
            if tipo == 'otro':
                tipo = request.POST['otro_tipo']
            nombre = request.POST['name'] 
            cantidad = request.POST['quantity']
            cantidad = float(cantidad)
            medida = request.POST['unit']
            lote = request.POST['lot_number']
            caducidad = request.POST['expiration_date']
            condicion = request.POST['storage_conditions']
            if condicion == 'otro':
                condicion = request.POST['otra_condicion']
            unidad = request.POST['cost_per_unit']
            unidad = float(unidad)
            total = cantidad * unidad
            descripcion = request.POST['detail']

            db_data = Suministro(tipo = tipo, name = nombre, descripcion = descripcion, cantidad = cantidad,
                                medida = medida, lote = lote, caducidad = caducidad, condicion = condicion, unidad = unidad,
                                total = total, encargado_insert = request.user, encargado_update = request.user, total_actual = total)
            db_data.save()
            messages.success(request, 'Registro insertado con exito.')
            return HttpResponseRedirect(reverse('supplies'))
        except ValueError as error:
            print(error)
            return HttpResponseRedirect(reverse('supplies'))

def update_cantidad(request):
    if request.method == 'POST':
        data = json.loads(request.body) # Con esto se llaman los datos del fetch
        suministro_lote = data.get('suministro_lote')
        cantidad_nueva = data.get('cantidad_nueva')
        
        try:
            suministro = Suministro.objects.get(lote=suministro_lote)
            suministro.cantidad = int(cantidad_nueva)
            suministro.save()
            return JsonResponse({'message': 'Cantidad actualizada correctamente.'})
        except Suministro.DoesNotExist:
            return JsonResponse({'error': 'Suministro no encontrado.'}, status=404)
    return JsonResponse({'error': 'Método no permitido.'}, status=405)
"""def update_cantidad(request):
    
    suministro_lote = request.POST.get('suministro_lote')
    cantidad_nueva = request.POST.get('cantidad_nueva')
    print(suministro_lote, cantidad_nueva)
    suministro = Suministro.objects.get(lote=suministro_lote)
    suministro.cantidad = int(cantidad_nueva)
    print(suministro)
    suministro.save()

    return JsonResponse({'message': 'Cantidad actualizada correctamente.'})"""
    
# Actualizar un suministro
@login_required
@rol_required('administrador')
def update_supplie(request):
    if request.method == 'POST':
        suministro_id = request.POST['id']
        tipo = request.POST['tipos']
        if tipo == 'otro':
            tipo = request.POST['otro_tipo']
        nombre = request.POST['name']
        cantidad = request.POST['quantity']
        medida = request.POST['unit']
        caducidad = request.POST['expiration_date']
        condicion = request.POST['storage_conditions']
        if condicion == 'otro':
            condicion = request.POST['otra_condicion']
        descripcion = request.POST['detail']

        if tipo not in Suministro.TIPOS:
            """Suministro.TIPOS.__add__(tuple[tipo])"""
            pass #Quiero que se agregue un nuevo tipo en caso de que no este en la lista
        
        suministro = get_object_or_404(Suministro, pk=suministro_id)

        """if cantidad == 0:
            suministro.estado = 'agotado'
            suministro = Suministro.objects.filter(id=suministro_id)
            suministro.delete()
            messages.info(request, 'El suministro en 0 se elimina')"""
        # Actualización de campos
        unidad = suministro.unidad
        suministro.tipo = tipo
        suministro.name = nombre
        suministro.cantidad = cantidad
        suministro.medida = medida
        suministro.caducidad = caducidad
        suministro.condicion = condicion
        suministro.total_actual = float(unidad) * float(cantidad)
        suministro.descripcion = descripcion
        suministro.encargado_update = request.user

        suministro.save()
        messages.success(request, 'Registro actualizado exitosamente.')
        return HttpResponseRedirect(reverse('supplies'))

# Habilitar el formulario de edición
@login_required
@rol_required('administrador')
def update_form_supplie(request, suministro_id):
    db_data = Suministro.objects.all()
    db_data_only = Suministro.objects.get(pk=suministro_id)
    context = {
        "db_data": db_data,
        "update": db_data_only,
        'Suministro': Suministro,
    }
   
    return render(request, 'granja/suministros.html', context)

# Borrar suministro
@login_required
@rol_required('administrador')
def delete_supplie(request, suministro_id):
    db_data = Suministro.objects.filter(id=suministro_id)
    db_data.delete()
    messages.success(request, 'El registro ha sido eliminado.')
    return HttpResponseRedirect(reverse('supplies'))

# Listar suministros con la barra de busqueda
@login_required
@rol_required('administrador')
def lista_suministros(request):
    search_term = request.GET.get('search', None)
    db_data = Suministro.objects.all()
   
    if search_term:
        db_data = db_data.filter(
            Q(lote__icontains=search_term) |
            Q(name__icontains=search_term) |
            Q(tipo__icontains=search_term)
        )
    suministros = Suministro.objects.values_list('name', flat=True).distinct()
    context = {
        'db_data': db_data[::-1],
        'update': None,
        'Suministro': Suministro,
        'search_term': search_term,
        'suministros': suministros
    }
    return render(request, 'granja/suministros.html', context)

# Grafico para hacer seguimiento de precios
def grafico_precio(request):
    suministro_id = request.GET.get('selectPrecios')
    rango = request.GET.get('rango_fecha')
    fecha_inicio = None
    fecha_fin = None

    if rango:
        fecha_inicio, fecha_fin = rango.split(' - ')

    colors = ['blue', 'orange', 'red', 'black', 'yellow', 'green', 'lightblue', 'purple', 'brown']

    datos = Suministro.objects.filter(
        Q(name=suministro_id) &
        Q(fecha_insert__range=[fecha_inicio, fecha_fin])
    ).order_by('fecha_insert')

    nombre = suministro_id
    fechas = [d.fecha_insert.strftime('%Y-%m-%d') for d in datos]
    precios = [d.unidad for d in datos]
    random_color = colors[randrange(0, len(colors))]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'fechas_json': json.dumps(fechas, cls=DjangoJSONEncoder),
            'precios_json': json.dumps(precios, cls=DjangoJSONEncoder),
            'nombre_json': json.dumps(nombre, cls=DjangoJSONEncoder),
            'color_json': json.dumps(random_color, cls=DjangoJSONEncoder)
        })

    context = {
        'fechas_json': json.dumps(fechas, cls=DjangoJSONEncoder),
        'precios_json': json.dumps(precios, cls=DjangoJSONEncoder),
        'nombre_json': json.dumps(nombre, cls=DjangoJSONEncoder),
        'color_json': json.dumps(random_color, cls=DjangoJSONEncoder)
    }
    return render(request, 'granja/suministros.html', context)

# Grafico para verificar existencias
def grafico_existencias(request):
    suministro_id = request.GET.get('selectExistencias', None)

    colors = ['blue', 'orange', 'red', 'black', 'yellow', 'green', 'lightblue', 'purple', 'brown']
    
    if not suministro_id:
        return JsonResponse({'error': 'El nombre del suministro es requerido.'}, status=400)
    
    datos = Suministro.objects.filter(
        Q(name=suministro_id)
    ).order_by('lote')

    nombre = suministro_id
    lotes = [d.lote for d in datos]
    existencias = [d.cantidad for d in datos]
    random_color = colors[randrange(0, len(colors))]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'lotes': lotes,
            'existencias': existencias,
            'nombre': nombre,
            'color': random_color
        })

    context = {
        'lotes_json': json.dumps(lotes, cls=DjangoJSONEncoder),
        'existencias_json': json.dumps(existencias, cls=DjangoJSONEncoder),
        'nombre_json': json.dumps(nombre, cls=DjangoJSONEncoder),
        'color_json': json.dumps(random_color, cls=DjangoJSONEncoder)
    }
    return render(request, 'granja/suministros.html', context)

# Tabla administrador/produccion
@login_required
@rol_required('administrador')
def production(request):
    db_data = Produccion.objects.all()
    animal_data = Animal.objects.all()

    for ids in db_data:
        if ids.id_vendidas:
            ids.id_vendidas_list = ids.id_vendidas.split(',')

    # Prepara datos JSON para poder ser manejados por JS
    if request.headers.get('accept') == 'application/json':
        animal_data_json = []
        for animal in animal_data:
            animal_dict = {
                'num_id': animal.num_id,
                'animalString': str(animal),
                'edad_categoria': animal.edad_categoria,
                'estado': animal.estado,
            }
            animal_data_json.append(animal_dict)

        data = {
            'animal_data': animal_data_json
        }

        return JsonResponse(data)

    context = {
        'Produccion': Produccion,
        'db_data': db_data,
        'update': None,
        'animal_data': animal_data,
    }

    if animal_data == '':
        messages.error(request, 'No hay animales registrados')
        return render(request, 'granja/produccion.html', context)

    return render(request, 'granja/produccion.html', context)

# Insertar produccion
@login_required
@rol_required('administrador')
def insert_production(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipoProduccion')
        if tipo == 'leche':
            cantidad = request.POST.get('cantidadLeche')
            vaca = request.POST.get('idVaca')
            adicional = request.POST.get('observacionesLeche')
            produccion = Produccion(tipo=tipo, cantidad_leche=cantidad, vaca=vaca, adicional=adicional,
                                    tipo_ganado='', cantidad_vendidas=0, id_vendidas='', precio=0)
            produccion.save()
        elif tipo == 'ventaGanado':
            tipo_ganado = request.POST.get('tipoGanado')
            cantidad = request.POST.get('cantidadCabezas')
            ids_vent = request.POST.getlist('idCabezas')
            ids_list = ','.join(ids_vent) 
            precio = request.POST.get('precioVenta')
            adicional = request.POST.get('observacionesGanado')
            produccion = Produccion(tipo=tipo, tipo_ganado=tipo_ganado, cantidad_vendidas=cantidad, id_vendidas=ids_list, precio=precio, adicional=adicional,
                                cantidad_leche=0, vaca=0)
            produccion.save()

            for animal_id in ids_vent:
                animal = Animal.objects.get(num_id=animal_id)
                animal.estado = 'vendido'
                animal.save()
        messages.success(request, 'Registro insertado con éxito.')
    return HttpResponseRedirect(reverse('production'))

#Eliminar producción
def delete_production(request, produccion_id):
    db_data = Produccion.objects.filter(id=produccion_id)
    db_data.delete()
    messages.success(request, 'El registro ha sido eliminado.')
    return HttpResponseRedirect(reverse('production'))

# Tabla administrador/registros-salud
@login_required
@rol_required('administrador')
def record(request):
    animal_data = Animal.objects.all()
    context = {
        'animal_data': animal_data,
    }
    return render(request, 'granja/registros_vet.html', context)

# TRABAJADOR
@login_required
@rol_required('trabajador')
def worker(request):
    return render(request, 'granja/trabajador.html')

# Tabla trabajador/animales
@login_required
@rol_required('trabajador')
def animals2(request):
    return render(request, 'granja/animales2.html')

# Tabla trabajador/produccion
@login_required
@rol_required('trabajador')
def production2(request):
    return render(request, 'granja/produccion2.html')

# Tabla trabajador/suministros
@login_required
@rol_required('trabajador')
def supplies2(request):
    return render(request, 'granja/suministros2.html')

# VETERINARIO
@login_required
@rol_required('veterinario')
def vet(request):
    return render(request, 'granja/veterinario.html')

# Tabla veterinario/registros-salud
@login_required
@rol_required('veterinario')
def record2(request):
    return render(request, 'granja/registros_vet2.html')

# Generar datos para grafico automaticamente
@login_required
@rol_required('administrador')
def get_chart(_request):
    colors = ['blue', 'orange', 'red', 'black', 'yellow', 'green', 'magenta', 'lightblue', 'purple', 'brown']
    random_color = colors[randrange(0, (len(colors)-1))]

    serie = []
    counter = 0

    while (counter < 7):
        serie.append(randrange(100, 400))
        counter += 1

    chart = {
        'tooltip': {
            'show': True,
            'trigger': "axis",
            'triggerOn': "mousemove|click"
        },
        'xAxis': [
            {
                'type': "category",
                'data': ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            }
        ],
        'yAxis': [
            {
                'type': "value"
            }
        ],
        'series': [
            {
                'data': serie,
                'type': "line",
                'itemStyle': {
                    'color': random_color
                },
                'lineStyle': {
                    'color': random_color
                }
            }
        ]
    }

    return JsonResponse(chart)