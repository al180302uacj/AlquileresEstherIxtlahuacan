from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name = 'home'),
    path('crearcuenta/', views.SignUp, name = 'signup'),
    path('iniciosesion/', views.LogIn, name = 'login'),
    path('cerrarsesion/', views.LogOut, name = 'logout'),
    path('contacto/', views.Contact, name = 'contact'),
    path('productos/', views.Products, name = 'products'),
    path('añadirproducto/', views.AddProduct, name = 'addproduct'),
    path('editarproducto/<int:producto_id>/', views.EditProduct, name = 'editproduct'),
    path('eliminarproducto/<int:producto_id>/', views.DeleteProduct, name = 'deleteproduct'),
    path('micuenta/', views.Account, name = 'account'),
    path('administracion/', views.Admin, name = 'admin'),
    path('rentar/', views.Rent, name = 'rent'),
    path('actualizarrenta/', views.UpdateOrder, name = 'updateorder'),
    path('procesarrenta/', views.ProcessRent, name = 'processrent'),
    path('actualizarestatus/<int:orden_id>/', views.UpdateStatus, name = 'updatestatus'),
    path('generarreporte/', views.GenerateReport, name = 'generatereport')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)