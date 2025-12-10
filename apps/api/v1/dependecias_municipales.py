from rest_framework import routers
from .views.dependecias_municipales import DependenciaMunicipalViewSet

router = routers.DefaultRouter()
router.register(r'', DependenciaMunicipalViewSet)

urlpatterns = router.urls
