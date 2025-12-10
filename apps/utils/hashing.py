import hashlib
from datetime import datetime, date


def indexed_hash(value: str) -> str:
    """
    Genera un hash SHA-256 del valor dado para indexación segura.
    """
    return hashlib.sha256(value.encode()).hexdigest()


def serialize_date(d):
    """
    Serializa un objeto datetime o date a un string ISO 8601.
    """
    if not isinstance(d, (datetime, date)):
        raise TypeError("serialize_date solo acepta datetime o date")
    return d.isoformat()


def deserialize_date(s):
    """
    Deserializa un string ISO 8601 a un objeto date.
    """
    if not isinstance(s, str):
        raise TypeError("deserialize_date requiere un ISO string")
    try:
        # date.fromisoformat acepta 'YYYY-MM-DD' ; se puede ampliar para datetime si se quiere
        return date.fromisoformat(s)
    except Exception as exc:
        raise ValueError(f"deserialize_date recibió un ISO string inválido: {s}") from exc
