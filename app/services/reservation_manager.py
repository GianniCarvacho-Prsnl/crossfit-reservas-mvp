import uuid
from datetime import datetime
from typing import Dict, Any
from loguru import logger

from app.models import ClaseConfig, EstadoReserva, ReservaResponse
from app.services.config_manager import ConfigManager
from app.services.web_automation import WebAutomationService


class ReservationManager:
    """
    Gestor principal de reservas que orquesta todo el proceso
    """
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.web_automation = WebAutomationService()
    
    async def execute_immediate_reservation(self, nombre_clase: str, fecha: str) -> ReservaResponse:
        """
        Ejecuta una reserva inmediata para una clase específica identificada por su nombre
        
        Args:
            nombre_clase: Nombre exacto de la clase como aparece en el sitio web
            fecha: Fecha en formato "XX ##" (ej: "JU 17", "VI 18")
                         Ejemplo: '17:00 CrossFit 17:00-18:00'
            
        Returns:
            ReservaResponse con el resultado
        """
        reservation_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        logger.info(f"🎯 Iniciando reserva inmediata para clase: '{nombre_clase}'")
        
        try:
            # 1. Buscar la clase por nombre en la configuración
            clase_config = self.config_manager.get_clase_by_nombre(nombre_clase)
            if not clase_config:
                logger.warning(f"⚠️ Clase no encontrada en configuración: '{nombre_clase}' - Continuando con reserva directa")
            else:
                logger.info(f"📋 Clase encontrada en configuración: {clase_config.nombre}")
            
            # 2. Validar credenciales
            if not self.web_automation.validate_credentials():
                logger.error("❌ Credenciales no configuradas correctamente")
                return ReservaResponse(
                    id=reservation_id,
                    clase_nombre=nombre_clase,
                    estado=EstadoReserva.FALLIDA,
                    fecha_ejecucion=timestamp,
                    mensaje="Credenciales no configuradas"
                )
            
            # 3. Ejecutar la automatización web directamente con el nombre y fecha
            logger.info(f"🤖 Iniciando automatización web para: '{nombre_clase}' en fecha: '{fecha}'")
            result = await self.web_automation.realizar_reserva(nombre_clase, fecha)
            
            # 4. Procesar resultado
            if result["success"]:
                logger.success(f"🎉 ¡Reserva exitosa! - {nombre_clase}")
                return ReservaResponse(
                    id=reservation_id,
                    clase_nombre=nombre_clase,
                    estado=EstadoReserva.EXITOSA,
                    fecha_ejecucion=timestamp,
                    mensaje=result["message"]
                )
            else:
                logger.error(f"💥 Fallo en la reserva: {result['message']}")
                return ReservaResponse(
                    id=reservation_id,
                    clase_nombre=nombre_clase,
                    estado=EstadoReserva.FALLIDA,
                    fecha_ejecucion=timestamp,
                    mensaje=result["message"]
                )
                
        except Exception as e:
            logger.error(f"🚨 Error inesperado en reserva: {str(e)}")
            return ReservaResponse(
                id=reservation_id,
                clase_nombre=nombre_clase,
                estado=EstadoReserva.FALLIDA,
                fecha_ejecucion=timestamp,
                mensaje=f"Error inesperado: {str(e)}"
            )
    
    def get_available_classes(self):
        """Obtiene todas las clases disponibles"""
        return self.config_manager.get_clases_activas()
