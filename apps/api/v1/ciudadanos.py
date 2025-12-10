from django.urls import path
from .views.ciudadanos import RegistrarCiudadanoCreateView, VerificarCiudadanoRegistradoView

urlpatterns = [
    path('registrar/', RegistrarCiudadanoCreateView.as_view(), name='registrar-ciudadano'),
    path('verificar/<str:curp>', VerificarCiudadanoRegistradoView.as_view(), name='verificar-ciudadano'),
]
