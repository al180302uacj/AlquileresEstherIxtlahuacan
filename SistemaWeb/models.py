from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuario(AbstractUser):
    is_admin = models.BooleanField(default = False)
    direccion = models.TextField(blank = True, null = True)
    telefono = models.CharField(max_length = 15, blank = True, null = True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Categorias(models.TextChoices):
    SILLAS = 'Sillas', 'Sillas'
    MESAS = 'Mesas', 'Mesas'
    MANTELES = 'Manteles', 'Manteles'
    OTROS = 'Otros', 'Otros'  

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length = 100, choices = Categorias.choices, default = Categorias.SILLAS)

    def __str__(self):
        return f"{self.nombre}"
    
    
class Producto(models.Model):
    imagen = models.URLField("Imagen (URL)", blank=True, null=True)
    nombre = models.CharField(max_length = 100)
    descripcion = models.TextField(blank = True, null = True)
    precio_renta = models.DecimalField(max_digits = 10, decimal_places = 2)
    stock = models.PositiveIntegerField(default = 0)
    categoria = models.ForeignKey(CategoriaProducto, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.nombre}"
    
    @property
    def imagenURL(self):
        if self.imagen and hasattr(self.imagen, 'url'):
            return self.imagen.url
        return ''
    
class Estados(models.TextChoices):
    PENDIENTE =  'Pendiente', 'Pendiente'
    COMPLETADO = 'Completado', 'Completado'
    CANCELADO = 'Cancelado', 'Cancelado'

class Orden(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    fecha_orden = models.DateField(auto_now_add = True, null = True)
    direccion_envio = models.TextField(blank = True, null = True)
    fecha_evento = models.DateTimeField(blank = True, null = True)
    total = models.DecimalField(max_digits = 10, decimal_places = 2, null = True)
    completado = models.BooleanField(default = False)
    estado = models.CharField(max_length = 20, choices = Estados.choices, default = Estados.PENDIENTE)

    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    telefono_cliente = models.CharField(max_length=15, blank=True, null=True)

    @property
    def total_select(self):
        productos = self.ordenproducto_set.all()
        total = sum([item.subtotal for item in productos])
        return total

    def __str__(self):
        return f"Orden {self.id} de {self.usuario} - {self.get_estado_display()} ({self.completado})"
    

class OrdenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete = models.CASCADE)
    orden = models.ForeignKey(Orden, on_delete = models.CASCADE)
    cantidad = models.IntegerField(default = 0, blank = True, null = True)
    fecha_creacion = models.DateField(auto_now_add = True, null = True)

    @property
    def subtotal(self):
        sub_total = self.producto.precio_renta * self.cantidad
        return sub_total

    def __str__(self):
        return f"Orden de {self.orden.usuario.first_name} - {self.cantidad} {self.producto.nombre}"
