def validar_curp(curp: str) -> bool:
    """
    Valida si una CURP (Clave Única de Registro de Población) es válida según su formato.

    Args:
        curp (str): La CURP a validar.

    Returns:
        bool: True si la CURP es válida, False en caso contrario.
    """
    import re

    # Expresión regular para validar el formato de la CURP
    patron_curp = re.compile(
        r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$'
    )

    return bool(patron_curp.match(curp))
