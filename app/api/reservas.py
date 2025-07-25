from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List

from app.models import (
    ReservaInmediataRequest, 
    ReservaResponse, 
    ClaseConfig, 
    HealthResponse,
    ReservaProgramadaRequest,
    ReservaProgramadaResponse
)
from app.services.reservation_manager import ReservationManager
from app.services.scheduled_reservation_manager import ScheduledReservationManager

router = APIRouter()
reservation_manager = ReservationManager()
scheduled_reservation_manager = ScheduledReservationManager()


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
        
        # Convertir el resultado al formato esperado por ReservaResponse
        if resultado.get("success"):
            import uuid
            
            return ReservaResponse(
                id=str(uuid.uuid4()),
                nombre_clase=request.nombre_clase,
                fecha=request.fecha,
                estado="exitosa",  # Cambiado de "confirmada" a "exitosa"
                mensaje=resultado.get("message", "Reserva completada exitosamente"),
                fecha_hora_reserva=datetime.now()
            )
        else:
            import uuid
            
            return ReservaResponse(
                id=str(uuid.uuid4()),
                nombre_clase=request.nombre_clase,
                fecha=request.fecha,
                estado="fallida",  # Cambiado de "error" a "fallida"
                mensaje=resultado.get("message", "Error en la reserva"),
                fecha_hora_reserva=datetime.now()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando reserva inmediata: {str(e)}")


@router.post("/reservas/programada", response_model=ReservaProgramadaResponse)
async def reserva_programada(request: ReservaProgramadaRequest):
    """
    Programa una reserva para ejecutarse en un momento exacto.
    
    Ejemplo de uso:
    {
        "nombre_clase": "18:00 CrossFit 18:00-19:00",
        "fecha_clase": "LU 21",
        "fecha_reserva": "2025-01-19",
        "hora_reserva": "17:00:00"
    }
    """
    try:
        # Ejecutar en background y devolver respuesta inmediata
        import asyncio
        
        # Crear la tarea en background (fire and forget)
        task = asyncio.create_task(
            scheduled_reservation_manager.execute_scheduled_reservation(request)
        )
        
        # Para MVP, devolvemos respuesta inmediata
        from datetime import datetime
        import uuid
        
        return ReservaProgramadaResponse(
            id=str(uuid.uuid4()),
            clase_nombre=request.nombre_clase,
            fecha_clase=request.fecha_clase,
            fecha_reserva=request.fecha_reserva,
            hora_reserva=request.hora_reserva,
            estado="programada",
            fecha_creacion=datetime.now(),
            fecha_ejecucion_programada=datetime.now(),
            fecha_ejecucion_real=None,
            mensaje="Reserva programada iniciada correctamente. El proceso se ejecutará en background.",
            tiempo_espera_segundos=0,
            error_type=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error programando reserva: {str(e)}")


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
