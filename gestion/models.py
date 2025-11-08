# En: gestion/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from catalogo.models import Producto  # Importamos el modelo Producto

# -----------------------------------------------------------------
# 1. MODELO PROVEEDOR (Corregido y Completo)
# -----------------------------------------------------------------
class Proveedor(models.Model):
    
    class EstadoChoices(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        BLOQUEADO = 'BLOQUEADO', 'Bloqueado'

    rut_nif = models.CharField(max_length=20, unique=True, verbose_name="RUT/NIF")
    razon_social = models.CharField(max_length=255, verbose_name="Razón Social")
    nombre_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nombre de Fantasía")
    
    email = models.EmailField(max_length=254)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    sitio_web = models.URLField(max_length=255, blank=True, null=True, verbose_name="Sitio Web")
    
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=128, blank=True, null=True)
    pais = models.CharField(max_length=64, default="Chile")
    
    # --- CAMPOS AÑADIDOS DEL PDF ---
    condiciones_pago = models.CharField(max_length=100, verbose_name="Condiciones de Pago", blank=True)
    moneda = models.CharField(max_length=8, default="CLP", blank=True)
    observaciones = models.TextField(blank=True, null=True)
    
    estado = models.CharField(max_length=10, choices=EstadoChoices.choices, default=EstadoChoices.ACTIVO)

    def __str__(self):
        return f"{self.razon_social} ({self.rut_nif})"

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"


# -----------------------------------------------------------------
# 2. MODELO MOVIMIENTO INVENTARIO (Corregido y Completo)
# -----------------------------------------------------------------
class MovimientoInventario(models.Model):
    
    # --- CORREGIDO: Tipos de movimiento del PDF ---
    class TipoMovimiento(models.TextChoices):
        INGRESO = 'IN', 'Ingreso'       # Suma
        SALIDA = 'OUT', 'Salida'         # Resta
        AJUSTE_POS = 'AJ-P', 'Ajuste Positivo' # Suma
        AJUSTE_NEG = 'AJ-N', 'Ajuste Negativo' # Resta
        DEVOLUCION = 'DEV', 'Devolución'   # Suma

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="movimientos")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    
    tipo = models.CharField(max_length=4, choices=TipoMovimiento.choices, verbose_name="Tipo de Movimiento")
    
    # --- CORREGIDO: Validación de no-negativos ---
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha")

    # --- CAMPOS AÑADIDOS DEL PDF ---
    bodega = models.CharField(max_length=100, default="BOD-CENTRAL", verbose_name="Bodega")
    doc_ref = models.CharField(max_length=100, blank=True, null=True, verbose_name="Documento Referencia")
    lote = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lote")
    serie = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serie")
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name="Fecha Vencimiento")
    observaciones = models.TextField(blank=True, null=True) # Tu campo, que también está en el PDF

    # --- CORREGIDO: Lógica de Stock Automática AÑADIDA ---
    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None 
        
        # Obtenemos el producto ANTES de guardar
        producto = self.producto
        
        if es_nuevo:
            # Es un nuevo movimiento, actualizamos el stock del producto
            if self.tipo in [self.TipoMovimiento.INGRESO, self.TipoMovimiento.AJUSTE_POS, self.TipoMovimiento.DEVOLUCION]:
                producto.stock_actual += self.cantidad
            
            elif self.tipo in [self.TipoMovimiento.SALIDA, self.TipoMovimiento.AJUSTE_NEG]:
                if producto.stock_actual < self.cantidad:
                    raise ValidationError(f"Stock insuficiente. Stock actual: {producto.stock_actual}, se intentó sacar: {self.cantidad}")
                producto.stock_actual -= self.cantidad
            
            producto.save(update_fields=['stock_actual']) # Guardamos solo el campo de stock
        
        super().save(*args, **kwargs) # Guardamos el movimiento

    def __str__(self):
        return f"[{self.fecha.strftime('%Y-%m-%d')}] {self.get_tipo_display()}: {self.cantidad} x {self.producto.sku}"

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']