# En: gestion/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser # <-- AÑADE ESTA IMPORTACIÓN
from django.core.exceptions import ValidationError
from django.utils import timezone
from catalogo.models import Producto

# -----------------------------------------------------------------
# 1. MODELO DE USUARIO PERSONALIZADO
# -----------------------------------------------------------------

class CustomUser(AbstractUser):
    
    # --- Roles del Sistema ---
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        AUDITOR = 'AUDITOR', 'Auditor'
        OPERADOR = 'OPERADOR', 'Operador'
        # Añadimos ROOT como en el mockup
        ROOT = 'ROOT', 'Root' 

    # --- Estados del Usuario ---
    class Estados(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        INACTIVO = 'INACTIVO', 'Inactivo'
        BLOQUEADO = 'BLOQUEADO', 'Bloqueado'

    # Campos de Identificación (nombres y apellidos ya vienen en AbstractUser como first_name y last_name)
    # 'username' y 'email' ya vienen en AbstractUser
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    
    # Campos de Estado y Acceso
    rol = models.CharField(max_length=10, choices=Roles.choices, default=Roles.OPERADOR, verbose_name="Rol")
    estado = models.CharField(max_length=10, choices=Estados.choices, default=Estados.ACTIVO, verbose_name="Estado")
    mfa_habilitado = models.BooleanField(default=False, verbose_name="MFA Habilitado")
    
    # 'ultimo_acceso' (last_login) ya viene en AbstractUser
    # 'sesiones_activas' es un campo muy complejo de implementar (requiere un backend de sesiones),
    # por ahora lo omitimos del modelo y lo mostraremos "falso" en el template.

    def __str__(self):
        return self.username

# -----------------------------------------------------------------
# 2. MODELO PROVEEDOR
# -----------------------------------------------------------------
class Proveedor(models.Model):
    # --- 1. Identificación y Contacto ---
    rut_nif = models.CharField(max_length=20, unique=True, verbose_name="RUT/NIF")
    razon_social = models.CharField(max_length=255, verbose_name="Razón Social")
    nombre_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nombre de Fantasía")
    email = models.EmailField(blank=True, null=True, verbose_name="Email de Contacto")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")
    sitio_web = models.URLField(blank=True, null=True, verbose_name="Sitio Web")

    # --- 2. Dirección y Comercial --- # <-- NUEVOS CAMPOS
    direccion_legal = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección Legal")
    ciudad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    pais = models.CharField(max_length=100, blank=True, null=True, verbose_name="País")
    contacto_comercial_nombre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contacto Comercial")
    contacto_comercial_telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono Comercial")
    condiciones_pago = models.CharField(max_length=100, blank=True, null=True, verbose_name="Condiciones de Pago")
    moneda = models.CharField(max_length=10, default='CLP', verbose_name="Moneda Predeterminada")
    estado = models.CharField(
        max_length=20,
        choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo'), ('BLOQUEADO', 'Bloqueado')],
        default='ACTIVO',
        verbose_name="Estado"
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    # --- 3. Relación con Productos --- # <-- NUEVOS CAMPOS
    # Esto ya estaba en esencia, pero lo podemos formalizar aquí
    productos_suministrados = models.ManyToManyField(Producto, blank=True, related_name='proveedores_asociados', verbose_name="Productos Suministrados")
    
    # Podrías añadir campos para "certificaciones", "acuerdos", etc. aquí si fuera necesario.

    def __str__(self):
        return f"{self.razon_social} ({self.rut_nif})"

# -----------------------------------------------------------------
# 3. MODELO MOVIMIENTO INVENTARIO
# -----------------------------------------------------------------
class MovimientoInventario(models.Model):
    
    class TipoMovimiento(models.TextChoices):
        INGRESO = 'IN', 'Ingreso'
        SALIDA = 'OUT', 'Salida'
        AJUSTE_POS = 'AJ-P', 'Ajuste Positivo'
        AJUSTE_NEG = 'AJ-N', 'Ajuste Negativo'
        DEVOLUCION = 'DEV', 'Devolución'

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="movimientos")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    
    tipo = models.CharField(max_length=4, choices=TipoMovimiento.choices, verbose_name="Tipo de Movimiento")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    
    # Este campo ya era editable, está perfecto para la Pestaña 1
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha")

    bodega = models.CharField(max_length=100, default="BOD-CENTRAL", verbose_name="Bodega")
    
    # --- Campos de la Pestaña 2 ---
    lote = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lote")
    serie = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serie")
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name="Fecha Vencimiento")

    # --- Campos de la Pestaña 3 ---
    doc_ref = models.CharField(max_length=100, blank=True, null=True, verbose_name="Doc. Referencia")
    motivo = models.CharField(max_length=255, blank=True, null=True, verbose_name="Motivo (ajustes/devoluciones)") # <-- NUEVO CAMPO
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones (notas de operación)")

    # --- Lógica de Stock (Sin cambios) ---
    def save(self, *args, **kwargs):
        # ... (tu lógica de save() sin cambios) ...
        es_nuevo = self.pk is None 
        producto = self.producto
        if es_nuevo:
            if self.tipo in [self.TipoMovimiento.INGRESO, self.TipoMovimiento.AJUSTE_POS, self.TipoMovimiento.DEVOLUCION]:
                producto.stock_actual += self.cantidad
            elif self.tipo in [self.TipoMovimiento.SALIDA, self.TipoMovimiento.AJUSTE_NEG]:
                if producto.stock_actual < self.cantidad:
                    raise ValidationError(f"Stock insuficiente. Stock actual: {producto.stock_actual}, se intentó sacar: {self.cantidad}")
                producto.stock_actual -= self.cantidad
            producto.save(update_fields=['stock_actual']) 
        super().save(*args, **kwargs) 

    def __str__(self):
        return f"[{self.fecha.strftime('%Y-%m-%d')}] {self.get_tipo_display()}: {self.cantidad} x {self.producto.sku}"

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']