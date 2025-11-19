# En: gestion/forms.py

from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from catalogo.models import Producto, Categoria, Marca
from .models import Proveedor, MovimientoInventario, CustomUser, Bodega
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
import re

# -----------------------------------------------------------------
#FORMULARIO PARA CATEGORÍAS
# -----------------------------------------------------------------
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})

# -----------------------------------------------------------------
# FORMULARIO PARA MARCAS
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
        self.fields['email'].required = True
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
    
    # --- 1. DEFINIMOS LAS OPCIONES DE UNIDAD DE MEDIDA ---
    UOM_CHOICES = [
        ('', 'Seleccione...'),
        ('UN', 'Unidad'),
        ('CAJA', 'Caja'),
        ('PAQ', 'Paquete'),
        ('KG', 'Kilos'),
        ('G', 'Gramos'),
        ('L', 'Litros'),
        ('ML', 'Mililitros'),
    ]

    # --- 2. REEMPLAZAMOS LOS CAMPOS DE TEXTO POR DROPDOWNS ---
    uom_compra = forms.ChoiceField(
        choices=UOM_CHOICES, 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="UOM Compra"
    )
    uom_venta = forms.ChoiceField(
        choices=UOM_CHOICES, 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="UOM Venta"
    )

    class Meta:
        model = Producto
        fields = [
            'sku', 'ean_upc', 'nombre', 'descripcion', 
            'categoria', 'marca', 'modelo',
            'uom_compra', 'uom_venta', 'factor_conversion',
            'costo_estandar', 'precio_venta', 'impuesto_iva',
            'stock_minimo', 'stock_maximo', 'punto_reorden',
            'perishable', 'control_por_lote', 'control_por_serie',
            'imagen', 'ficha_tecnica_url',
            'es_vegano', 'sin_gluten',
        ]
        
        widgets = {
            'imagen': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/png, image/jpeg, image/jpg' # Solo imágenes
                }
            ),
            'ficha_tecnica_url': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': '.pdf, .doc, .docx, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document' # Solo PDF y Word
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['categoria'].required = True
        self.fields['uom_compra'].required = True
        self.fields['uom_venta'].required = True
        

        # --- 3. BUCLE DE ESTILOS ACTUALIZADO ---
        for field_name, field in self.fields.items():
            
            # Si es un Checkbox
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            
            # Si es un Dropdown (Select)
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')

            # Si es un Archivo (Imagen, Ficha)
            elif isinstance(field.widget, (forms.ClearableFileInput, forms.FileInput)):
                field.widget.attrs.setdefault('class', 'form-control')
            
            # Para todos los demás (text, number, etc.)
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
        
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        # Esta expresión regular busca cualquier cosa que NO sea una letra (a-z, A-Z) o un espacio
        if re.search(r'[^a-zA-Z\s]', nombre):
            raise ValidationError("El nombre solo puede contener letras y espacios.")
        return nombre

# --- Formulario de Proveedor ---
class ProveedorForm(forms.ModelForm):
    
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
        self.fields['email'].required = True
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


# --- NUEVO FORMULARIO PARA BODEGAS ---
class BodegaForm(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = ['nombre', 'ubicacion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['ubicacion'].widget.attrs.update({'class': 'form-control'})            

class MovimientoForm(forms.ModelForm):
    
    # ... (producto y proveedor igual que antes) ...
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
    
    # --- CAMBIO: Bodega ahora es un Dropdown ---
    bodega = forms.ModelChoiceField(
        queryset=Bodega.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Bodega"
    )

    class Meta:
        model = MovimientoInventario
        fields = [
            'producto', 'tipo', 'cantidad', 
            'proveedor', 'bodega', 'doc_ref',
            'lote', 'serie', 'fecha_vencimiento', 'observaciones', 'motivo', 'fecha'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                 field.widget.attrs.setdefault('class', 'form-control')
            
            if field_name in ['proveedor', 'doc_ref', 'lote', 'serie', 'fecha_vencimiento', 'observaciones', 'motivo']:
                field.required = False
            
            if field_name == 'fecha_vencimiento':
                field.widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
            
            if field_name == 'fecha':
                field.widget = forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
                field.initial = timezone.now().strftime('%Y-%m-%dT%H:%M')
    
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