# Importar todos los modelos desde reserva.py
from .reserva import (
    EstadoReserva,
    EstadoReservaProgramada,
    ReservaInmediataRequest,
    ReservaProgramadaRequest,
    ReservaResponse,
    ReservaProgramadaResponse,
    ClaseConfig,
    HealthResponse
)

# Exportar para facilitar las importaciones
__all__ = [
    "EstadoReserva",
    "EstadoReservaProgramada",
    "ReservaInmediataRequest",
    "ReservaProgramadaRequest", 
    "ReservaResponse",
    "ReservaProgramadaResponse",
    "ClaseConfig",
    "HealthResponse"
]
