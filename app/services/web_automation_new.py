import os
import asyncio
from typing import Dict, Any
from loguru import logger
from playwright.async_api import async_playwright


class WebAutomationService:
    """
    Servicio de automatización web usando Playwright para Python
    Este servicio maneja toda la navegación en el sitio de CrossFit
    """
    
    def __init__(self):
        self.crossfit_url = os.getenv("CROSSFIT_URL")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        
        if not all([self.crossfit_url, self.username, self.password]):
            raise ValueError("Faltan credenciales en las variables de entorno")
    
    async def execute_reservation(self, clase_nombre: str) -> Dict[str, Any]:
        """
        Ejecuta el flujo completo de reserva para una clase específica usando Playwright
        
        Args:
            clase_nombre: Nombre de la clase a reservar (ej: "17:00 CrossFit 17:00-18:00")
            
        Returns:
            Dict con el resultado de la operación
        """
        logger.info(f"🚀 Iniciando reserva con Playwright para clase: {clase_nombre}")
        
        async with async_playwright() as p:
            try:
                # Lanzar browser
                browser = await p.chromium.launch(headless=False)  # headless=False para debug
                context = await browser.new_context()
                page = await context.new_page()
                
                # Paso 1: Navegar al sitio
                logger.info("📱 Paso 1: Navegando al sitio web...")
                await page.goto(self.crossfit_url)
                await page.wait_for_timeout(3000)
                
                # Paso 2: Realizar login
                logger.info("🔐 Paso 2: Realizando login...")
                await page.fill('input[placeholder="Correo"], input[name="email"], textbox:has-text("Correo")', self.username)
                await page.fill('input[placeholder="Contraseña"], input[name="password"], input[type="password"]', self.password)
                await page.click('button:has-text("Ingresar")')
                await page.wait_for_timeout(3000)
                
                # Verificar que el login fue exitoso
                if "home" not in page.url:
                    raise Exception("Login falló - no se redirigió al home")
                
                # Paso 3: Ir a la sección de clases
                logger.info("📅 Paso 3: Navegando a la sección Clases...")
                await page.click('a:has-text("Clases")')
                await page.wait_for_timeout(2000)
                
                # Paso 4: Seleccionar el día de mañana (jueves 17)
                logger.info("📆 Paso 4: Seleccionando día de mañana...")
                await page.click('text="17"')
                await page.wait_for_timeout(3000)
                
                # Verificar que las clases se cargaron
                await page.wait_for_selector('text="Jueves 17 de julio"')
                
                # Paso 5: Buscar y seleccionar la clase específica
                logger.info(f"🔍 Paso 5: Buscando clase '{clase_nombre}'...")
                clase_selector = f'text="{clase_nombre}"'
                
                # Esperar a que aparezca la clase
                await page.wait_for_selector(clase_selector, timeout=10000)
                await page.click(clase_selector)
                await page.wait_for_timeout(2000)
                
                # Paso 6: Confirmar la reserva
                logger.info("💫 Paso 6: Ejecutando reserva...")
                
                # Esperar a que aparezca el modal y el botón Reservar
                await page.wait_for_selector('button:has-text("Reservar")')
                await page.click('button:has-text("Reservar")')
                await page.wait_for_timeout(3000)
                
                # Verificar que la reserva fue exitosa
                # Buscar indicadores de éxito como "Reservada" o "Cancelar reserva"
                try:
                    await page.wait_for_selector('text="Reservada"', timeout=5000)
                    logger.success(f"✅ Reserva completada exitosamente para: {clase_nombre}")
                    success = True
                    message = f"Reserva exitosa para {clase_nombre}"
                except:
                    # Si no encuentra "Reservada", intentar buscar otros indicadores
                    try:
                        await page.wait_for_selector('button:has-text("Cancelar reserva")', timeout=3000)
                        logger.success(f"✅ Reserva completada exitosamente para: {clase_nombre}")
                        success = True
                        message = f"Reserva exitosa para {clase_nombre}"
                    except:
                        logger.error("⚠️ No se pudo verificar el estado de la reserva")
                        success = False
                        message = "Reserva procesada pero no se pudo verificar el estado"
                
                # Cerrar browser
                await browser.close()
                
                return {
                    "success": success,
                    "message": message,
                    "steps_completed": 6
                }
                
            except Exception as e:
                logger.error(f"❌ Error durante la reserva: {str(e)}")
                try:
                    await browser.close()
                except:
                    pass
                
                return {
                    "success": False,
                    "message": f"Error: {str(e)}",
                    "steps_completed": 0
                }
    
    def validate_credentials(self) -> bool:
        """Valida que las credenciales estén configuradas"""
        return all([self.crossfit_url, self.username, self.password])
