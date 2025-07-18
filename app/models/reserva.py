from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoReserva(str, Enum):
    EXITOSA = "exitosa"
    FALLIDA = "fallida"
    EN_PROCESO = "en_proceso"

class ReservaInmediataRequest(BaseModel):
    nombre_clase: str
    fecha: str  # Formato: "JU 17", "VI 18", etc.
    
class ReservaResponse(BaseModel):
    id: str
    clase_nombre: str
    estado: EstadoReserva
    fecha_ejecucion: datetime
    mensaje: str

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
