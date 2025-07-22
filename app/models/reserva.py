from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoReserva(str, Enum):
    EXITOSA = "exitosa"
    FALLIDA = "fallida"
    EN_PROCESO = "en_proceso"

class EstadoReservaProgramada(str, Enum):
    PROGRAMADA = "programada"
    EJECUTANDO = "ejecutando"
    EXITOSA = "exitosa"
    FALLIDA = "fallida"

class ReservaInmediataRequest(BaseModel):
    nombre_clase: str
    fecha: str  # Formato: "JU 17", "VI 18", etc.

class ReservaProgramadaRequest(BaseModel):
    nombre_clase: str
    fecha: str  # Formato: "JU 17", "VI 18", etc.
    hora_reserva: str  # Formato: "18:27:00"
    
class ReservaResponse(BaseModel):
    id: str
    clase_nombre: str
    estado: EstadoReserva
    fecha_ejecucion: datetime
    mensaje: str
    error_type: Optional[str] = None  # "NO_CUPOS", "LOGIN_FAILED", "NETWORK_ERROR", etc.

class ReservaProgramadaResponse(BaseModel):
    id: str
    clase_nombre: str
    fecha: str
    hora_reserva: str
    estado: EstadoReservaProgramada
    fecha_programada: datetime
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
