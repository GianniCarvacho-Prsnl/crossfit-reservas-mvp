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
    
    async def realizar_reserva(self, clase_nombre: str, fecha: str) -> dict:
        """
        Realiza una reserva automatizada usando Playwright
        
        Args:
            clase_nombre: Nombre de la clase a reservar (ej: "17:00 CrossFit 17:00-18:00")
            fecha: Día a seleccionar en formato "XX ##" (ej: "JU 17", "VI 18")
            
        Returns:
            Dict con el resultado de la operación
        """
        logger.info(f"🚀 Iniciando reserva con Playwright para clase: {clase_nombre} en fecha: {fecha}")
        
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
                
                # Paso 4: Seleccionar el día dinámicamente basado en la fecha
                logger.info(f"📆 Paso 4: Seleccionando fecha: {fecha}")
                
                # Extraer el día de la semana y número del día (ej: "VI 18" -> "vi" y "18")
                partes_fecha = fecha.split()
                if len(partes_fecha) != 2:
                    raise Exception(f"Formato de fecha inválido: {fecha}. Debe ser 'XX ##' como 'VI 18'")
                
                dia_semana = partes_fecha[0].upper()  # "VI" 
                numero_dia = partes_fecha[1]          # "18"
                
                # Método optimizado: usar solo el número del día (método que funciona)
                try:
                    # Usar el número del día que viene del endpoint dinámicamente
                    await page.click(f'text="{numero_dia}"', timeout=5000)
                    logger.info(f"✅ Fecha seleccionada: {fecha} (usando día {numero_dia})")
                except:
                    # Fallback: intentar con el formato combinado
                    logger.info(f"⚠️ Probando selector alternativo para {fecha}")
                    try:
                        fecha_selector = f'text="{dia_semana}{numero_dia}"'
                        await page.click(fecha_selector, timeout=3000)
                        logger.info(f"✅ Fecha seleccionada con método alternativo: {fecha}")
                    except Exception as e:
                        raise Exception(f"No se pudo seleccionar la fecha {fecha}: {str(e)}")
                
                # Reducir espera después de seleccionar fecha
                await page.wait_for_timeout(1500)  # Reducido de 3000 a 1500ms
                
                
                # Verificar que las clases se cargaron para la fecha seleccionada
                logger.info(f"⏳ Esperando a que se carguen las clases para {fecha}...")
                
                # Esperar a que aparezca contenido de clases con timeout optimizado
                try:
                    # Reducir timeout de 10 a 6 segundos
                    await page.wait_for_selector('text="Presencial"', timeout=6000)
                    await page.wait_for_timeout(1000)  # Reducido de 2000 a 1000ms
                    logger.info(f"✅ Clases cargadas para {fecha}")
                except:
                    logger.warning(f"⚠️ No se detectaron clases para {fecha}, continuando...")
                    await page.wait_for_timeout(1500)  # Reducido de 3000 a 1500ms
                
                # Paso 5: Buscar y seleccionar la clase específica
                logger.info(f"🔍 Paso 5: Buscando clase '{clase_nombre}'...")
                clase_selector = f'text="{clase_nombre}"'
                
                # Reducir timeout de 10 a 8 segundos
                await page.wait_for_selector(clase_selector, timeout=8000)
                await page.click(clase_selector)
                await page.wait_for_timeout(1500)  # Reducido de 2000 a 1500ms
                
                # Paso 6: Confirmar la reserva
                logger.info("💫 Paso 6: Ejecutando reserva...")
                
                # Esperar a que aparezca el modal con los detalles de la clase
                logger.info("⏳ Esperando a que aparezca el modal de la clase...")
                modal_found = False
                
                try:
                    # Reducir timeout de 10 a 6 segundos
                    await page.wait_for_selector('dialog', timeout=6000)
                    logger.info("✅ Modal (dialog) detectado")
                    modal_found = True
                except:
                    # Intentar detectar otros tipos de modal
                    try:
                        await page.wait_for_selector('[role="dialog"]', timeout=3000)  # Reducido de 5 a 3 segundos
                        logger.info("✅ Modal (role=dialog) detectado")
                        modal_found = True
                    except:
                        logger.warning("⚠️ No se detectó un modal específico, continuando...")
                
                # Esperar a que aparezca el botón Reservar
                logger.info("🔍 Buscando botón 'Reservar'...")
                reservar_button_found = False
                
                try:
                    await page.wait_for_selector('button:has-text("Reservar")', timeout=10000)  # Mantener 10s aquí
                    logger.info("✅ Botón 'Reservar' encontrado")
                    reservar_button_found = True
                except:
                    # Verificar si la clase ya está reservada
                    logger.warning("⚠️ No se encontró botón 'Reservar', verificando si ya está reservada...")
                    try:
                        await page.wait_for_selector('button:has-text("Cancelar reserva")', timeout=3000)
                        logger.info("📝 La clase ya está reservada (botón 'Cancelar reserva' presente)")
                        return {
                            "success": True,
                            "message": f"La clase {clase_nombre} ya estaba reservada previamente",
                            "steps_completed": 6
                        }
                    except:
                        logger.error("❌ No se pudo encontrar el botón 'Reservar' ni 'Cancelar reserva'")
                        raise Exception("Botón 'Reservar' no encontrado en la página")
                
                # Solo hacer click si encontramos el botón Reservar
                if reservar_button_found:
                    logger.info("🎯 Haciendo click en 'Reservar'...")
                    await page.click('button:has-text("Reservar")')
                    await page.wait_for_timeout(2000)  # Reducido de 3000 a 2000ms
                
                # Verificar que la reserva fue exitosa
                logger.info("🔍 Verificando éxito de la reserva...")
                
                success = False
                message = ""
                
                # Reducir tiempo de procesamiento
                await page.wait_for_timeout(1000)  # Reducido de 2000 a 1000ms
                
                try:
                    # Método 1: Buscar botón "Cancelar reserva" en el modal (indicador más confiable)
                    await page.wait_for_selector('button:has-text("Cancelar reserva")', timeout=8000)
                    logger.success(f"✅ Reserva completada exitosamente para: {clase_nombre}")
                    success = True
                    message = f"Reserva exitosa para {clase_nombre} - Confirmada con botón 'Cancelar reserva'"
                except:
                    logger.info("⏳ No se encontró 'Cancelar reserva', buscando otros indicadores...")
                    try:
                        # Método 2: Buscar texto "Reservada" en el modal o página
                        await page.wait_for_selector('text="Reservada"', timeout=5000)
                        logger.success(f"✅ Reserva completada exitosamente para: {clase_nombre}")
                        success = True
                        message = f"Reserva exitosa para {clase_nombre} - Confirmada con estado 'Reservada'"
                    except:
                        logger.info("⏳ Verificando si el botón 'Reservar' cambió...")
                        try:
                            # Método 3: Verificar que el botón "Reservar" ya no existe
                            await page.wait_for_selector('button:has-text("Reservar")', timeout=3000)
                            # Si llegamos aquí, el botón aún existe, la reserva probablemente falló
                            logger.warning("⚠️ El botón 'Reservar' aún existe")
                            
                            # Verificar si hay algún mensaje de error
                            try:
                                error_message = await page.text_content('text*="error"', timeout=2000)
                                success = False
                                message = f"Error en la reserva: {error_message}"
                            except:
                                # Si no hay mensaje de error, asumir que se procesó
                                logger.info("📝 No se encontró mensaje de error específico")
                                success = True
                                message = f"Reserva procesada para {clase_nombre} - Estado indeterminado pero sin errores detectados"
                        except:
                            # Si el botón "Reservar" ya no existe, es una buena señal
                            logger.success("✅ El botón 'Reservar' ya no está disponible")
                            success = True
                            message = f"Reserva exitosa para {clase_nombre} - Botón 'Reservar' desapareció"
                
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
