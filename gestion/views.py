# En: gestion/views.py

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalogo.models import Producto, Categoria, Marca
from .models import Proveedor, MovimientoInventario
from .forms import (ProductoForm, ProveedorForm, MovimientoForm, CustomUserCreationForm, CustomUserChangeForm, CategoriaForm, MarcaForm )
from django.db.models import Sum, Count
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import CustomUser
from django.urls import reverse_lazy
from openpyxl import Workbook

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

    productos = Producto.objects.all().order_by('nombre')
    
    context = {
        'form': form,
        'productos': productos
    }
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

    context = {
        'form': form,
        'producto': producto
    }
    return render(request, 'gestion/producto_form_edit.html', context)

@login_required
def producto_delete(request, sku):
    producto = get_object_or_404(Producto, sku=sku)
    try:
        producto.delete()
        messages.success(request, f'Producto {sku} eliminado.')
    except Exception as e:
        messages.error(request, f'No se puede eliminar el producto. Error: {e}')
    
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
            messages.error(request, 'Error al crear el proveedor. Revisa el formulario.')
    else:
        form = ProveedorForm()

    proveedores = Proveedor.objects.all().order_by('razon_social')
    
    context = {
        'form': form,
        'proveedores': proveedores
    }
    return render(request, 'gestion/proveedor_list.html', context)

@login_required
def proveedor_update(request, rut_nif):
    proveedor = get_object_or_404(Proveedor, rut_nif=rut_nif)
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Proveedor {rut_nif} actualizado.')
            return redirect('proveedor_list')
    else:
        form = ProveedorForm(instance=proveedor)

    context = {
        'form': form,
        'proveedor': proveedor
    }
    return render(request, 'gestion/proveedor_form_edit.html', context)

@login_required
def proveedor_delete(request, rut_nif):
    proveedor = get_object_or_404(Proveedor, rut_nif=rut_nif)
    try:
        proveedor.delete()
        messages.success(request, f'Proveedor {rut_nif} eliminado.')
    except Exception as e:
        messages.error(request, f'No se puede eliminar el proveedor. Puede tener registros asociados. Error: {e}')
    
    return redirect('proveedor_list')


# ----------------------------------------------
# --- 2. AÑADE ESTE BLOQUE QUE TE FALTA ---
# VISTA DE INVENTARIO
# ----------------------------------------------

@login_required
def inventario_list(request):
    # Lógica del Formulario de Registro
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            try:
                # El método .save() de nuestro modelo se encargará
                # de actualizar el stock y validar
                form.save()
                messages.success(request, 'Movimiento registrado y stock actualizado.')
                return redirect('inventario_list')
            except ValidationError as e:
                # Capturamos el error de "Stock insuficiente" del modelo
                messages.error(request, f"Error: {e.args[0]}")
            except Exception as e:
                messages.error(request, f"Error inesperado al guardar: {e}")
        else:
            messages.error(request, 'Error en el formulario. Revisa los datos.')
    else:
        form = MovimientoForm()

    # Lógica de los KPIs (Mockup pág. 11)
    today = timezone.now().date()
    kpis = {
        'movimientos_hoy': MovimientoInventario.objects.filter(fecha__date=today).count(), 
        'stock_total': Producto.objects.aggregate(total=Sum('stock_actual'))['total'] or 0, 
        'productos_unicos': Producto.objects.count() 
    }

    # Lógica de la Tabla "Movimientos"
    movimientos = MovimientoInventario.objects.all().select_related('producto', 'proveedor').order_by('-fecha')[:50] # (Mostramos los 50 más nuevos)
    
    context = {
        'form': form,
        'kpis': kpis,
        'movimientos': movimientos
    }
    return render(request, 'gestion/inventario_list.html', context)

    # En: gestion/views.py (al final)

# ----------------------------------------------
# CRUD DE USUARIOS
# ----------------------------------------------

@login_required
def user_list(request):
    # Solo los 'ROOT' o 'ADMIN' pueden gestionar usuarios
    if request.user.rol not in [CustomUser.Roles.ROOT, CustomUser.Roles.ADMIN]:
        messages.error(request, "No tienes permisos para gestionar usuarios.")
        return redirect('inicio_gestion')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('user_list')
        else:
            messages.error(request, 'Error al crear el usuario. Revisa el formulario.')
    else:
        form = CustomUserCreationForm()

    # Excluimos al usuario actual de la lista para que no se edite a sí mismo
    users = CustomUser.objects.exclude(pk=request.user.pk).order_by('username')
    
    context = {
        'form': form,
        'usuarios': users
    }
    return render(request, 'gestion/user_list.html', context)

@login_required
def user_update(request, pk):
    if request.user.rol not in [CustomUser.Roles.ROOT, CustomUser.Roles.ADMIN]:
        messages.error(request, "No tienes permisos para gestionar usuarios.")
        return redirect('inicio_gestion')

    user_to_edit = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {user_to_edit.username} actualizado.')
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user_to_edit)

    context = {
        'form': form,
        'usuario_editado': user_to_edit
    }
    return render(request, 'gestion/user_form_edit.html', context)

