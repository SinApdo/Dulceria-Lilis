from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Categoría')

    def __str__(self):
        return self.nombre



class Producto(models.Model):

    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU", null=True, blank=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Producto')
    descripcion = models.TextField(verbose_name='Descripción Breve', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)



    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Precio de Venta (Neto)")
    impuesto_iva = models.BooleanField(default=True, verbose_name="Aplica IVA (19%)")


    stock_minimo = models.PositiveIntegerField(default=0, verbose_name="Stock Mínimo")
    stock_maximo = models.PositiveIntegerField(blank=True, null=True, verbose_name="Stock Máximo")
    es_vegano = models.BooleanField(default=False, verbose_name="Es Vegano")
    sin_gluten= models.BooleanField(default=False, verbose_name="Sin Gluten")
    control_por_lote = models.BooleanField(default=False, verbose_name="Control por Lote")


    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, verbose_name='Imagen')

    def __str__(self):
        return f"{self.nombre} ({self.sku})"