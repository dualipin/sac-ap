from django.conf import settings

OTP_TTL_SECONDS = getattr(settings, "OTP_TTL_SECONDS", 300)

OTP_TTL = 300