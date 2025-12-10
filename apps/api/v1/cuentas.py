from django.urls import path
from .views.ciudadanos import CiudadanoCreateView
from .views.dependencias import DependenciaListCreate
from .views.funcionarios import FuncionarioListCreate
from .views.otp import OTPRequestView, OTPVerifyView

urlpatterns = [
    path('ciudadanos/', CiudadanoCreateView.as_view(), name='ciudadanos-create'),
    path('otp/request/', OTPRequestView.as_view(), name='otp-request'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    path('dependencias/', DependenciaListCreate.as_view(), name='dependencias-list-create'),
    path('funcionarios/', FuncionarioListCreate.as_view(), name='funcionarios-list-create'),
]