@login_required
def user_delete(request, pk):
    if request.user.rol not in [CustomUser.Roles.ROOT, CustomUser.Roles.ADMIN]:
        messages.error(request, "No tienes permisos para gestionar usuarios.")
        return redirect('inicio_gestion')
        
    user_to_delete = get_object_or_404(CustomUser, pk=pk)
    
    # Simple medida de seguridad para no borrar al usuario ROOT
    if user_to_delete.rol == CustomUser.Roles.ROOT:
        messages.error(request, 'No se puede eliminar al usuario ROOT.')
        return redirect('user_list')
        
    try:
        user_to_delete.delete()
        messages.success(request, f'Usuario {user_to_delete.username} eliminado.')
    except Exception as e:
        messages.error(request, f'No se puede eliminar al usuario. Error: {e}')
    
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
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm()

    categorias = Categoria.objects.all().order_by('nombre')
    context = {
        'form': form,
        'items': categorias, # Usamos 'items' como nombre genérico
        'titulo': 'Categorías'
    }
    # Reutilizaremos un template genérico para Categorías y Marcas
    return render(request, 'gestion/categoria_marca_list.html', context)

@login_required
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm(instance=categoria)

    context = {
        'form': form,
        'item': categoria,
        'titulo': 'Categoría',
        'lista_url': 'categoria_list' # Para el botón "Cancelar"
    }
    return render(request, 'gestion/categoria_marca_form_edit.html', context)

@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    try:
        categoria.delete()
        messages.success(request, f'Categoría "{categoria.nombre}" eliminada.')
    except Exception as e:
        messages.error(request, 'No se puede eliminar. Es probable que esté siendo usada por uno o más productos.')
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
            messages.success(request, 'Marca creada exitosamente.')
            return redirect('marca_list')
    else:
        form = MarcaForm()

    marcas = Marca.objects.all().order_by('nombre')
    context = {
        'form': form,
        'items': marcas, # Usamos 'items' como nombre genérico
        'titulo': 'Marcas'
    }
    return render(request, 'gestion/categoria_marca_list.html', context)

@login_required
def marca_update(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca actualizada.')
            return redirect('marca_list')
    else:
        form = MarcaForm(instance=marca)

    context = {
        'form': form,
        'item': marca,
        'titulo': 'Marca',
        'lista_url': 'marca_list' # Para el botón "Cancelar"
    }
    return render(request, 'gestion/categoria_marca_form_edit.html', context)

@login_required
def marca_delete(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    try:
        marca.delete()
        messages.success(request, f'Marca "{marca.nombre}" eliminada.')
    except Exception as e:
        messages.error(request, 'No se puede eliminar. Es probable que esté siendo usada por uno o más productos.')
    return redirect('marca_list')

# ----------------------------------------------
# VISTAS DE EXPORTACIÓN A EXCEL
# ----------------------------------------------

# --- PRODUCTOS---
@login_required
def exportar_productos_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Productos"
    ws.append(['SKU', 'Nombre', 'Categoría', 'Stock', 'Precio Neto', 'Precio c/IVA'])
    
    productos = Producto.objects.all().order_by('sku')
    for p in productos:
        categoria = p.categoria.nombre if p.categoria else "N/A"
        ws.append([p.sku, p.nombre, categoria, p.stock_actual, p.precio_venta, p.precio_venta_con_iva])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="listado_productos.xlsx"'
    wb.save(response)
    return response

# --- PROVEEDORES---
@login_required
def exportar_proveedores_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Proveedores"
    ws.append(['RUT/NIF', 'Razón Social', 'Email', 'Teléfono', 'Estado', 'País'])
    
    proveedores = Proveedor.objects.all().order_by('razon_social')
    for p in proveedores:
        ws.append([p.rut_nif, p.razon_social, p.email, p.telefono, p.get_estado_display(), p.pais])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="listado_proveedores.xlsx"'
    wb.save(response)
    return response

# --- INVENTARIO---
@login_required
def exportar_inventario_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Movimientos"
    ws.append(['Fecha', 'Tipo', 'SKU', 'Producto', 'Cantidad', 'Proveedor', 'Bodega', 'Doc. Ref.', 'Lote'])
    
    movimientos = MovimientoInventario.objects.all().order_by('-fecha').select_related('producto', 'proveedor')
    for m in movimientos:
        producto_sku = m.producto.sku if m.producto else "N/A"
        producto_nombre = m.producto.nombre if m.producto else "N/A"
        proveedor_nombre = m.proveedor.razon_social if m.proveedor else "N/A"
        
        ws.append([
            m.fecha.strftime('%Y-%m-%d %H:%M'), 
            m.get_tipo_display(), 
            producto_sku,
            producto_nombre,
            m.cantidad, 
            proveedor_nombre,
            m.bodega,
            m.doc_ref,
            m.lote
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="listado_inventario.xlsx"'
    wb.save(response)
    return response

# --- USUARIOS---
@login_required
def exportar_usuarios_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Usuarios"
    ws.append(['Username', 'Email', 'Nombre', 'Apellido', 'Rol', 'Estado', 'Último Acceso'])
    
    usuarios = CustomUser.objects.all().order_by('username')
    for u in usuarios:
        ws.append([
            u.username, 
            u.email, 
            u.first_name, 
            u.last_name, 
            u.get_rol_display(), 
            u.get_estado_display(),
            u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else "N/A"
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="listado_usuarios.xlsx"'
    wb.save(response)
    return response

# --- CATEGORÍAS---
@login_required
def exportar_categorias_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Categorías"
    ws.append(['Nombre'])
    
    items = Categoria.objects.all().order_by('nombre')
    for item in items:
        ws.append([item.nombre])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="listado_categorias.xlsx"'
    wb.save(response)
    return response

# --- MARCAS ---
@login_required
def exportar_marcas_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Marcas"
    ws.append(['Nombre'])
    
    items = Marca.objects.all().order_by('nombre')
    for item in items:
        ws.append([item.nombre])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="listado_marcas.xlsx"'
    wb.save(response)
    return response