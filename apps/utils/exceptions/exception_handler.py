from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Obtener la respuesta estándar de DRF
    response = exception_handler(exc, context)

    # Si es un error 500 o no manejado por DRF
    if response is None:
        return Response(
            {
                'code': 'ServerError',
                'message': 'Error interno del servidor.',
                'detail': str(exc)  # Idealmente solo en DEBUG
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 1. Intentamos obtener el 'code' específico que tú definiste
    #    En `ValidationError`, el código está en `exc.detail['code']`
    #    si se lanzó desde la vista.
    #    En otras APIException, está en `exc.default_code`.

    code = 'error'  # Valor por defecto

    if isinstance(exc, APIException):
        # Usamos el .default_code (ej. 'invalid', 'not_found', etc.)
        if isinstance(exc.detail, dict):
            for field_errors in exc.detail.values():
                first_error = field_errors[0]
                if hasattr(first_error, 'code'):
                    code = first_error.code
                    break
        else:
            code = exc.default_code

        # Si tiene un 'code' personalizado en su detalle, lo usamos
        if isinstance(exc.detail, dict) and exc.detail.get('code'):
            code = exc.detail.pop('code')  # Lo usamos Y lo quitamos del detalle


    # Vamos a confiar en la respuesta de DRF
    if 'code' in response.data:
        code = response.data['code']

    # El `detail` de la respuesta de DRF (ej. {"curp": [...]})
    detail = response.data.get('detail', response.data)

    # Limpiamos el 'detail' si es un dict que solo contiene el 'code'
    if isinstance(detail, dict) and 'code' in detail:
        detail.pop('code', None)  # Quita el 'code' duplicado del detalle

    # Re-formateamos la respuesta final
    custom_data = {
        'code': code,  # <-- Aquí irá tu 'required'
        'message': 'Ha ocurrido un error.',  # Mensaje genérico
        'detail': detail
    }

    response.data = custom_data
    return response