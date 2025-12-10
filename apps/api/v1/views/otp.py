from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from apps.cuentas.models.ciudadano import Ciudadano
from apps.cuentas.models.cuenta import Cuenta
from apps.cuentas.services.otp_service import generar_enviar_otp, verificar_opt
from rest_framework.authtoken.models import Token
from apps.utils.hashing import indexed_hash


class OTPRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        curp = request.data.get("curp")
        if not email or not curp:
            return Response({"detail": "email y curp requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        # ensure Ciudadano exists or create minimal
        ciudad = Ciudadano.objects.filter(curp_hash=indexed_hash(str(curp).strip().upper())).first()
        if not ciudad:
            # create quickly
            ciudad = Ciudadano(curp=curp)
            ciudad.save()

        # ensure Cuenta exists
        cuenta, _ = Cuenta.objects.get_or_create(email=email.lower(), defaults={"ciudadano": ciudad})
        # generate OTP
        otp = generar_enviar_otp(correo=cuenta.email, cuenta=cuenta)
        return Response({"detail": "OTP enviado (revisa logs si ambiente dev)"})


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        if not email or not code:
            return Response({"detail": "email y code requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        otp = verificar_opt(correo=email, code=code)
        if not otp:
            return Response({"detail": "OTP inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure cuenta exists
        cuenta = otp.cuenta or Cuenta.objects.filter(email=email.lower()).first()
        if not cuenta:
            return Response({"detail": "Cuenta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # create or return token
        token, _ = Token.objects.get_or_create(user=cuenta)
        return Response({"token": token.key})
