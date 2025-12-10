from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.autenticacion.serializers import CustomTokenObtainPairSerializer


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Credenciales inválidas"}, status=401)

        tokens = serializer.validated_data
        access = tokens["access"]
        refresh = tokens["refresh"]

        response = Response({"access": access, "refresh": refresh}, status=200)

        response.set_cookie(
            key="refresh",
            value=refresh,
            httponly=True,
            secure=False,  # settings.DEBUG,
            samesite=(
                "Strict" if not hasattr(settings, "DEBUG") or settings.DEBUG else "None"
            ),
            path="/api/v1/token/refresh/",
        )

        return response


class RefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        # Intentar obtener el refresh token de la cookie primero, luego del body
        refresh = request.COOKIES.get("refresh") or request.data.get("refresh")

        if refresh is None:
            return Response(
                {"detail": "No hay token de refresco en las cookies o en el body"},
                status=401,
            )

        serializer = self.get_serializer(data={"refresh": refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Token de refresco inválido"}, status=401)

        access = serializer.validated_data["access"]
        response = Response({"access": access}, status=200)

        # Actualizar la cookie también
        response.set_cookie(
            key="refresh",
            value=refresh,
            httponly=True,
            secure=False,  # settings.DEBUG,
            samesite=(
                "Strict" if not hasattr(settings, "DEBUG") or settings.DEBUG else "None"
            ),
            path="/api/v1/token/refresh/",
        )

        return response
