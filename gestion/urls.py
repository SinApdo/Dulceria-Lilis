# En: gestion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Inicio
    path('', views.inicio_gestion, name='inicio_gestion'),
    
    # CRUD de Productos
    path('productos/', views.producto_list, name='producto_list'),    
    path('productos/editar/<str:sku>/', views.producto_update, name='producto_update'),
    path('productos/eliminar/<str:sku>/', views.producto_delete, name='producto_delete'),
    
    # CRUD de Proveedores
    path('proveedores/', views.proveedor_list, name='proveedor_list'),
    path('proveedores/editar/<str:rut_nif>/', views.proveedor_update, name='proveedor_update'),
    path('proveedores/eliminar/<str:rut_nif>/', views.proveedor_delete, name='proveedor_delete'),

    # Inventario
    path('inventario/', views.inventario_list, name='inventario_list'),
    
    # CRUD de Usuarios
    path('usuarios/', views.user_list, name='user_list'),
    path('usuarios/editar/<int:pk>/', views.user_update, name='user_update'),
    path('usuarios/eliminar/<int:pk>/', views.user_delete, name='user_delete'),

    # CRUD de Categorías
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/editar/<int:pk>/', views.categoria_update, name='categoria_update'),
    path('categorias/eliminar/<int:pk>/', views.categoria_delete, name='categoria_delete'),

    # CRUD de Marcas
    path('marcas/', views.marca_list, name='marca_list'),
    path('marcas/editar/<int:pk>/', views.marca_update, name='marca_update'),
    path('marcas/eliminar/<int:pk>/', views.marca_delete, name='marca_delete'),
]