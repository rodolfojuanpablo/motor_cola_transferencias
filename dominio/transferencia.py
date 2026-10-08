"""Modelo de datos de una transferencia y de los eventos del historial."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Estado(Enum):
    PENDIENTE = "Pendiente"
    EN_REINTENTO = "En reintento"
    PROCESADA = "Procesada"
    RECHAZADA = "Rechazada (notificada)"
    REVERTIDA = "Revertida"


CANALES = ("App móvil", "Banca por internet", "Plin", "Agente")


@dataclass
class Transferencia:
    id: int
    origen: str          # cuenta de 13 dígitos
    destino: str
    monto: float         # soles
    canal: str
    llegada: datetime = field(default_factory=datetime.now)
    estado: Estado = Estado.PENDIENTE
    intentos: int = 0
    motivo: str = ""


@dataclass
class Evento:
    """Registro inmutable que se guarda en la lista doble del historial."""
    hora: datetime
    id_transferencia: int
    tipo: str
    monto: float
    detalle: str
