from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views.autenticacion import LoginView, RefreshView

urlpatterns = [
    # ...
    path('blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', RefreshView.as_view(), name='token_refresh'),
]
