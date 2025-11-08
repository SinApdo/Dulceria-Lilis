# En: gestion/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalogo.models import Producto
# --- 1. IMPORTA TODO LO NECESARIO ---
from .models import Proveedor, MovimientoInventario
from .forms import ProductoForm, ProveedorForm, MovimientoForm
from django.db.models import Sum, Count
from django.utils import timezone
from django.core.exceptions import ValidationError

# ----------------------------------------------
# VISTA DE INICIO
# ----------------------------------------------
@login_required 
def inicio_gestion(request):
    return render(request, 'gestion/inicio_gestion.html')

# ----------------------------------------------
# CRUD DE PRODUCTOS (Ya lo tienes)
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
# CRUD DE PROVEEDORES (Ya lo tienes)
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