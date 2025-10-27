from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria

def inicio(request):
    productos = Producto.objects.all()

    return render(request, 'catalogo/inicio.html', {'productos': productos})

def acercade(request):

    return render(request, 'catalogo/acercade.html')

def producto(request, producto_id):
    producto_obj = get_object_or_404(Producto, id=producto_id)

    return render(request, 'catalogo/producto.html', {'producto': producto_obj})

def categoria(request, nombre_categoria):
    categoria_obj = get_object_or_404(Categoria, nombre=nombre_categoria)
    productos = Producto.objects.filter(categoria=categoria_obj)

    return render(request, 'catalogo/categoria.html', {
        'categoria': categoria_obj,
        'productos': productos
    })