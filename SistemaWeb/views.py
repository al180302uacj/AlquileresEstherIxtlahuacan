from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate # - Autenticar Usuarios
from .models import *
from django.contrib.auth.decorators import login_required # - Protejer Rutas
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import json
from datetime import datetime
from django.contrib import messages
from django.db.models.functions import TruncMonth, ExtractYear
from django.utils.timezone import localtime
import cloudinary.uploader


# Create your views here.
def home (request):
    return render(request, 'index.html')


def SignUp(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password-confirm')
        is_admin = request.POST.get('is-admin')
        admin_key = request.POST.get('clave-acceso')

        if password != password_confirm:
            return render(request, 'signup.html', {
                'error': '<strong>¡Error!</strong> Las Contraseñas no Coinciden!'
            })
        
        if is_admin:
            if admin_key == settings.ADMIN_KEY:
                user = Usuario.objects.create_user(
                username = email,
                first_name = first_name,
                last_name = last_name,
                email = email,
                direccion = address,
                telefono = phone,
                is_admin = True
                )

                user.set_password(password)
                user.save()
                login(request, user)
                return redirect('home')

            else:
                return render(request, 'signup.html', {
                    'error': '<strong>¡Error!</strong> Clave de Administrador Incorrecta!'
                })
        else:
            user = Usuario.objects.create_user(
                username = email,
                first_name = first_name,
                last_name = last_name,
                email = email,
                direccion = address,
                telefono = phone
            )
            user.set_password(password)
            user.save()
            login(request, user)
        
        return redirect('home')


def LogIn(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        user = authenticate(request, username = request.POST['email'], password = request.POST['password'])
        if user is None:
            return render(request, 'login.html', {
                'error': '<strong>¡Error!</strong> Usuario / Contraseña Incorrecto!'
            })
        else:
            login(request, user)
            return redirect('home')


@login_required
def LogOut(request):
    logout(request)
    return redirect('home')


def Contact(request):
    if request.method == 'GET':
        return render(request, 'contact.html')
    else:
        nombre = request.POST['name']
        email = request.POST['email']
        mensaje = request.POST['message']

        send_mail(
            'Nuevo mensaje de ' + nombre,
            mensaje,
            email,
            [settings.EMAIL_HOST_USER],
        )

        messages.success(request, '<strong>¡Éxito!</strong> Tu Mensaje ha Sido Enviado!')

        return render(request, 'contact.html')
        

def Products(request):
    if request.user.is_authenticated:
        usuario = request.user
        orden, creado = Orden.objects.get_or_create(usuario=usuario, completado=False)
        productoSelect = orden.ordenproducto_set.values_list('producto_id', flat=True)
    else:
        productoSelect = []

    productos = Producto.objects.all()

    return render(request, 'products.html', {
        'productos': productos,
        'productoSelect': productoSelect
    })


@login_required
def AddProduct(request):
    if not request.user.is_admin:
        return render(request, 'acceso_denegado.html', status=403)

    categorias = CategoriaProducto.objects.all()

    if request.method == 'GET':
        return render(request, 'add_product.html', {
            'categorias': categorias,
        })
    else:
        imagen = request.FILES.get('image')
        nombre = request.POST.get('name')
        descripcion = request.POST.get('description')
        precio = request.POST.get('price')
        disponibilidad = request.POST.get('stock')
        categoria_id = request.POST.get('category')

        if not nombre or not descripcion or not precio or not disponibilidad or not categoria_id:
            return render(request, 'add_product.html', {
                'categorias': categorias,
                'error': 'Todos los campos son obligatorios!'
            })
        
        try:
            precio = float(precio)
            disponibilidad = int(disponibilidad)
        except ValueError:
            return render(request, 'add_product.html', {
                'categorias': categorias,
                'error': 'Error al capturar Precio / Stock!'
            })
        
        if precio < 0 or disponibilidad < 0:
            return render(request, 'add_product.html', {
                'categorias': categorias,
                'error': 'Precio / Stock no valido!',
            })
        
        categorias = CategoriaProducto.objects.get(id = categoria_id)

        url_imagen = None
        if imagen:
            resultado = cloudinary.uploader.upload(imagen, folder="alquileres_esther")
            url_imagen = resultado.get("secure_url")

        producto = Producto(
            imagen = url_imagen,
            nombre = nombre,
            descripcion = descripcion,
            precio_renta = precio,
            stock = disponibilidad,
            categoria = categorias
        )
        producto.save()

        return redirect('products') 


@login_required
def DeleteProduct(request, producto_id):
    if not request.user.is_admin:
        return render(request, 'acceso_denegado.html', status=403)

    producto = get_object_or_404(Producto, id = producto_id)
    producto.delete()
    return redirect('admin')


@login_required
def EditProduct(request, producto_id):
    if not request.user.is_admin:
        return render(request, 'acceso_denegado.html', status=403)

    categorias = CategoriaProducto.objects.all()
    producto = get_object_or_404(Producto, id = producto_id)

    if request.method == 'GET':
        return render(request, 'edit_product.html', {
            'categorias': categorias,
            'producto': producto
    })
    else:
        imagen = request.FILES.get('image')
        nombre = request.POST.get('name')
        descripcion = request.POST.get('description')
        precio = request.POST.get('price')
        disponibilidad = request.POST.get('stock')
        categoria_id = request.POST.get('category')

        if not nombre or not descripcion or not precio or not disponibilidad or not categoria_id:
            return render(request, 'edit_product.html', {
                'categorias': categorias,
                'producto': producto,
                'error': 'Todos los campos son obligatorios!',
        })

        try:
            precio = float(precio)
            disponibilidad = int(disponibilidad)
        except ValueError:
            return render(request, 'edit_product.html', {
                'categorias': categorias,
                'producto': producto,
                'error': 'Error al capturar Precio / Stock!',
            })
        
        if precio < 0 or disponibilidad < 0:
            return render(request, 'edit_product.html', {
                'categorias': categorias,
                'producto': producto,
                'error': 'Precio / Stock no valido!',
            })
        
        categoria = CategoriaProducto.objects.get(id=categoria_id)
        if imagen:
            resultado = cloudinary.uploader.upload(imagen, folder="alquileres_esther")
            producto.imagen = resultado.get("secure_url")

        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.precio_renta = precio
        producto.stock = disponibilidad
        producto.categoria = categoria
        producto.save()

        return redirect('admin') 


@login_required
def Account(request):
    rentas = Orden.objects.filter(usuario = request.user, completado = True).order_by('-id')

    return render(request, 'account.html', {
        'nombre': request.user.first_name,
        'apellido': request.user.last_name,
        'direccion': request.user.direccion,
        'telefono': request.user.telefono,
        'correo': request.user.email,
        'ingreso': request.user.date_joined,
        'admin': request.user.is_admin,

        'rentas': rentas,
    })


@login_required
def Admin(request):
    if not request.user.is_admin:
        return render(request, 'acceso_denegado.html', status=403)

    productos = Producto.objects.all().order_by('categoria')
    rentas = Orden.objects.filter(completado=True, fecha_evento__isnull=False).order_by('-fecha_evento')

    MESES_ES = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    # --- MESES ---
    meses_rentas = (
        rentas.annotate(mes=TruncMonth('fecha_evento'))
            .values_list('mes', flat=True)
            .distinct()
    )

    meses_filtrados = sorted(set([
        (mes.month, MESES_ES[mes.month]) for mes in meses_rentas if mes
    ]))

    # --- AÑOS ---
    anios_filtrados = sorted(
        set(rentas.annotate(anio=ExtractYear('fecha_evento'))
            .values_list('anio', flat=True)
            .distinct()),
        reverse=True
    )

    usuarios_filtrados = Usuario.objects.filter(is_superuser=False).order_by('first_name')

    estados_filtrados = Estados.choices

    return render(request, 'admin.html', {
        'productos': productos,
        'rentas': rentas,
        'meses_filtrados': meses_filtrados,
        'anios_filtrados': anios_filtrados,
        'usuarios_filtrados': usuarios_filtrados,
        'estados_filtrados': estados_filtrados, 
    })


@login_required
def Rent(request):
    if request.user.is_authenticated:
        usuario = request.user
        orden, creado = Orden.objects.get_or_create(usuario = usuario, completado = False)
        items = orden.ordenproducto_set.all()
        direccion_usuario = usuario.direccion

    return render(request, 'rent.html', {
        'items': items,
        'orden': orden,
        'direccion_usuario': direccion_usuario
    })


@login_required
def UpdateOrder(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    usuario = request.user
    producto = Producto.objects.get(id = productId)
    orden, creado = Orden.objects.get_or_create(usuario = usuario, completado = False)

    ordenProducto, creado = OrdenProducto.objects.get_or_create(producto = producto, orden = orden)

    if action == 'add':
        if ordenProducto.cantidad < producto.stock:
            ordenProducto.cantidad = (ordenProducto.cantidad + 1)
        else:
            return JsonResponse({'error': 'No hay más unidades disponibles!'})
    elif action == 'remove':
        ordenProducto.cantidad = (ordenProducto.cantidad - 1)
    elif action == 'delete':
        ordenProducto.delete()
        return JsonResponse({
            'productId': productId,
            'cantidad': ordenProducto.cantidad
        })

    ordenProducto.save()

    if ordenProducto.cantidad <= 0:
        ordenProducto.delete()

    return JsonResponse({
        'productId': productId,
        'cantidad': ordenProducto.cantidad
    })


@login_required
def ProcessRent(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        usuario = request.user
        orden, creado = Orden.objects.get_or_create(usuario = usuario, completado = False)

        total = float(data['form']['total'].replace(',', '.'))
        direccionEnvio = data['form']['direccion_envio']
        fechaEvento = data['form']['fecha_evento']
        nombre_cliente = data['form'].get('nombre_cliente', None)
        telefono_cliente = data['form'].get('telefono_cliente', None)

        fecha_evento_obj = datetime.fromisoformat(fechaEvento)

        orden.direccion_envio = direccionEnvio
        orden.fecha_evento = fecha_evento_obj

        if request.user.is_admin or request.user.is_superuser:
            if nombre_cliente:
                orden.nombre_cliente = nombre_cliente
            if telefono_cliente:
                orden.telefono_cliente = telefono_cliente

        for item in orden.ordenproducto_set.all():
            producto = item.producto

            if producto.stock <= 0:
                return JsonResponse({
                    'message': f'Stock no Disponible del Producto: {producto.nombre}',
                    'status': 'error'
                })

            if producto.stock >= item.cantidad:
                producto.stock -= item.cantidad
                producto.save()

        if total == orden.total_select:
            orden.total = total
            orden.completado = True
            orden.save()

    return JsonResponse('Completando...', safe = False)


@login_required
def UpdateStatus(request, orden_id):
    if not request.user.is_admin:
        return render(request, 'acceso_denegado.html', status=403)

    renta = get_object_or_404(Orden, id = orden_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('order-status')
        estado_anterior = renta.estado

        estados_finales = ['Completado', 'Cancelado']

        # Sumar stock
        if nuevo_estado in estados_finales and estado_anterior not in estados_finales:
            for item in renta.ordenproducto_set.all():
                producto = item.producto
                producto.stock += item.cantidad
                producto.save()

        # Restar stock
        if estado_anterior in estados_finales and nuevo_estado not in estados_finales:
            for item in renta.ordenproducto_set.all():
                producto = item.producto
                producto.stock -= item.cantidad
                producto.save()

        renta.estado = nuevo_estado
        renta.save()

    return redirect('admin')


@login_required
def GenerateReport(request):
    if not request.user.is_admin:
        return render(request, 'acceso_denegado.html', status=403)

    if request.method == "POST":
        data = json.loads(request.body)
        mes = data.get('mes')
        anio = data.get('anio')
        usuario = data.get('usuario')
        estado = data.get('estado')
        todos = data.get('todos')

        ordenes = Orden.objects.select_related('usuario').prefetch_related('ordenproducto_set__producto')

        if not todos:

            # Meses
            if mes != "todos-meses":
                try:
                    ordenes = ordenes.filter(fecha_evento__month=int(mes))
                except ValueError:
                    return JsonResponse({"data": [], "error": "Mes inválido"}, status=400)
                
            # Años
            if anio != "all-years":
                try:
                    ordenes = ordenes.filter(fecha_evento__year=int(anio))
                except ValueError:
                    return JsonResponse({"data": [], "error": "Año inválido"}, status=400)
                
            # Usuario
            if usuario != "all-users":
                try:
                    ordenes = ordenes.filter(usuario__id=int(usuario))
                except ValueError:
                    return JsonResponse({"data": [], "error": "Usuario inválido"}, status=400)
                
            # Estado
            if estado != "all-status":
                ordenes = ordenes.filter(estado=estado)

        ordenes = ordenes.distinct().order_by('-fecha_evento')

        resultado = []
        for orden in ordenes:
            productos = orden.ordenproducto_set.all()
            for op in productos:
                nombre_cliente = orden.nombre_cliente if orden.nombre_cliente else f"{orden.usuario.first_name} {orden.usuario.last_name}"
                fecha_local = localtime(orden.fecha_evento) if orden.fecha_evento else None

                resultado.append({
                    "orden_id": orden.id,
                    "estado": orden.estado,
                    "usuario": nombre_cliente,
                    "direccion_envio": orden.direccion_envio,
                    "fecha_entrega": fecha_local.strftime("%d/%m/%Y") if fecha_local else "Sin Fecha",
                    "producto": op.producto.nombre,
                    "cantidad": op.cantidad,
                    "total": round(op.subtotal, 2),
                })

        return JsonResponse({"data": resultado})
