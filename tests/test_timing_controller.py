"""
Tests unitarios para DirectTimingController

Este módulo contiene tests unitarios completos para validar el comportamiento
del DirectTimingController en diversos escenarios:
- Validación de formatos de fecha/hora
- Cálculo de tiempos de preparación y ejecución
- Manejo de casos edge (fechas pasadas, muy futuras, etc.)
- Precisión de zona horaria Chile/Santiago
"""

import unittest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytz

from app.services.direct_timing_controller import DirectTimingController


class TestDirectTimingController(unittest.TestCase):
    """Test cases para DirectTimingController"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.controller = DirectTimingController()
        self.timezone = pytz.timezone("America/Santiago")
    
    def test_initialization(self):
        """Test: Inicialización correcta del controlador"""
        controller = DirectTimingController()
        self.assertEqual(str(controller.timezone), "America/Santiago")
    
    def test_validate_fecha_hora_valid_future(self):
        """Test: Validación exitosa de fecha/hora futura"""
        # Preparar fecha futura (mañana a las 15:00)
        future_time = datetime.now(self.timezone) + timedelta(days=1)
        fecha_str = future_time.strftime("%Y-%m-%d")
        hora_str = "15:00:00"
        
        # Ejecutar validación
        result = self.controller.validate_fecha_hora(fecha_str, hora_str)
        
        # Verificar resultado
        self.assertTrue(result["is_valid"])
        self.assertEqual(len(result["errors"]), 0)
        self.assertIsNotNone(result["parsed_datetime"])
        self.assertIn("válidas", result["message"].lower())
    
    def test_validate_fecha_hora_invalid_format_date(self):
        """Test: Validación falla con formato de fecha inválido"""
        result = self.controller.validate_fecha_hora("2025-13-45", "15:00:00")
        
        self.assertFalse(result["is_valid"])
        self.assertTrue(len(result["errors"]) > 0)
        self.assertIsNone(result["parsed_datetime"])
        self.assertIn("formato de fecha inválido", result["errors"][0].lower())
    
    def test_validate_fecha_hora_invalid_format_time(self):
        """Test: Validación falla con formato de hora inválido"""
        future_date = (datetime.now(self.timezone) + timedelta(days=1)).strftime("%Y-%m-%d")
        result = self.controller.validate_fecha_hora(future_date, "25:70:90")
        
        self.assertFalse(result["is_valid"])
        self.assertTrue(len(result["errors"]) > 0)
        self.assertIsNone(result["parsed_datetime"])
        self.assertIn("formato de hora inválido", result["errors"][0].lower())
    
    def test_validate_fecha_hora_past_datetime(self):
        """Test: Validación falla con fecha/hora pasada"""
        # Usar fecha de ayer
        past_time = datetime.now(self.timezone) - timedelta(days=1)
        fecha_str = past_time.strftime("%Y-%m-%d")
        hora_str = "15:00:00"
        
        result = self.controller.validate_fecha_hora(fecha_str, hora_str)
        
        self.assertFalse(result["is_valid"])
        self.assertTrue(len(result["errors"]) > 0)
        self.assertIn("debe ser futura", result["errors"][0])
    
    def test_validate_fecha_hora_too_far_future(self):
        """Test: Validación falla con fecha muy lejana (>7 días)"""
        # Usar fecha en 10 días
        far_future = datetime.now(self.timezone) + timedelta(days=10)
        fecha_str = far_future.strftime("%Y-%m-%d")
        hora_str = "15:00:00"
        
        result = self.controller.validate_fecha_hora(fecha_str, hora_str)
        
        self.assertFalse(result["is_valid"])
        self.assertTrue(len(result["errors"]) > 0)
        self.assertIn("más de 7 días", result["errors"][0])
    
    def test_calculate_execution_times_valid_future(self):
        """Test: Cálculo correcto de tiempos para fecha futura"""
        # Preparar fecha 2 horas en el futuro
        future_time = datetime.now(self.timezone) + timedelta(hours=2)
        fecha_str = future_time.strftime("%Y-%m-%d")
        hora_str = future_time.strftime("%H:%M:%S")
        
        # Ejecutar cálculo
        result = self.controller.calculate_execution_times(fecha_str, hora_str)
        
        # Verificar resultado
        self.assertTrue(result["is_valid"])
        self.assertIsNotNone(result["preparation_datetime"])
        self.assertIsNotNone(result["execution_datetime"])
        
        # Verificar diferencia de 60 segundos entre preparación y ejecución
        prep_time = result["preparation_datetime"]
        exec_time = result["execution_datetime"]
        target_time = result["target_time"]
        
        # Preparación debe ser 1 minuto antes del objetivo
        self.assertEqual((target_time - prep_time).total_seconds(), 60)
        
        # Ejecución debe ser 1 milisegundo después del objetivo
        self.assertEqual((exec_time - target_time).total_seconds(), 0.001)
        
        # Verificar que los tiempos de espera son positivos
        self.assertGreater(result["wait_until_prep_seconds"], 0)
        self.assertGreater(result["wait_until_exec_seconds"], 0)
    
    def test_calculate_execution_times_past_time(self):
        """Test: Cálculo marca como inválido para tiempo pasado"""
        # Usar tiempo pasado (1 hora atrás)
        past_time = datetime.now(self.timezone) - timedelta(hours=1)
        fecha_str = past_time.strftime("%Y-%m-%d")
        hora_str = past_time.strftime("%H:%M:%S")
        
        # Ejecutar cálculo
        result = self.controller.calculate_execution_times(fecha_str, hora_str)
        
        # Verificar que es inválido
        self.assertFalse(result["is_valid"])
        self.assertIn("ya pasó", result["validation_message"])
    
    def test_calculate_execution_times_very_long_wait(self):
        """Test: Cálculo marca como inválido para espera muy larga (>24h)"""
        # Usar tiempo muy futuro (30 horas)
        far_future = datetime.now(self.timezone) + timedelta(hours=30)
        fecha_str = far_future.strftime("%Y-%m-%d")
        hora_str = far_future.strftime("%H:%M:%S")
        
        # Ejecutar cálculo
        result = self.controller.calculate_execution_times(fecha_str, hora_str)
        
        # Verificar que es inválido
        self.assertFalse(result["is_valid"])
        self.assertIn("muy largo", result["validation_message"])
    
    def test_calculate_execution_times_invalid_format(self):
        """Test: Cálculo maneja formatos inválidos correctamente"""
        # Usar formato inválido
        result = self.controller.calculate_execution_times("fecha-invalida", "hora-invalida")
        
        # Verificar manejo de error
        self.assertFalse(result["is_valid"])
        self.assertIsNone(result["preparation_datetime"])
        self.assertIsNone(result["execution_datetime"])
        self.assertIn("formato de fecha/hora", result["validation_message"])
    
    def test_get_timing_info_integration(self):
        """Test: Función de integración get_timing_info funciona correctamente"""
        # Preparar fecha válida futura
        future_time = datetime.now(self.timezone) + timedelta(hours=3)
        fecha_str = future_time.strftime("%Y-%m-%d")
        hora_str = future_time.strftime("%H:%M:%S")
        
        # Ejecutar función de integración
        result = self.controller.get_timing_info(fecha_str, hora_str)
        
        # Verificar estructura de respuesta
        self.assertIn("validation", result)
        self.assertIn("timing", result)
        self.assertIn("overall_valid", result)
        self.assertIn("message", result)
        
        # Verificar que es válido
        self.assertTrue(result["overall_valid"])
        self.assertTrue(result["validation"]["is_valid"])
        self.assertTrue(result["timing"]["is_valid"])
    
    def test_get_timing_info_invalid_date(self):
        """Test: get_timing_info maneja fechas inválidas correctamente"""
        # Usar fecha inválida
        result = self.controller.get_timing_info("fecha-invalida", "15:00:00")
        
        # Verificar que es inválido
        self.assertFalse(result["overall_valid"])
        self.assertFalse(result["validation"]["is_valid"])
        self.assertIsNone(result["timing"])
        self.assertIn("Validación fallida", result["message"])
    
    def test_timezone_consistency(self):
        """Test: Consistencia de zona horaria en todos los cálculos"""
        # Verificar que todos los datetime usan la misma zona horaria
        future_time = datetime.now(self.timezone) + timedelta(hours=1)
        fecha_str = future_time.strftime("%Y-%m-%d")
        hora_str = future_time.strftime("%H:%M:%S")
        
        result = self.controller.calculate_execution_times(fecha_str, hora_str)
        
        # Verificar que todos los datetime tienen timezone
        self.assertIsNotNone(result["current_time"].tzinfo)
        self.assertIsNotNone(result["target_time"].tzinfo)
        self.assertIsNotNone(result["preparation_datetime"].tzinfo)
        self.assertIsNotNone(result["execution_datetime"].tzinfo)
        
        # Verificar que todos usan zona horaria de Chile (comparar nombre, no objeto)
        expected_tz_name = "America/Santiago"
        self.assertEqual(str(result["current_time"].tzinfo), expected_tz_name)
        self.assertEqual(str(result["target_time"].tzinfo), expected_tz_name)
        self.assertEqual(str(result["preparation_datetime"].tzinfo), expected_tz_name)
        self.assertEqual(str(result["execution_datetime"].tzinfo), expected_tz_name)


class TestDirectTimingControllerAsync(unittest.IsolatedAsyncioTestCase):
    """Test cases asíncronos para DirectTimingController"""
    
    async def asyncSetUp(self):
        """Configuración inicial para tests asíncronos"""
        self.controller = DirectTimingController()
        self.timezone = pytz.timezone("America/Santiago")
    
    async def test_sleep_until_basic_functionality(self):
        """Test: sleep_until funciona correctamente para tiempos cortos"""
        # Preparar tiempo 0.1 segundos en el futuro
        target_time = datetime.now(self.timezone) + timedelta(milliseconds=100)
        
        # Medir tiempo de inicio
        start_time = datetime.now(self.timezone)
        
        # Ejecutar sleep
        result = await self.controller.sleep_until(target_time)
        
        # Medir tiempo de finalización
        end_time = datetime.now(self.timezone)
        
        # Verificar resultado
        self.assertTrue(result["success"])
        self.assertEqual(result["target_time"], target_time)
        
        # Verificar que la duración fue aproximadamente correcta (±50ms tolerance)
        actual_duration = (end_time - start_time).total_seconds()
        expected_duration = 0.1
        self.assertAlmostEqual(actual_duration, expected_duration, delta=0.05)
    
    async def test_sleep_until_past_time(self):
        """Test: sleep_until maneja correctamente tiempos pasados"""
        # Usar tiempo pasado
        past_time = datetime.now(self.timezone) - timedelta(seconds=1)
        
        # Ejecutar sleep
        result = await self.controller.sleep_until(past_time)
        
        # Verificar que no fue exitoso
        self.assertFalse(result["success"])
        self.assertIn("ya pasó", result["message"])
    
    async def test_sleep_until_precision(self):
        """Test: Precisión de sleep_until para tiempos muy cortos"""
        # Preparar tiempo muy corto (50ms en el futuro)
        target_time = datetime.now(self.timezone) + timedelta(milliseconds=50)
        
        # Ejecutar sleep
        result = await self.controller.sleep_until(target_time)
        
        # Verificar que fue exitoso
        self.assertTrue(result["success"])
        
        # Verificar precisión (debe ser ±20ms)
        precision_ms = abs(result["precision_ms"])
        self.assertLess(precision_ms, 20, f"Precisión fuera de rango: {precision_ms}ms")
    
    async def test_sleep_until_concurrent(self):
        """Test: Múltiples sleep_until concurrentes"""
        # Preparar múltiples tiempos futuros
        base_time = datetime.now(self.timezone)
        targets = [
            base_time + timedelta(milliseconds=100),
            base_time + timedelta(milliseconds=150),
            base_time + timedelta(milliseconds=200)
        ]
        
        # Ejecutar sleep concurrentes
        tasks = [self.controller.sleep_until(target) for target in targets]
        results = await asyncio.gather(*tasks)
        
        # Verificar que todos fueron exitosos
        for result in results:
            self.assertTrue(result["success"])
            
        # Verificar que se ejecutaron en el orden correcto
        wake_times = [result["actual_wake_time"] for result in results]
        self.assertEqual(wake_times, sorted(wake_times))


def run_basic_tests():
    """Función auxiliar para ejecutar tests básicos sin asyncio"""
    print("🧪 Ejecutando tests unitarios básicos...")
    
    # Crear suite de tests síncronos
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDirectTimingController)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


async def run_async_tests():
    """Función auxiliar para ejecutar tests asíncronos"""
    print("🧪 Ejecutando tests unitarios asíncronos...")
    
    # Crear suite de tests asíncronos
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDirectTimingControllerAsync)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Ejecutar todos los tests
    print("🚀 Iniciando batería completa de tests para DirectTimingController")
    
    # Tests síncronos
    sync_success = run_basic_tests()
    
    # Tests asíncronos
    async_success = asyncio.run(run_async_tests())
    
    # Resumen
    if sync_success and async_success:
        print("\n✅ Todos los tests pasaron exitosamente!")
    else:
        print("\n❌ Algunos tests fallaron")
        if not sync_success:
            print("  - Tests síncronos fallaron")
        if not async_success:
            print("  - Tests asíncronos fallaron")
