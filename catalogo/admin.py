# En: catalogo/admin.py

from django.contrib import admin
from .models import Producto, Categoria, Marca

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',) # Necesario si Producto lo usa en autocomplete

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',) # Necesario si Producto lo usa en autocomplete

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'marca', 'precio_venta', 'stock_actual')
    list_filter = ('categoria', 'marca', 'perishable', 'control_por_lote')
    
    # --- ESTA ES LA LÍNEA QUE SOLUCIONA EL ERROR ---
    # Le dice a Django cómo buscar un Producto
    search_fields = ('sku', 'nombre', 'ean_upc') 
    
    # Opcional, pero recomendado para buscar Categorías y Marcas
    autocomplete_fields = ('categoria', 'marca')