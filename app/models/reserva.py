from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoReserva(str, Enum):
    EXITOSA = "exitosa"
    FALLIDA = "fallida"
    EN_PROCESO = "en_proceso"

class EstadoReservaProgramada(str, Enum):
    PROGRAMADA = "programada"           # Esperando momento de ejecución
    PREPARANDO = "preparando"           # Iniciando navegación (T-1 min)
    EJECUTANDO = "ejecutando"           # Monitoreo de precisión hasta hora exacta
    EXITOSA = "exitosa"                 # Reserva completada exitosamente
    FALLIDA = "fallida"                 # Error en cualquier fase

class ReservaInmediataRequest(BaseModel):
    nombre_clase: str
    fecha: str  # Formato: "JU 17", "VI 18", etc.

class ReservaProgramadaRequest(BaseModel):
    nombre_clase: str                    # "18:00 CrossFit 18:00-19:00"
    fecha_clase: str                     # "LU 21" (fecha de la clase)
    fecha_reserva: str                   # "2025-01-19" (fecha cuando ejecutar la reserva)
    hora_reserva: str                    # "17:00:00" (hora exacta de ejecución)
    timezone: str = "America/Santiago"   # Zona horaria
    
class ReservaResponse(BaseModel):
    id: str
    nombre_clase: str
    fecha: str
    estado: EstadoReserva
    mensaje: str
    fecha_hora_reserva: datetime
    
class ReservaProgramadaResponse(BaseModel):
    id: str
    clase_nombre: str
    fecha_clase: str
    fecha_reserva: str
    hora_reserva: str
    estado: EstadoReservaProgramada
    fecha_creacion: datetime
    fecha_ejecucion_programada: datetime
    fecha_ejecucion_real: Optional[datetime]
    mensaje: str
    tiempo_espera_segundos: int
    error_type: Optional[str] = None

class ClaseConfig(BaseModel):
    id: str
    nombre: str
    dia_semana: str
    hora_inicio: str
    hora_reserva: str
    activo: bool = True

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime

class ScheduledReservationErrors:
    """Tipos de error específicos para reservas programadas"""
    INVALID_TIMING = "INVALID_TIMING"           # Hora de reserva inválida
    TOO_LATE = "TOO_LATE"                       # Ya pasó la hora de reserva
    PREPARATION_FAILED = "PREPARATION_FAILED"   # Fallo en preparación
    TIMING_DRIFT = "TIMING_DRIFT"               # Deriva temporal detectada
    SESSION_EXPIRED = "SESSION_EXPIRED"         # Sesión web expiró
    NETWORK_INTERRUPTED = "NETWORK_INTERRUPTED" # Conectividad perdida
    EXECUTION_MISSED = "EXECUTION_MISSED"       # No se pudo ejecutar a tiempo
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"       # Error inesperado
