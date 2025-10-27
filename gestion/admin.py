from django.contrib import admin
from .models import Cliente, Pedido

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')
    search_fields = ('nombre', 'email')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_pedido', 'estado')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('cliente__nombre', 'id')
    date_hierarchy = 'fecha_pedido'

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Pedido, PedidoAdmin)
# Register your models here.
