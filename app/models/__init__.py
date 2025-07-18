# Importar todos los modelos desde reserva.py
from .reserva import (
    EstadoReserva,
    ReservaInmediataRequest,
    ReservaResponse,
    ClaseConfig,
    HealthResponse
)

# Exportar para facilitar las importaciones
__all__ = [
    "EstadoReserva",
    "ReservaInmediataRequest", 
    "ReservaResponse",
    "ClaseConfig",
    "HealthResponse"
]
