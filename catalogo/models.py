# En: catalogo/models.py

from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Categoría')

    def __str__(self):
        return self.nombre

# --- AÑADIR ESTE MODELO ---
class Marca(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Marca')

    def __str__(self):
        return self.nombre

class Producto(models.Model):

    # --- 1. Identificación (Campos ajustados/añadidos) ---
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU") # Ajustado (Requerido)
    ean_upc = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="EAN/UPC") # Añadido
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Producto')
    descripcion = models.TextField(verbose_name='Descripción Breve', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True) # Blank=True
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True) # Añadido
    
    # --- 2. Precios (Campos añadidos) ---
    costo_estandar = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo Estándar") # Añadido
    costo_promedio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo Promedio", editable=False) # Añadido
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Precio de Venta (Neto)")
    
    # El PDF indica guardar el % (ej. 19). Guardar el % es más flexible.
    impuesto_iva = models.DecimalField(max_digits=4, decimal_places=2, default=19.00, verbose_name="IVA (%)") # Ajustado

    # --- 3. Stock y Control (Campos añadidos) ---
    stock_actual = models.PositiveIntegerField(default=0, verbose_name="Stock Actual", editable=False) # ¡Añadido y Clave!
    stock_minimo = models.PositiveIntegerField(default=0, verbose_name="Stock Mínimo")
    stock_maximo = models.PositiveIntegerField(blank=True, null=True, verbose_name="Stock Máximo")
    punto_reorden = models.PositiveIntegerField(blank=True, null=True, verbose_name="Punto de Reorden") # Añadido
    
    perishable = models.BooleanField(default=False, verbose_name="Es Perecible") # Añadido
    control_por_lote = models.BooleanField(default=False, verbose_name="Control por Lote")
    control_por_serie = models.BooleanField(default=False, verbose_name="Control por Serie") # Añadido

    # --- 4. Atributos (Tus campos) y Media ---
    es_vegano = models.BooleanField(default=False, verbose_name="Es Vegano")
    sin_gluten = models.BooleanField(default=False, verbose_name="Sin Gluten")
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, verbose_name='Imagen')
    # ficha_tecnica = models.FileField(upload_to='fichas/', null=True, blank=True, verbose_name='Ficha Técnica') # Añadido del PDF

    def __str__(self):
        return f"{self.nombre} ({self.sku})"