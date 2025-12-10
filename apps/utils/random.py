import random

def generar_otp():
    return f"{random.randint(100000, 999999):06d}"