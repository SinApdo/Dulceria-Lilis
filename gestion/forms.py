# En: gestion/forms.py

from django import forms
from catalogo.models import Producto
# --- 1. AÑADE ESTAS IMPORTACIONES ---
from .models import Proveedor, MovimientoInventario

# --- Formulario de Producto (CON SU __init__ CORREGIDO) ---
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'sku', 'ean_upc', 'nombre', 'descripcion', 
            'categoria', 'marca',
            'costo_estandar', 'precio_venta', 'impuesto_iva',
            'stock_minimo', 'stock_maximo', 'punto_reorden',
            'perishable', 'control_por_lote', 'control_por_serie',
            'es_vegano', 'sin_gluten', 'imagen'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añade clases de Bootstrap
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
            
        # El SKU no debería ser editable una vez creado
        if self.instance and self.instance.pk:
            self.fields['sku'].widget.attrs['readonly'] = True

# --- Formulario de Proveedor (CON SU __init__ CORREGIDO) ---
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'rut_nif', 'razon_social', 'nombre_fantasia',
            'email', 'telefono', 'sitio_web',
            'direccion', 'ciudad', 'pais',
            'condiciones_pago', 'moneda', 'estado', 'observaciones'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añade clases de Bootstrap
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        
        # El RUT no debería ser editable una vez creado
        if self.instance and self.instance.pk:
            self.fields['rut_nif'].widget.attrs['readonly'] = True

# --- 3. AÑADE ESTE NUEVO FORMULARIO ---
class MovimientoForm(forms.ModelForm):
    
    # Hacemos que los campos de selección sean más amigables
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}) # form-select es mejor para <select>
    )
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.all(),
        required=False, # No siempre se requiere un proveedor (ej. Salida)
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tipo = forms.ChoiceField(
        choices=MovimientoInventario.TipoMovimiento.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    bodega = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


    class Meta:
        model = MovimientoInventario
        
        # Campos basados en el mockup (pág. 11)
        fields = [
            'producto', 'tipo', 'cantidad', 
            'proveedor', 'bodega', 'doc_ref',
            'lote', 'serie', 'fecha_vencimiento', 'observaciones'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añade clases de Bootstrap a los campos restantes
        for field_name, field in self.fields.items():
            # Aplicamos la clase base a todos
            if not field.widget.attrs.get('class'):
                 field.widget.attrs.setdefault('class', 'form-control')
            
            # Ajustamos campos opcionales del PDF
            if field_name in ['proveedor', 'doc_ref', 'lote', 'serie', 'fecha_vencimiento', 'observaciones']:
                field.required = False
            
            # Ajustamos los widgets para fecha
            if field_name == 'fecha_vencimiento':
                field.widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})