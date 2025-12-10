from django.urls import path
from .views.localidades import LocalidadApiView

urlpatterns = [
    path('', LocalidadApiView.as_view(), name='localidades-list'),
]