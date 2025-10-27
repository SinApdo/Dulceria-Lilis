from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('acercade/', views.acercade, name='acercade'),

    path('producto/<int:producto_id>/', views.producto, name='producto'),

    path('categoria/<str:nombre_categoria>/', views.categoria, name='categoria'),
]