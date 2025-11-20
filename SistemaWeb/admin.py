from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Orden)
admin.site.register(OrdenProducto)
admin.site.register(Producto)
admin.site.register(CategoriaProducto)
