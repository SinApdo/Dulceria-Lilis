# En: gestion/forms.py

from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from catalogo.models import Producto, Categoria, Marca
from .models import Proveedor, MovimientoInventario, CustomUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# -----------------------------------------------------------------
#FORMULARIO PARA CATEGORÍAS (¡AÑADE ESTO!)
# -----------------------------------------------------------------
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})

# -----------------------------------------------------------------
# FORMULARIO PARA MARCAS (¡AÑADE ESTO!)
# -----------------------------------------------------------------
class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})

# -----------------------------------------------------------------
# FORMULARIO PARA CREAR USUARIOS
# -----------------------------------------------------------------
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        # Campos que se piden al CREAR un usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'telefono', 'rol', 'estado')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Aplicamos estilos de Bootstrap
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            else:
                field.widget.attrs.setdefault('class', 'form-control')

# -----------------------------------------------------------------
# FORMULARIO PARA EDITAR USUARIOS
# -----------------------------------------------------------------
class CustomUserChangeForm(UserChangeForm):
    # Quitamos el campo de contraseña, no queremos cambiarla aquí
    password = None 

    class Meta:
        model = CustomUser
        # Campos que se pueden EDITAR
        fields = ('username', 'email', 'first_name', 'last_name', 'telefono', 'rol', 'estado', 'mfa_habilitado')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            else:
                field.widget.attrs.setdefault('class', 'form-control')
        
        # Hacemos que el username (nombre de usuario) no se pueda editar
        self.fields['username'].widget.attrs['readonly'] = True


# --- Formulario de Producto (ACTUALIZADO) ---
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # --- LISTA DE CAMPOS ACTUALIZADA ---
        fields = [
            # Tab 1
            'sku', 'ean_upc', 'nombre', 'descripcion', 
            'categoria', 'marca', 'modelo',
            'uom_compra', 'uom_venta', 'factor_conversion',
            'costo_estandar', 'precio_venta', 'impuesto_iva',
            # Tab 2
            'stock_minimo', 'stock_maximo', 'punto_reorden',
            'perishable', 'control_por_lote', 'control_por_serie',
            # Tab 3
            'imagen', 'ficha_tecnica_url',
            # Atributos (los ponemos en una tab)
            'es_vegano', 'sin_gluten',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Bucle de estilos (ya está corregido para checkboxes)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, (forms.ClearableFileInput, forms.FileInput)):
                field.widget.attrs.setdefault('class', 'form-control')
            else:
                field.widget.attrs.setdefault('class', 'form-control')

        # Lógica de solo lectura (IVA, SKU, EAN)
        self.fields['sku'].widget.attrs['readonly'] = True
        self.fields['ean_upc'].widget.attrs['readonly'] = True
        self.fields['impuesto_iva'].widget.attrs['readonly'] = True

    # ... (tu método 'clean' sin cambios) ...
    def clean(self):
        # ... (código de validación de stock) ...
        cleaned_data = super().clean()
        stock_minimo = cleaned_data.get("stock_minimo")
        stock_maximo = cleaned_data.get("stock_maximo")
        if stock_maximo is not None and stock_minimo is not None:
            if stock_maximo < stock_minimo:
                raise ValidationError("Error: El Stock Máximo no puede ser menor que el Stock Mínimo.")
        return cleaned_data

# --- Formulario de Proveedor (ACTUALIZADO) ---
class ProveedorForm(forms.ModelForm):
    # products = forms.ModelMultipleChoiceField(
    #     queryset=Producto.objects.all(),
    #     widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
    #     required=False,
    #     label="Productos Suministrados"
    # )

    class Meta:
        model = Proveedor
        # --- LISTA DE CAMPOS ACTUALIZADA ---
        fields = [
            # Tab 1
            'rut_nif', 'razon_social', 'nombre_fantasia',
            'email', 'telefono', 'sitio_web',
            # Tab 2
            'direccion_legal', 'ciudad', 'pais',
            'contacto_comercial_nombre', 'contacto_comercial_telefono',
            'condiciones_pago', 'moneda', 'estado', 'observaciones',
            # Tab 3 (El ManyToManyField se gestiona de forma diferente)
            'productos_suministrados' # Aunque lo gestionaremos fuera del Meta.fields
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
        
        # El RUT/NIF es solo lectura si ya existe (para edición)
        if self.instance and self.instance.pk:
            self.fields['rut_nif'].widget.attrs['readonly'] = True
        
        # Aseguramos que los ManyToManyFields se muestren correctamente
        if 'productos_suministrados' in self.fields:
            self.fields['productos_suministrados'].widget.attrs.update({'class': 'form-select select2-enable', 'multiple': 'multiple'})
            # Puedes usar 'forms.SelectMultiple' para un mejor control visual
            self.fields['productos_suministrados'].widget = forms.SelectMultiple(attrs={'class': 'form-control'})

# --- Formulario de Movimiento (Sin cambios) ---
class MovimientoForm(forms.ModelForm):
    
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tipo = forms.ChoiceField(
        choices=MovimientoInventario.TipoMovimiento.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = MovimientoInventario
        
        # --- CAMPOS REORDENADOS POR PESTAÑA ---
        fields = [
            # Pestaña 1
            'fecha', 'tipo', 'cantidad', 
            'producto', 'proveedor', 'bodega', 
            # Pestaña 2
            'lote', 'serie', 'fecha_vencimiento', 
            # Pestaña 3
            'doc_ref', 'motivo', 'observaciones' 
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- BUCLE DE ESTILOS ACTUALIZADO ---
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                 field.widget.attrs.setdefault('class', 'form-control')
            
            # Ajustamos campos opcionales
            if field_name in ['proveedor', 'doc_ref', 'lote', 'serie', 'fecha_vencimiento', 'observaciones', 'motivo']:
                field.required = False
            
            # Widgets de Fecha
            if field_name == 'fecha_vencimiento':
                field.widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
            if field_name == 'fecha':
                # Usamos datetime-local para la fecha y hora del movimiento
                field.widget = forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
                field.initial = timezone.now().strftime('%Y-%m-%dT%H:%M') # Valor inicial
            
            if field_name == 'bodega':
                field.initial = 'BOD-CENTRAL'
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad == 0:
            raise ValidationError("La cantidad del movimiento no puede ser cero.")
        return cantidad
    
    def clean_fecha_vencimiento(self):
        fecha = self.cleaned_data.get('fecha_vencimiento')
        if fecha and fecha < timezone.now().date():
            raise ValidationError("La fecha de vencimiento no puede ser una fecha pasada.")
        return fecha