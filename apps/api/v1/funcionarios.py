from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.api.v1.views.funcionarios import FuncionarioViewSet

router = DefaultRouter()
router.register(r"", FuncionarioViewSet, basename="funcionarios")

urlpatterns = router.urls
