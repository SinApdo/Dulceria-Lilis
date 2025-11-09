# En: catalogo/models.py

from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Categoría')
    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Marca')
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    # --- 1. Identificación ---
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU", blank=True)
    ean_upc = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="EAN/UPC")
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Producto')
    descripcion = models.TextField(verbose_name='Descripción Breve', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo") # <-- NUEVO

    # --- 2. Precios y Unidades ---
    uom_compra = models.CharField(max_length=50, blank=True, null=True, verbose_name="UOM Compra") # <-- NUEVO
    uom_venta = models.CharField(max_length=50, blank=True, null=True, verbose_name="UOM Venta") # <-- NUEVO
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="Factor Conversión") # <-- NUEVO
    
    costo_estandar = models.PositiveIntegerField(default=0, verbose_name="Costo Estándar")
    costo_promedio = models.PositiveIntegerField(default=0, verbose_name="Costo Promedio", editable=False)
    precio_venta = models.PositiveIntegerField(default=0, verbose_name="Precio de Venta (Neto)")
    impuesto_iva = models.IntegerField(default=19, verbose_name="IVA (%)")

    # --- 3. Stock y Control ---
    stock_actual = models.PositiveIntegerField(default=0, verbose_name="Stock Actual", editable=False)
    stock_minimo = models.PositiveIntegerField(default=0, verbose_name="Stock Mínimo")
    stock_maximo = models.PositiveIntegerField(blank=True, null=True, verbose_name="Stock Máximo")
    punto_reorden = models.PositiveIntegerField(blank=True, null=True, verbose_name="Punto de Reorden")
    
    perishable = models.BooleanField(default=False, verbose_name="Es Perecible")
    control_por_lote = models.BooleanField(default=False, verbose_name="Control por Lote")
    control_por_serie = models.BooleanField(default=False, verbose_name="Control por Serie")

    # --- 4. Relaciones y Atributos ---
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, verbose_name='Imagen')
    ficha_tecnica_url = models.FileField(upload_to='fichas/', null=True, blank=True, verbose_name='Ficha Técnica') # <-- NUEVO
    es_vegano = models.BooleanField(default=False, verbose_name="Es Vegano")
    sin_gluten = models.BooleanField(default=False, verbose_name="Sin Gluten")
    
    # --- 5. Propiedades (Derivados) ---
    @property
    def precio_venta_con_iva(self):
        if self.precio_venta is None or self.impuesto_iva is None:
            return 0
        precio_con_iva = self.precio_venta * (1 + (self.impuesto_iva / 100))
        return round(precio_con_iva)
    
    @property
    def alerta_bajo_stock(self): # <-- NUEVO
        if self.stock_actual <= self.stock_minimo:
            return "SÍ"
        return "NO"
    
    @property
    def alerta_por_vencer(self): # <-- NUEVO
        # Esta lógica es más compleja, requiere Lotes con fechas.
        # Por ahora, solo revisa si es perecible.
        if self.perishable:
            return "REVISAR" # O 'SÍ' si tienes lógica de lotes
        return "NO"

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

    # Lógica de SKU y EAN (sin cambios)
    def save(self, *args, **kwargs):
        is_new = self.pk is None 
        super().save(*args, **kwargs) 
        if is_new and not self.sku:
            self.sku = f"PROD-{self.id:05d}" 
            if not self.ean_upc:
                self.ean_upc = f"780000{self.id:06d}" 
            super().save(update_fields=['sku', 'ean_upc'])