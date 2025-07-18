from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List

from app.models import ReservaInmediataRequest, ReservaResponse, ClaseConfig, HealthResponse
from app.services.reservation_manager import ReservationManager

router = APIRouter()
reservation_manager = ReservationManager()


@router.post("/reservas/inmediata", response_model=ReservaResponse)
async def reserva_inmediata(request: ReservaInmediataRequest):
    """
    Ejecuta una reserva inmediata para la clase especificada por nombre y fecha.
    Recibe el nombre de la clase y la fecha en formato "XX ##".
    Ejemplo: nombre_clase='17:00 CrossFit 17:00-18:00', fecha='JU 17'
    """
    try:
        resultado = await reservation_manager.execute_immediate_reservation(
            nombre_clase=request.nombre_clase,
            fecha=request.fecha
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando reserva inmediata: {str(e)}")


@router.get("/clases", response_model=List[ClaseConfig])
async def listar_clases():
    """
    Lista todas las clases disponibles y activas
    """
    try:
        clases = reservation_manager.get_available_classes()
        return clases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo clases: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check del servicio
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now()
    )
