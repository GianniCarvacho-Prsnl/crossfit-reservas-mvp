"""
Direct Timing Controller - Control de temporización simplificado sin ciclos

Este módulo implementa el control de tiempo SIMPLIFICADO para reservas programadas.
Utiliza cálculo directo sin ciclos complejos, maximizando la precisión temporal.

Características principales:
- Cálculo directo de tiempos de preparación y ejecución
- asyncio.sleep() para máxima precisión
- Manejo de zona horaria Chile/Santiago
- Validaciones de seguridad temporal
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import pytz
import logging

logger = logging.getLogger(__name__)


class DirectTimingController:
    """
    Control de tiempo SIMPLIFICADO - Sin ciclos, solo cálculo directo
    
    Este controlador maneja toda la lógica de temporización para reservas programadas:
    - Calcula momentos críticos (preparación y ejecución)
    - Ejecuta esperas precisas con asyncio
    - Valida fechas y horas futuras
    - Maneja zona horaria de Chile
    """
    
    def __init__(self):
        """Inicializa el controlador con configuración de Chile/Santiago"""
        self.timezone = pytz.timezone("America/Santiago")
        logger.info("🕐 DirectTimingController inicializado con timezone: America/Santiago")
    
    def calculate_execution_times(
        self, 
        fecha_reserva_str: str, 
        hora_reserva_str: str
    ) -> Dict[str, Any]:
        """
        Calcula los dos momentos críticos de ejecución: preparación y ejecución final
        
        Args:
            fecha_reserva_str: Fecha en formato "YYYY-MM-DD" (ej: "2025-01-19")
            hora_reserva_str: Hora en formato "HH:MM:SS" (ej: "17:00:00")
            
        Returns:
            Dict con información de timing:
            {
                "preparation_datetime": datetime,    # Momento de preparación (T-1min)
                "execution_datetime": datetime,      # Momento de ejecución (T+1ms)
                "wait_until_prep_seconds": float,    # Segundos hasta preparación
                "wait_until_exec_seconds": float,    # Segundos hasta ejecución
                "is_valid": bool,                    # Si es ejecutable
                "target_time": datetime,             # Tiempo objetivo
                "validation_message": str            # Mensaje de validación
            }
        """
        logger.info(f"🧮 Calculando tiempos de ejecución: {fecha_reserva_str} {hora_reserva_str}")
        
        try:
            # SOLUCIÓN SIMPLE: Usar datetime naive (sin timezone) para evitar problemas
            now = datetime.now()
            
            # Crear datetime objetivo usando fecha y hora específicas
            target_date = datetime.strptime(fecha_reserva_str, "%Y-%m-%d").date()
            target_time = datetime.strptime(hora_reserva_str, "%H:%M:%S").time()
            target_datetime = datetime.combine(target_date, target_time)
            
            # Calcular momentos críticos
            # Preparación: 1 minuto antes del objetivo
            prep_datetime = target_datetime - timedelta(minutes=1)
            # Ejecución: 1 milisegundo después del objetivo (para no ejecutar antes)
            exec_datetime = target_datetime + timedelta(milliseconds=1)
            
            # Calcular segundos de espera
            wait_until_prep = (prep_datetime - now).total_seconds()
            wait_until_exec = (exec_datetime - now).total_seconds()
            
            # Log para debugging
            logger.info(f"⏰ Hora actual: {now}")
            logger.info(f"🎯 Hora objetivo: {target_datetime}")
            logger.info(f"🔧 Preparación en: {prep_datetime}")
            logger.info(f"⚡ Ejecución en: {exec_datetime}")
            logger.info(f"⏳ Segundos hasta preparación: {wait_until_prep:.1f}")
            logger.info(f"⏰ Segundos hasta ejecución: {wait_until_exec:.1f}")
            
            # Validaciones de seguridad
            is_valid = True
            validation_message = "Timing válido"
            
            if wait_until_prep <= 0:
                is_valid = False
                validation_message = f"La hora de preparación ya pasó. Objetivo: {prep_datetime}, Actual: {now}"
            elif wait_until_exec <= 0:
                is_valid = False
                validation_message = f"La hora de ejecución ya pasó. Objetivo: {target_datetime}, Actual: {now}"
            elif wait_until_prep > 24 * 3600:  # Más de 24 horas
                is_valid = False
                validation_message = f"Tiempo de espera muy largo: {wait_until_prep/3600:.1f} horas"
            
            result = {
                "preparation_datetime": prep_datetime,
                "execution_datetime": exec_datetime,
                "wait_until_prep_seconds": wait_until_prep,
                "wait_until_exec_seconds": wait_until_exec,
                "is_valid": is_valid,
                "current_time": now,
                "target_time": target_datetime,
                "validation_message": validation_message
            }
            
            logger.info(f"✅ Cálculo completado. Válido: {is_valid}, Preparación en: {wait_until_prep:.1f}s, Ejecución en: {wait_until_exec:.1f}s")
            return result
            
        except ValueError as e:
            logger.error(f"❌ Error en formato de fecha/hora: {str(e)}")
            return {
                "preparation_datetime": None,
                "execution_datetime": None,
                "wait_until_prep_seconds": -1,
                "wait_until_exec_seconds": -1,
                "is_valid": False,
                "current_time": datetime.now(self.timezone),
                "target_time": None,
                "validation_message": f"Error en formato de fecha/hora: {str(e)}"
            }
        except Exception as e:
            logger.error(f"💥 Error inesperado en cálculo de tiempos: {str(e)}")
            return {
                "preparation_datetime": None,
                "execution_datetime": None,
                "wait_until_prep_seconds": -1,
                "wait_until_exec_seconds": -1,
                "is_valid": False,
                "current_time": datetime.now(self.timezone),
                "target_time": None,
                "validation_message": f"Error inesperado: {str(e)}"
            }
    
    async def sleep_until(self, target_datetime: datetime):
        """
        Duerme hasta un momento exacto usando asyncio
        MÁXIMA PRECISIÓN - Sin ciclos ni verificaciones
        
        Args:
            target_datetime: Momento exacto hasta el cual dormir
        """
        # Usar datetime naive para evitar problemas de timezone
        now = datetime.now()
        sleep_seconds = (target_datetime - now).total_seconds()
        
        logger.info(f"😴 Durmiendo {sleep_seconds:.1f} segundos hasta {target_datetime}")
        
        if sleep_seconds > 0:
            await asyncio.sleep(sleep_seconds)
        else:
            logger.warning(f"⚠️ Tiempo objetivo ya pasó: {target_datetime} vs actual: {now}")
    
    def validate_fecha_hora(
        self, 
        fecha_reserva: str, 
        hora_reserva: str
    ) -> Dict:
        """
        Valida formato y lógica de fecha y hora
        
        Args:
            fecha_reserva: Fecha en formato "YYYY-MM-DD"
            hora_reserva: Hora en formato "HH:MM:SS"
            
        Returns:
            Dict con resultado de validación:
            {
                "is_valid": bool,
                "errors": List[str],
                "parsed_datetime": Optional[datetime],
                "message": str
            }
        """
        errors = []
        parsed_datetime = None
        
        try:
            # Validar formato de fecha
            try:
                fecha_obj = datetime.strptime(fecha_reserva, "%Y-%m-%d").date()
            except ValueError:
                errors.append(f"Formato de fecha inválido: {fecha_reserva}. Use YYYY-MM-DD")
                fecha_obj = None
            
            # Validar formato de hora
            try:
                hora_obj = datetime.strptime(hora_reserva, "%H:%M:%S").time()
            except ValueError:
                errors.append(f"Formato de hora inválido: {hora_reserva}. Use HH:MM:SS")
                hora_obj = None
            
            # Si ambos formatos son válidos, crear datetime y validar lógica
            if fecha_obj and hora_obj:
                parsed_datetime = datetime.combine(fecha_obj, hora_obj).replace(tzinfo=self.timezone)
                now = datetime.now(self.timezone)
                
                # Validar que sea fecha futura
                if parsed_datetime <= now:
                    errors.append(f"La fecha/hora debe ser futura. Especificada: {parsed_datetime}, Actual: {now}")
                
                # Validar que no sea muy lejana (más de 7 días)
                max_future = now + timedelta(days=7)
                if parsed_datetime > max_future:
                    errors.append(f"La fecha/hora no puede ser más de 7 días en el futuro. Máximo: {max_future}")
            
            is_valid = len(errors) == 0
            message = "Fecha y hora válidas" if is_valid else f"Errores encontrados: {'; '.join(errors)}"
            
            logger.info(f"📋 Validación de fecha/hora: {is_valid} - {message}")
            
            return {
                "is_valid": is_valid,
                "errors": errors,
                "parsed_datetime": parsed_datetime,
                "message": message
            }
            
        except Exception as e:
            error_msg = f"Error inesperado durante validación: {str(e)}"
            logger.error(f"💥 {error_msg}")
            return {
                "is_valid": False,
                "errors": [error_msg],
                "parsed_datetime": None,
                "message": error_msg
            }
    
    def get_timing_info(
        self, 
        fecha_reserva: str, 
        hora_reserva: str
    ) -> Dict:
        """
        Función de conveniencia que combina validación y cálculo de tiempos
        
        Args:
            fecha_reserva: Fecha en formato "YYYY-MM-DD"
            hora_reserva: Hora en formato "HH:MM:SS"
            
        Returns:
            Dict completo con validación y cálculos de tiempo
        """
        logger.info(f"📊 Obteniendo información completa de timing: {fecha_reserva} {hora_reserva}")
        
        # Primero validar formatos
        validation = self.validate_fecha_hora(fecha_reserva, hora_reserva)
        
        if not validation["is_valid"]:
            return {
                "validation": validation,
                "timing": None,
                "overall_valid": False,
                "message": f"Validación fallida: {validation['message']}"
            }
        
        # Si la validación es exitosa, calcular tiempos
        timing = self.calculate_execution_times(fecha_reserva, hora_reserva)
        
        overall_valid = validation["is_valid"] and timing["is_valid"]
        
        return {
            "validation": validation,
            "timing": timing,
            "overall_valid": overall_valid,
            "message": "Información de timing completa" if overall_valid else f"Error: {timing['validation_message']}"
        }
