# En: gestion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Inicio
    path('', views.inicio_gestion, name='inicio_gestion'),
    
    # CRUD de Productos
    path('productos/', views.producto_list, name='producto_list'),
    
    # --- BORRA ESTA LÍNEA QUE DA EL ERROR ---
    # path('productos/crear/', views.producto_create, name='producto_create'), 
    
    path('productos/editar/<str:sku>/', views.producto_update, name='producto_update'),
    path('productos/eliminar/<str:sku>/', views.producto_delete, name='producto_delete'),
    
    # CRUD de Proveedores
    path('proveedores/', views.proveedor_list, name='proveedor_list'),
    path('proveedores/editar/<str:rut_nif>/', views.proveedor_update, name='proveedor_update'),
    path('proveedores/eliminar/<str:rut_nif>/', views.proveedor_delete, name='proveedor_delete'),
    
    # Inventario
    path('inventario/', views.inventario_list, name='inventario_list'),
]