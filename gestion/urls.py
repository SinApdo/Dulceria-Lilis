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
    path('productos/exportar/', views.exportar_productos_excel, name='exportar_productos_excel'),

    # CRUD de Proveedores
    path('proveedores/', views.proveedor_list, name='proveedor_list'),
    path('proveedores/editar/<str:rut_nif>/', views.proveedor_update, name='proveedor_update'),
    path('proveedores/eliminar/<str:rut_nif>/', views.proveedor_delete, name='proveedor_delete'),
    path('proveedores/exportar/', views.exportar_proveedores_excel, name='exportar_proveedores_excel'),

    # Inventario
    path('inventario/', views.inventario_list, name='inventario_list'),
    path('inventario/exportar/', views.exportar_inventario_excel, name='exportar_inventario_excel'),
    
    # CRUD de Usuarios
    path('usuarios/', views.user_list, name='user_list'),
    path('usuarios/editar/<int:pk>/', views.user_update, name='user_update'),
    path('usuarios/eliminar/<int:pk>/', views.user_delete, name='user_delete'),
    path('usuarios/exportar/', views.exportar_usuarios_excel, name='exportar_usuarios_excel'),

    # CRUD de Categorías
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/editar/<int:pk>/', views.categoria_update, name='categoria_update'),
    path('categorias/eliminar/<int:pk>/', views.categoria_delete, name='categoria_delete'),
    path('categorias/exportar/', views.exportar_categorias_excel, name='exportar_categorias_excel'),

    # CRUD de Marcas
    path('marcas/', views.marca_list, name='marca_list'),
    path('marcas/editar/<int:pk>/', views.marca_update, name='marca_update'),
    path('marcas/eliminar/<int:pk>/', views.marca_delete, name='marca_delete'),
    path('marcas/exportar/', views.exportar_marcas_excel, name='exportar_marcas_excel'),

    # CRUD de Bodegas
    path('bodegas/', views.bodega_list, name='bodega_list'),
    path('bodegas/editar/<int:pk>/', views.bodega_update, name='bodega_update'),
    path('bodegas/eliminar/<int:pk>/', views.bodega_delete, name='bodega_delete'),

]