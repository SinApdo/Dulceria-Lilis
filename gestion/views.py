# En: gestion/views.py

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from openpyxl import Workbook

# Modelos
from catalogo.models import Producto, Categoria, Marca
from .models import Proveedor, MovimientoInventario, CustomUser, Bodega

# Formularios
from .forms import (
    ProductoForm, ProveedorForm, MovimientoForm, 
    CustomUserCreationForm, CustomUserChangeForm, 
    CategoriaForm, MarcaForm, BodegaForm
)

# Utilidad para contraseñas (Crea gestion/utils.py si no existe con la función generar_password_robusta)
try:
    from .utils import generar_password_robusta
except ImportError:
    # Fallback por si no tienes el archivo utils.py
    import secrets
    import string
    def generar_password_robusta():
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            if (any(c.islower() for c in password) and any(c.isupper() for c in password) and any(c.isdigit() for c in password)):
                return password

# ----------------------------------------------
# VISTA DE INICIO
# ----------------------------------------------
@login_required 
def inicio_gestion(request):
    return render(request, 'gestion/inicio_gestion.html')

# ----------------------------------------------
# CRUD DE PRODUCTOS
# ----------------------------------------------
@login_required
def producto_list(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('producto_list')
        else:
            messages.error(request, 'Error al crear el producto. Revisa el formulario.')
    else:
        form = ProductoForm()

    # Búsqueda y Paginación
    query = request.GET.get('q', '')
    productos_list = Producto.objects.all().order_by('nombre')
    
    if query:
        productos_list = productos_list.filter(Q(nombre__icontains=query) | Q(sku__icontains=query))

    paginator = Paginator(productos_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'form': form, 'page_obj': page_obj, 'query': query}
    return render(request, 'gestion/producto_list.html', context)

@login_required
def producto_update(request, sku):
    producto = get_object_or_404(Producto, sku=sku)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto {sku} actualizado.')
            return redirect('producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'gestion/producto_form_edit.html', {'form': form, 'producto': producto})

@login_required
def producto_delete(request, sku):
    producto = get_object_or_404(Producto, sku=sku)
    try:
        producto.delete()
        messages.success(request, f'Producto {sku} eliminado.')
    except Exception as e:
        messages.error(request, f'No se puede eliminar. Error: {e}')
    return redirect('producto_list')

# ----------------------------------------------
# CRUD DE PROVEEDORES
# ----------------------------------------------
@login_required
def proveedor_list(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente.')
            return redirect('proveedor_list')
        else:
            messages.error(request, 'Error al crear el proveedor.')
    else:
        form = ProveedorForm()

    query = request.GET.get('q', '')
    proveedores_list = Proveedor.objects.all().order_by('razon_social')
    if query:
        proveedores_list = proveedores_list.filter(Q(razon_social__icontains=query) | Q(rut_nif__icontains=query))

    # Usamos 'proveedores' en el contexto para simplificar si no usas paginator aquí,
    # pero idealmente usa Paginator igual que en productos.
    context = {'form': form, 'proveedores': proveedores_list, 'query': query}
    return render(request, 'gestion/proveedor_list.html', context)

@login_required
def proveedor_update(request, rut_nif):
    proveedor = get_object_or_404(Proveedor, rut_nif=rut_nif)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado.')
            return redirect('proveedor_list')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'gestion/proveedor_form_edit.html', {'form': form, 'proveedor': proveedor})

@login_required
def proveedor_delete(request, rut_nif):
    proveedor = get_object_or_404(Proveedor, rut_nif=rut_nif)
    try:
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado.')
    except:
        messages.error(request, 'No se puede eliminar, tiene datos asociados.')
    return redirect('proveedor_list')

# ----------------------------------------------
# CRUD DE USUARIOS (Solo Admin/Root)
# ----------------------------------------------
@login_required
def user_list(request):
    if request.user.rol not in [CustomUser.Roles.ROOT, CustomUser.Roles.ADMIN]:
        messages.error(request, "No tienes permisos para gestionar usuarios.")
        return redirect('inicio_gestion')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            temp_pass = generar_password_robusta()
            user.set_password(temp_pass)
            user.debe_cambiar_clave = True
            user.save()
            
            # Enviar correo (consola)
            send_mail(
                'Bienvenido - Clave Temporal',
                f'Usuario: {user.username}\nClave: {temp_pass}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True
            )
            messages.success(request, f'Usuario creado. Clave enviada al correo.')
            return redirect('user_list')
        else:
            messages.error(request, 'Error al crear usuario.')
    else:
        form = CustomUserCreationForm()

    query = request.GET.get('q', '')
    users = CustomUser.objects.exclude(pk=request.user.pk).order_by('username')
    if query:
        users = users.filter(username__icontains=query)

    return render(request, 'gestion/user_list.html', {'form': form, 'usuarios': users})

@login_required
def user_update(request, pk):
    if request.user.rol not in [CustomUser.Roles.ROOT, CustomUser.Roles.ADMIN]:
        return redirect('inicio_gestion')
    user_to_edit = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado.')
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user_to_edit)
    return render(request, 'gestion/user_form_edit.html', {'form': form, 'usuario_editado': user_to_edit})

@login_required
def user_delete(request, pk):
    if request.user.rol not in [CustomUser.Roles.ROOT, CustomUser.Roles.ADMIN]:
        return redirect('inicio_gestion')
    user_to_delete = get_object_or_404(CustomUser, pk=pk)
    if user_to_delete.rol == CustomUser.Roles.ROOT:
        messages.error(request, 'No se puede eliminar al ROOT.')
    else:
        user_to_delete.delete()
        messages.success(request, 'Usuario eliminado.')
    return redirect('user_list')

# ----------------------------------------------
# CRUD DE CATEGORÍAS
# ----------------------------------------------
@login_required
def categoria_list(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm()
    
    query = request.GET.get('q', '')
    items = Categoria.objects.all().order_by('nombre')
    if query: items = items.filter(nombre__icontains=query)
    
    return render(request, 'gestion/categoria_marca_list.html', {'form': form, 'items': items, 'titulo': 'Categorías'})

@login_required
def categoria_update(request, pk):
    item = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('categoria_list')
    else:
        form = CategoriaForm(instance=item)
    return render(request, 'gestion/categoria_marca_form_edit.html', {'form': form, 'item': item, 'titulo': 'Categoría', 'lista_url': 'categoria_list'})

@login_required
def categoria_delete(request, pk):
    item = get_object_or_404(Categoria, pk=pk)
    try:
        item.delete()
        messages.success(request, 'Categoría eliminada.')
    except:
        messages.error(request, 'No se puede eliminar.')
    return redirect('categoria_list')

# ----------------------------------------------
# CRUD DE MARCAS
# ----------------------------------------------
@login_required
def marca_list(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca creada.')
            return redirect('marca_list')
    else:
        form = MarcaForm()
    
    query = request.GET.get('q', '')
    items = Marca.objects.all().order_by('nombre')
    if query: items = items.filter(nombre__icontains=query)

    return render(request, 'gestion/categoria_marca_list.html', {'form': form, 'items': items, 'titulo': 'Marcas'})

@login_required
def marca_update(request, pk):
    item = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        form = MarcaForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('marca_list')
    else:
        form = MarcaForm(instance=item)
    return render(request, 'gestion/categoria_marca_form_edit.html', {'form': form, 'item': item, 'titulo': 'Marca', 'lista_url': 'marca_list'})

@login_required
def marca_delete(request, pk):
    item = get_object_or_404(Marca, pk=pk)
    try:
        item.delete()
        messages.success(request, 'Marca eliminada.')
    except:
        messages.error(request, 'No se puede eliminar.')
    return redirect('marca_list')

# ----------------------------------------------
# CRUD DE BODEGAS (¡EL QUE FALTABA!)
# ----------------------------------------------
@login_required
def bodega_list(request):
    if request.user.rol not in [CustomUser.Roles.ROOT, CustomUser.Roles.ADMIN]:
        messages.error(request, "Acceso denegado.")
        return redirect('inicio_gestion')

    if request.method == 'POST':
        form = BodegaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bodega creada.')
            return redirect('bodega_list')
    else:
        form = BodegaForm()
    
    items = Bodega.objects.all().order_by('nombre')
    return render(request, 'gestion/categoria_marca_list.html', {'form': form, 'items': items, 'titulo': 'Bodegas'})

@login_required
def bodega_update(request, pk):
    if request.user.rol not in [CustomUser.Roles.ROOT, CustomUser.Roles.ADMIN]: return redirect('inicio_gestion')
    item = get_object_or_404(Bodega, pk=pk)
    if request.method == 'POST':
        form = BodegaForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('bodega_list')
    else:
        form = BodegaForm(instance=item)
    return render(request, 'gestion/categoria_marca_form_edit.html', {'form': form, 'item': item, 'titulo': 'Bodega', 'lista_url': 'bodega_list'})

@login_required
def bodega_delete(request, pk):
    if request.user.rol not in [CustomUser.Roles.ROOT, CustomUser.Roles.ADMIN]: return redirect('inicio_gestion')
    item = get_object_or_404(Bodega, pk=pk)
    try:
        item.delete()
        messages.success(request, 'Bodega eliminada.')
    except:
        messages.error(request, 'No se puede eliminar.')
    return redirect('bodega_list')


# ----------------------------------------------
# INVENTARIO (TRANSACCIONAL)
# ----------------------------------------------
@login_required
def inventario_list(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Movimiento registrado.')
                return redirect('inventario_list')
            except ValidationError as e:
                messages.error(request, f"Error: {e.args[0]}")
        else:
            messages.error(request, 'Formulario inválido.')
    else:
        form = MovimientoForm()

    today = timezone.now().date()
    kpis = {
        'movimientos_hoy': MovimientoInventario.objects.filter(fecha__date=today).count(),
        'stock_total': Producto.objects.aggregate(total=Sum('stock_actual'))['total'] or 0,
        'productos_unicos': Producto.objects.count()
    }

    query = request.GET.get('q', '')
    movimientos = MovimientoInventario.objects.all().select_related('producto', 'proveedor', 'bodega').order_by('-fecha')
    if query:
        movimientos = movimientos.filter(Q(producto__sku__icontains=query) | Q(producto__nombre__icontains=query))

    return render(request, 'gestion/inventario_list.html', {'form': form, 'kpis': kpis, 'movimientos': movimientos[:50]})

# ----------------------------------------------
# EXPORTACIONES A EXCEL (OPTIMIZADO)
# ----------------------------------------------

# Función auxiliar para no repetir código
def export_base(filename, headers, data_generator):
    wb = Workbook()
    ws = wb.active
    ws.title = filename.capitalize()
    ws.append(headers)
    
    for row in data_generator:
        ws.append(row)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="listado_{filename}.xlsx"'
    wb.save(response)
    return response

@login_required
def exportar_productos_excel(request):
    # 1. Recuperar filtro
    query = request.GET.get('q', '')
    productos = Producto.objects.all().order_by('sku')
    
    # 2. Aplicar filtro (Igual que en la lista)
    if query:
        productos = productos.filter(Q(nombre__icontains=query) | Q(sku__icontains=query))

    # 3. Generar datos (Incluyendo Categoría legible y Precio con IVA)
    data = []
    for p in productos:
        cat_nombre = p.categoria.nombre if p.categoria else "Sin Categoría"
        # Usamos la propiedad .precio_venta_con_iva del modelo
        data.append([p.sku, p.nombre, cat_nombre, p.stock_actual, p.precio_venta, p.precio_venta_con_iva])

    return export_base('productos', ['SKU', 'Nombre', 'Categoría', 'Stock', 'Precio Neto', 'Precio c/IVA'], data)

@login_required
def exportar_proveedores_excel(request):
    query = request.GET.get('q', '')
    qs = Proveedor.objects.all().order_by('razon_social')
    
    if query:
        qs = qs.filter(Q(razon_social__icontains=query) | Q(rut_nif__icontains=query))

    data = ([p.rut_nif, p.razon_social, p.email, p.telefono, p.get_estado_display()] for p in qs)
    return export_base('proveedores', ['RUT', 'Razón Social', 'Email', 'Teléfono', 'Estado'], data)

@login_required
def exportar_inventario_excel(request):
    query = request.GET.get('q', '')
    qs = MovimientoInventario.objects.all().order_by('-fecha')
    
    if query:
        qs = qs.filter(Q(producto__sku__icontains=query) | Q(producto__nombre__icontains=query))

    # Incluimos Bodega y Tipo legible
    data = ([m.fecha.strftime('%Y-%m-%d'), m.get_tipo_display(), m.producto.sku, m.cantidad, m.bodega.nombre if m.bodega else ""] for m in qs)
    return export_base('inventario', ['Fecha', 'Tipo', 'Producto', 'Cantidad', 'Bodega'], data)

@login_required
def exportar_usuarios_excel(request):
    query = request.GET.get('q', '')
    qs = CustomUser.objects.all().order_by('username')
    
    if query:
        qs = qs.filter(Q(username__icontains=query) | Q(email__icontains=query))

    data = ([u.username, u.email, u.get_rol_display(), u.get_estado_display()] for u in qs)
    return export_base('usuarios', ['Usuario', 'Email', 'Rol', 'Estado'], data)

@login_required
def exportar_categorias_excel(request):
    # Las categorías suelen ser pocas, el filtro es opcional pero útil
    query = request.GET.get('q', '')
    qs = Categoria.objects.all().order_by('nombre')
    if query: qs = qs.filter(nombre__icontains=query)
    
    data = ([i.nombre] for i in qs)
    return export_base('categorias', ['Nombre'], data)

@login_required
def exportar_marcas_excel(request):
    query = request.GET.get('q', '')
    qs = Marca.objects.all().order_by('nombre')
    if query: qs = qs.filter(nombre__icontains=query)
    
    data = ([i.nombre] for i in qs)
    return export_base('marcas', ['Nombre'], data)