from rest_framework import routers
from django.urls import path
from .views.programas import ProgramasListView, ProgramaViewSet

router = routers.DefaultRouter()
router.register(r'admin', ProgramaViewSet)

urlpatterns = [
    path('', ProgramasListView.as_view(), name='localidades-list'),
] + router.urls