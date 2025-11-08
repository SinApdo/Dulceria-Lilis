# En: gestion/admin.py

from django.contrib import admin
from .models import Proveedor, MovimientoInventario

# Registramos los modelos del PDF
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'rut_nif', 'email', 'estado')
    search_fields = ('razon_social', 'rut_nif')
    list_filter = ('estado', 'pais')

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'producto', 'tipo', 'cantidad', 'proveedor', 'doc_ref')
    search_fields = ('producto__sku', 'producto__nombre', 'doc_ref', 'lote', 'serie')
    list_filter = ('tipo', 'bodega', 'fecha')
    autocomplete_fields = ('producto', 'proveedor') # Facilita la búsqueda