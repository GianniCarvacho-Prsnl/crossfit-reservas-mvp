"""
Scheduled Reservation Manager - Orquestador principal para reservas programadas

Este módulo implementa el orquestador principal que coordina todo el flujo
de reserva programada desde la recepción del request hasta la ejecución final.

Flujo simplificado:
1. Validar request y calcular tiempos
2. Espera directa hasta preparación (T-1 min)
3. Ejecutar preparación web (60 segundos)
4. Espera directa hasta ejecución (T+1 ms)
5. Click inmediato y respuesta final
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any
from loguru import logger

from ..models.reserva import (
    ReservaProgramadaRequest,
    ReservaProgramadaResponse,
    EstadoReservaProgramada
)
from .direct_timing_controller import DirectTimingController
from .preparation_service import PreparationService


class ScheduledReservationManager:
    """
    ORQUESTADOR PRINCIPAL - Flujo lineal sin ciclos complejos
    
    Coordina todo el proceso de reserva programada:
    - Cálculo de tiempos exactos
    - Esperas precisas con asyncio
    - Preparación web hasta botón de reserva
    - Ejecución inmediata del click
    """
    
    def __init__(self):
        self.timing_controller = DirectTimingController()
        self.preparation_service = PreparationService()
    
    async def execute_scheduled_reservation(self, request: ReservaProgramadaRequest) -> ReservaProgramadaResponse:
        """
        FLUJO PRINCIPAL - Máxima simplicidad para MVP
        
        Args:
            request: Datos de la reserva programada
            
        Returns:
            ReservaProgramadaResponse: Resultado de la operación
        """
        reservation_id = str(uuid.uuid4())
        logger.info(f"🎯 Iniciando reserva programada: {reservation_id}")
        logger.info(f"📅 Clase: {request.nombre_clase}")
        logger.info(f"⏰ Ejecución programada: {request.fecha_reserva} {request.hora_reserva}")
        
        try:
            # 1. CALCULAR tiempos exactos (sin ciclos)
            timing = self.timing_controller.calculate_execution_times(
                request.fecha_reserva, 
                request.hora_reserva
            )
            
            if not timing["is_valid"]:
                return self._create_error_response(
                    reservation_id, 
                    request,
                    "TOO_LATE", 
                    "La hora de reserva ya pasó"
                )
            
            logger.info(f"⏳ Tiempo hasta preparación: {timing['wait_until_prep_seconds']:.1f} segundos")
            logger.info(f"⏰ Tiempo hasta ejecución: {timing['wait_until_exec_seconds']:.1f} segundos")
            
            # 2. Crear respuesta inicial (se devuelve inmediatamente)
            response = self._create_initial_response(reservation_id, request, timing)
            
            # 3. ESPERA DIRECTA hasta momento de preparación
            logger.info(f"😴 Durmiendo hasta preparación: {timing['preparation_datetime']}")
            await self.timing_controller.sleep_until(timing["preparation_datetime"])
            
            # 4. PREPARACIÓN (60 segundos exactos)
            logger.info("🔧 Iniciando preparación web...")
            prep_result = await self._prepare_web_navigation(request)
            
            if not prep_result["success"]:
                logger.error(f"❌ Preparación falló: {prep_result['message']}")
                return self._create_error_response(
                    reservation_id,
                    request,
                    "PREPARATION_FAILED", 
                    prep_result["message"]
                )
            
            # 5. ESPERA DIRECTA hasta momento exacto
            logger.info(f"😴 Durmiendo hasta ejecución: {timing['execution_datetime']}")
            await self.timing_controller.sleep_until(timing["execution_datetime"])
            
            # 6. EJECUCIÓN INMEDIATA (milisegundos)
            execution_moment = datetime.now()
            target_time = timing["execution_datetime"]
            timing_difference = (execution_moment - target_time).total_seconds()
            
            logger.info(f"⚡ EJECUTANDO CLICK EN: {execution_moment.strftime('%H:%M:%S.%f')[:-3]}")
            logger.info(f"🎯 Objetivo era: {target_time.strftime('%H:%M:%S.%f')[:-3]}")
            logger.info(f"📊 Diferencia: {timing_difference:+.3f} segundos")
            
            exec_result = await self._execute_immediate_click(prep_result)
            
            # 7. CLEANUP MANUAL (siempre al final)
            try:
                await self.preparation_service._cleanup_browser()
                logger.info("🧹 Cleanup manual completado")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Error en cleanup manual: {str(cleanup_error)}")
            
            if exec_result["success"]:
                logger.success("✅ Reserva programada exitosa!")
                return self._create_success_response(reservation_id, request, exec_result)
            else:
                logger.error(f"❌ Ejecución falló: {exec_result['message']}")
                return self._create_error_response(
                    reservation_id,
                    request,
                    "EXECUTION_FAILED",
                    exec_result["message"]
                )
                
        except Exception as e:
            logger.error(f"💥 Error inesperado en reserva programada: {str(e)}")
            
            # Cleanup de emergencia en caso de excepción
            try:
                await self.preparation_service._cleanup_browser()
                logger.info("🧹 Cleanup de emergencia completado")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Error en cleanup de emergencia: {str(cleanup_error)}")
            
            return self._create_error_response(
                reservation_id,
                request,
                "UNEXPECTED_ERROR", 
                f"Error inesperado: {str(e)}"
            )
    
    async def _prepare_web_navigation(self, request: ReservaProgramadaRequest) -> Dict[str, Any]:
        """
        Preparación completa de navegación web usando PreparationService
        """
        try:
            result = await self.preparation_service.prepare_reservation(
                nombre_clase=request.nombre_clase,
                fecha_clase=request.fecha_clase
            )
            
            if result["success"]:
                logger.info("✅ Preparación web completada exitosamente")
                return result
            else:
                logger.warning(f"⚠️ Preparación con problemas: {result['message']}")
                return result
                
        except Exception as e:
            logger.error(f"💥 Error en preparación web: {str(e)}")
            return {
                "success": False,
                "message": f"Error en preparación: {str(e)}",
                "page_context": None
            }
    
    async def _execute_immediate_click(self, prep_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el click inmediato en el botón de reserva
        """
        try:
            if not prep_result.get("success"):
                return {
                    "success": False,
                    "message": "Preparación no fue exitosa"
                }
            
            # El PreparationService ya tiene el contexto interno
            result = await self.preparation_service.execute_final_click()
            
            return result
            
        except Exception as e:
            logger.error(f"💥 Error en ejecución final: {str(e)}")
            return {
                "success": False,
                "message": f"Error en ejecución: {str(e)}"
            }
    
    def _create_initial_response(
        self, 
        reservation_id: str, 
        request: ReservaProgramadaRequest, 
        timing: Dict[str, Any]
    ) -> ReservaProgramadaResponse:
        """Crea la respuesta inicial que se devuelve inmediatamente"""
        return ReservaProgramadaResponse(
            id=reservation_id,
            clase_nombre=request.nombre_clase,
            fecha_clase=request.fecha_clase,
            fecha_reserva=request.fecha_reserva,
            hora_reserva=request.hora_reserva,
            estado=EstadoReservaProgramada.PROGRAMADA,
            fecha_creacion=datetime.now(),
            fecha_ejecucion_programada=timing["execution_datetime"],
            fecha_ejecucion_real=None,
            mensaje=f"Reserva programada exitosamente. Ejecución en {timing['wait_until_exec_seconds']:.0f} segundos.",
            tiempo_espera_segundos=int(timing["wait_until_exec_seconds"]),
            error_type=None
        )
    
    def _create_success_response(
        self,
        reservation_id: str,
        request: ReservaProgramadaRequest,
        exec_result: Dict[str, Any]
    ) -> ReservaProgramadaResponse:
        """Crea respuesta de éxito"""
        return ReservaProgramadaResponse(
            id=reservation_id,
            clase_nombre=request.nombre_clase,
            fecha_clase=request.fecha_clase,
            fecha_reserva=request.fecha_reserva,
            hora_reserva=request.hora_reserva,
            estado=EstadoReservaProgramada.EXITOSA,
            fecha_creacion=datetime.now(),
            fecha_ejecucion_programada=datetime.now(),
            fecha_ejecucion_real=datetime.now(),
            mensaje=exec_result.get("message", "Reserva ejecutada exitosamente"),
            tiempo_espera_segundos=0,
            error_type=None
        )
    
    def _create_error_response(
        self,
        reservation_id: str,
        request: ReservaProgramadaRequest,
        error_type: str,
        message: str
    ) -> ReservaProgramadaResponse:
        """Crea respuesta de error"""
        return ReservaProgramadaResponse(
            id=reservation_id,
            clase_nombre=request.nombre_clase,
            fecha_clase=request.fecha_clase,
            fecha_reserva=request.fecha_reserva,
            hora_reserva=request.hora_reserva,
            estado=EstadoReservaProgramada.FALLIDA,
            fecha_creacion=datetime.now(),
            fecha_ejecucion_programada=datetime.now(),
            fecha_ejecucion_real=None,
            mensaje=message,
            tiempo_espera_segundos=0,
            error_type=error_type
        )
