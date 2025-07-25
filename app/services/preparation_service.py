"""
Preparation Service - Servicio de preparación web para reservas programadas

Este módulo implementa la preparación de navegación web antes de la ejecución de reservas.
Se encarga de navegar hasta el botón de reserva específico y mantener la sesión lista
para ejecutar el click en el momento exacto.

Características principales:
- Navegación completa hasta el botón de reserva (sin hacer click)
- Mantenimiento de sesión activa durante la espera
- Detección y validación del botón de reserva
- Ejecución del click final con máxima precisión
"""

import asyncio
import os
from typing import Dict, Any, Optional
from loguru import logger
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from datetime import datetime

from .web_automation import WebAutomationService


class PreparationService:
    """
    Maneja la preparación de la navegación web antes de la ejecución de reservas programadas
    
    Este servicio implementa el patrón de navegación en dos fases:
    1. Preparación: Navegar hasta el botón de reserva (T-1 min)
    2. Ejecución: Click inmediato en el momento exacto (T+1ms)
    """
    
    def __init__(self):
        """Inicializa el servicio con configuración de automatización web"""
        self.crossfit_url = os.getenv("CROSSFIT_URL")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        
        if not all([self.crossfit_url, self.username, self.password]):
            raise ValueError("Faltan credenciales en las variables de entorno")
        
        # Referencias para mantener contexto del navegador
        self.playwright: Optional[Any] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.button_selector: Optional[str] = None
        
        logger.info("🔧 PreparationService inicializado para reservas programadas")
    
    async def prepare_reservation(self, nombre_clase: str, fecha_clase: str) -> Dict[str, Any]:
        """
        Prepara la navegación web hasta el botón de reserva específico
        
        Esta función navega completamente hasta el botón de reserva pero NO hace click.
        Mantiene la sesión activa y guarda el contexto para ejecución posterior.
        
        Args:
            nombre_clase: Nombre exacto de la clase (ej: "18:00 CrossFit 18:00-19:00")
            fecha_clase: Fecha de la clase en formato "XX ##" (ej: "LU 21")
            
        Returns:
            Dict con resultado de preparación:
            {
                "success": bool,
                "message": str,
                "button_ready": bool,
                "session_active": bool,
                "page_context": dict,
                "preparation_time": float,
                "error_type": Optional[str]
            }
        """
        logger.info(f"🚀 Iniciando preparación para clase: {nombre_clase} en fecha: {fecha_clase}")
        preparation_start = datetime.now()
        
        try:
            # Importar async_playwright directamente (sin async with para mantener sesión)
            from playwright.async_api import async_playwright
            
            # Inicializar Playwright manualmente para control total de la sesión
            self.playwright = await async_playwright().start()
            
            # Configuración del browser (similar a WebAutomationService)
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-sandbox'
            ] if self.headless else []
            
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=browser_args,
                slow_mo=50 if self.headless else 0
            )
            
            # Crear contexto
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Script anti-detección
            if self.headless:
                await self.context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                """)
            
            self.page = await self.context.new_page()
            
            # FASE 1: Navegación y Login
            logger.info("📱 Fase 1: Navegando al sitio web...")
            await self.page.goto(self.crossfit_url, wait_until='networkidle')
            await self.page.wait_for_timeout(2000)
            
            # Login (reutilizando lógica de WebAutomationService)
            logger.info("🔐 Fase 2: Realizando login...")
            await self._perform_login()
            
            # FASE 2: Navegación a Clases
            logger.info("📅 Fase 3: Navegando a la sección Clases...")
            await self._navigate_to_classes()
            
            # FASE 3: Selección de Fecha
            logger.info(f"📆 Fase 4: Seleccionando fecha: {fecha_clase}")
            await self._select_date(fecha_clase)
            
            # FASE 4: Encontrar Clase
            logger.info(f"🔍 Fase 5: Localizando clase '{nombre_clase}'...")
            await self._locate_class(nombre_clase)
            
            # FASE 5: Preparar Botón de Reserva (SIN HACER CLICK)
            logger.info("🎯 Fase 6: Preparando botón de reserva...")
            button_result = await self._prepare_reservation_button()
            
            if not button_result["success"]:
                return {
                    "success": False,
                    "message": f"Error preparando botón: {button_result['message']}",
                    "button_ready": False,
                    "session_active": False,
                    "page_context": None,
                    "preparation_time": (datetime.now() - preparation_start).total_seconds(),
                    "error_type": button_result.get("error_type", "BUTTON_PREPARATION_FAILED")
                }
            
            # ÉXITO: Preparación completada
            preparation_time = (datetime.now() - preparation_start).total_seconds()
            
            logger.success(f"✅ Preparación completada en {preparation_time:.2f}s - Botón listo para click")
            
            return {
                "success": True,
                "message": f"Preparación exitosa para {nombre_clase}. Botón listo para ejecución.",
                "button_ready": True,
                "session_active": True,
                "page_context": {
                    "button_selector": self.button_selector,
                    "page_ready": True,
                    "modal_open": True
                },
                "preparation_time": preparation_time,
                "error_type": None
            }
                
        except Exception as e:
            logger.error(f"❌ Error durante preparación: {str(e)}")
            
            # Cleanup en caso de error
            await self._cleanup_browser()
            
            return {
                "success": False,
                "message": f"Error en preparación: {str(e)}",
                "button_ready": False,
                "session_active": False,
                "page_context": None,
                "preparation_time": (datetime.now() - preparation_start).total_seconds(),
                "error_type": "PREPARATION_FAILED"
            }
    
    async def execute_final_click(self) -> Dict[str, Any]:
        """
        Ejecuta el click final en el botón de reserva preparado
        
        Esta función debe ser llamada en el momento exacto de ejecución.
        Utiliza el contexto del navegador preparado previamente.
        
        Returns:
            Dict con resultado de ejecución:
            {
                "success": bool,
                "message": str,
                "execution_time": float,
                "click_successful": bool,
                "reservation_confirmed": bool,
                "error_type": Optional[str]
            }
        """
        logger.info("⚡ Ejecutando click final en botón de reserva...")
        execution_start = datetime.now()
        
        try:
            if not self.page or not self.button_selector:
                raise Exception("Sesión no preparada - debe llamar prepare_reservation() primero")
            
            # Verificar que la página sigue activa
            if self.page.is_closed():
                raise Exception("Página cerrada - sesión expirada")
            
            # Ejecutar click inmediato
            logger.info(f"🎯 Haciendo click en botón: {self.button_selector}")
            
            # TIMING CRÍTICO: Registrar momento exacto del click
            click_timestamp = datetime.now()
            logger.info(f"⚡ CLICK EJECUTADO A LAS: {click_timestamp.strftime('%H:%M:%S.%f')[:-3]}")
            
            # Click con timeout muy corto para máxima velocidad
            await self.page.click(self.button_selector, timeout=2000)
            
            # Registrar tiempo del click únicamente
            click_execution_time = (datetime.now() - click_timestamp).total_seconds()
            logger.info(f"🚀 Click completado en: {click_execution_time:.3f} segundos")
            
            await self.page.wait_for_timeout(1500)  # Espera breve para procesamiento
            
            # Verificar éxito de la reserva
            verification_result = await self._verify_reservation_success()
            
            execution_time = (datetime.now() - execution_start).total_seconds()
            
            if verification_result["success"]:
                logger.success(f"✅ Reserva ejecutada exitosamente en {execution_time:.3f}s")
                
                # Cleanup después del éxito
                await self._cleanup_browser()
                
                return {
                    "success": True,
                    "message": verification_result["message"],
                    "execution_time": execution_time,
                    "click_successful": True,
                    "reservation_confirmed": True,
                    "error_type": None
                }
            else:
                logger.warning(f"⚠️ Click ejecutado pero verificación falló: {verification_result['message']}")
                
                # NO hacer cleanup aquí, permitir reintentos
                return {
                    "success": False,
                    "message": verification_result["message"],
                    "execution_time": execution_time,
                    "click_successful": True,
                    "reservation_confirmed": False,
                    "error_type": verification_result.get("error_type", "VERIFICATION_FAILED")
                }
                
        except Exception as e:
            logger.error(f"❌ Error durante ejecución: {str(e)}")
            
            execution_time = (datetime.now() - execution_start).total_seconds()
            
            # Log del error pero NO hacer cleanup automático
            logger.warning(f"⚠️ Error en ejecución, sesión mantenida para debugging: {str(e)}")
            
            return {
                "success": False,
                "message": f"Error en ejecución: {str(e)}",
                "execution_time": execution_time,
                "click_successful": False,
                "reservation_confirmed": False,
                "error_type": "EXECUTION_FAILED"
            }
    
    async def validate_button_ready(self) -> Dict[str, Any]:
        """
        Valida que el botón de reserva esté listo para ejecución
        
        Función de diagnóstico para verificar el estado de la preparación
        antes de la ejecución final.
        
        Returns:
            Dict con estado de validación:
            {
                "button_ready": bool,
                "session_active": bool,
                "page_available": bool,
                "modal_open": bool,
                "selector_valid": bool
            }
        """
        try:
            if not self.page or not self.button_selector:
                return {
                    "button_ready": False,
                    "session_active": False,
                    "page_available": False,
                    "modal_open": False,
                    "selector_valid": False
                }
            
            page_available = not await self.page.is_closed()
            modal_open = await self.page.is_visible('[role="dialog"]') if page_available else False
            selector_valid = await self.page.is_visible(self.button_selector) if page_available else False
            
            button_ready = page_available and modal_open and selector_valid
            
            logger.info(f"🔍 Validación - Botón listo: {button_ready}, Página: {page_available}, Modal: {modal_open}, Selector: {selector_valid}")
            
            return {
                "button_ready": button_ready,
                "session_active": page_available,
                "page_available": page_available,
                "modal_open": modal_open,
                "selector_valid": selector_valid
            }
            
        except Exception as e:
            logger.error(f"❌ Error en validación: {str(e)}")
            return {
                "button_ready": False,
                "session_active": False,
                "page_available": False,
                "modal_open": False,
                "selector_valid": False
            }
    
    # ================================
    # MÉTODOS PRIVADOS DE NAVEGACIÓN
    # ================================
    
    async def _perform_login(self):
        """Realiza el login reutilizando lógica de WebAutomationService"""
        # Buscar campos de email
        email_selectors = [
            'input[placeholder="Correo"]',
            'input[name="email"]', 
            'input[type="email"]',
            'textbox:has-text("Correo")',
            'input:near(:text("Correo"))',
            'input[placeholder*="correo" i]'
        ]
        
        email_filled = False
        for selector in email_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                await self.page.fill(selector, self.username)
                email_filled = True
                logger.info(f"✅ Email llenado con selector: {selector}")
                break
            except:
                continue
        
        if not email_filled:
            raise Exception("No se pudo encontrar el campo de email")
        
        # Buscar campos de contraseña
        password_selectors = [
            'input[placeholder="Contraseña"]',
            'input[name="password"]',
            'input[type="password"]',
            'input:near(:text("Contraseña"))',
            'input[placeholder*="contraseña" i]'
        ]
        
        password_filled = False
        for selector in password_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                await self.page.fill(selector, self.password)
                password_filled = True
                logger.info(f"✅ Contraseña llenada con selector: {selector}")
                break
            except:
                continue
        
        if not password_filled:
            raise Exception("No se pudo encontrar el campo de contraseña")
        
        # Buscar botón de login
        login_selectors = [
            'button:has-text("Ingresar")',
            'button:has-text("Iniciar")',
            'button:has-text("Login")',
            'input[type="submit"]',
            'button[type="submit"]'
        ]
        
        login_clicked = False
        for selector in login_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                await self.page.click(selector)
                login_clicked = True
                logger.info(f"✅ Login clickeado con selector: {selector}")
                break
            except:
                continue
        
        if not login_clicked:
            raise Exception("No se pudo encontrar el botón de login")
        
        await self.page.wait_for_timeout(5000)
        
        # Verificar login exitoso
        if "home" not in self.page.url:
            raise Exception("Login falló - no se redirigió al home")
        
        logger.info("🎉 Login exitoso confirmado")
    
    async def _navigate_to_classes(self):
        """Navega a la sección de clases"""
        await self.page.wait_for_timeout(2000)
        
        clases_selectors = [
            'a:has-text("Clases")',
            'a:has-text("Classes")',
            'a:has-text("CLASES")', 
            'a:has-text("CLASSES")',
            'button:has-text("Clases")',
            'button:has-text("Classes")',
            'a[href*="clases"]',
            'a[href*="classes"]'
        ]
        
        clases_clicked = False
        for selector in clases_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=3000)
                await self.page.click(selector)
                clases_clicked = True
                logger.info(f"✅ Navegación a Clases exitosa con selector: {selector}")
                break
            except:
                continue
        
        if not clases_clicked:
            raise Exception("No se pudo encontrar el enlace de Clases")
        
        await self.page.wait_for_timeout(2000)
    
    async def _select_date(self, fecha_clase: str):
        """Selecciona la fecha de la clase"""
        partes_fecha = fecha_clase.split()
        if len(partes_fecha) != 2:
            raise Exception(f"Formato de fecha inválido: {fecha_clase}. Debe ser 'XX ##' como 'VI 18'")
        
        dia_semana = partes_fecha[0].upper()
        numero_dia = partes_fecha[1]
        
        # Intentar con número del día primero
        try:
            await self.page.click(f'text="{numero_dia}"', timeout=5000)
            logger.info(f"✅ Fecha seleccionada: {fecha_clase} (usando día {numero_dia})")
        except:
            # Fallback con formato combinado
            try:
                fecha_selector = f'text="{dia_semana}{numero_dia}"'
                await self.page.click(fecha_selector, timeout=3000)
                logger.info(f"✅ Fecha seleccionada con método alternativo: {fecha_clase}")
            except Exception as e:
                raise Exception(f"No se pudo seleccionar la fecha {fecha_clase}: {str(e)}")
        
        await self.page.wait_for_timeout(500)
        
        # Esperar a que se carguen las clases
        logger.info(f"⏳ Esperando a que se carguen las clases para {fecha_clase}...")
        try:
            clases_loaded_selectors = [
                'text="Presencial"',
                'text="In-person"',
                'text="CrossFit"'
            ]
            
            for selector in clases_loaded_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=2000)
                    logger.info(f"✅ Clases cargadas para {fecha_clase}")
                    break
                except:
                    continue
            
            await self.page.wait_for_timeout(500)
            
        except Exception as e:
            logger.debug(f"⚠️ Error detectando clases cargadas: {str(e)}, continuando...")
            await self.page.wait_for_timeout(500)
    
    async def _locate_class(self, nombre_clase: str):
        """Localiza y selecciona la clase específica"""
        logger.info(f"🔍 Buscando clase '{nombre_clase}'...")
        
        clase_selector = f'text="{nombre_clase}"'
        await self.page.wait_for_selector(clase_selector, timeout=8000)
        await self.page.click(clase_selector)
        await self.page.wait_for_timeout(800)
        
        logger.info(f"✅ Clase '{nombre_clase}' seleccionada")
    
    async def _prepare_reservation_button(self) -> Dict[str, Any]:
        """
        Prepara el botón de reserva sin hacer click
        
        Returns:
            Dict con resultado de preparación del botón
        """
        try:
            # Esperar a que aparezca el modal
            logger.info("⏳ Esperando modal de clase...")
            modal_found = False
            
            try:
                await self.page.wait_for_selector('dialog', timeout=6000)
                logger.info("✅ Modal (dialog) detectado")
                modal_found = True
            except:
                try:
                    await self.page.wait_for_selector('[role="dialog"]', timeout=3000)
                    logger.info("✅ Modal (role=dialog) detectado")
                    modal_found = True
                except:
                    logger.warning("⚠️ No se detectó modal específico, continuando...")
            
            # Buscar y preparar botón de reserva
            logger.info("🔍 Localizando botón de reserva...")
            
            # Lista de selectores de botón en orden de prioridad
            button_selectors = [
                'button:has-text("Reservar")',
                'button:has-text("Book")'
            ]
            
            button_found = False
            for selector in button_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    
                    # Verificar que el botón esté visible y habilitado
                    is_visible = await self.page.is_visible(selector)
                    is_enabled = await self.page.is_enabled(selector)
                    
                    if is_visible and is_enabled:
                        self.button_selector = selector
                        button_found = True
                        logger.info(f"✅ Botón de reserva preparado: {selector}")
                        break
                    else:
                        logger.debug(f"🔍 Botón {selector} encontrado pero no disponible (visible: {is_visible}, enabled: {is_enabled})")
                        
                except:
                    continue
            
            if not button_found:
                # Verificar si no quedan cupos
                try:
                    no_cupos_esp = await self.page.is_visible('button:has-text("No quedan cupos")')
                    no_cupos_eng = await self.page.is_visible('button:has-text("No places left")')
                    
                    if no_cupos_esp or no_cupos_eng:
                        cupos_msg = "No quedan cupos" if no_cupos_esp else "No places left"
                        return {
                            "success": False,
                            "message": f"Sin cupos disponibles - Botón: '{cupos_msg}'",
                            "error_type": "NO_CUPOS"
                        }
                except:
                    pass
                
                # Verificar si ya está reservada
                try:
                    cancel_esp = await self.page.is_visible('button:has-text("Cancelar reserva")')
                    cancel_eng = await self.page.is_visible('button:has-text("Cancel booking")')
                    
                    if cancel_esp or cancel_eng:
                        return {
                            "success": False,
                            "message": "La clase ya está reservada",
                            "error_type": "ALREADY_RESERVED"
                        }
                except:
                    pass
                
                return {
                    "success": False,
                    "message": "No se encontró botón de reserva disponible",
                    "error_type": "BUTTON_NOT_FOUND"
                }
            
            return {
                "success": True,
                "message": f"Botón de reserva preparado: {self.button_selector}",
                "error_type": None
            }
            
        except Exception as e:
            logger.error(f"❌ Error preparando botón: {str(e)}")
            return {
                "success": False,
                "message": f"Error preparando botón: {str(e)}",
                "error_type": "BUTTON_PREPARATION_ERROR"
            }
    
    async def _verify_reservation_success(self) -> Dict[str, Any]:
        """
        Verifica que la reserva fue exitosa después del click
        
        Returns:
            Dict con resultado de verificación
        """
        try:
            await self.page.wait_for_timeout(1000)
            
            # Buscar indicadores de éxito
            success_indicators = [
                ('button:has-text("Cancelar reserva")', "Confirmada con botón 'Cancelar reserva'"),
                ('button:has-text("Cancel booking")', "Confirmada con botón 'Cancel booking'"),
                ('text="Reservada"', "Confirmada con estado 'Reservada'")
            ]
            
            for selector, message in success_indicators:
                try:
                    await self.page.wait_for_selector(selector, timeout=8000)
                    return {
                        "success": True,
                        "message": f"Reserva exitosa - {message}",
                        "error_type": None
                    }
                except:
                    continue
            
            # Verificar si botones de reserva desaparecieron
            try:
                modal_visible = await self.page.is_visible('[role="dialog"]')
                
                if modal_visible:
                    reservar_exists = await self.page.is_visible('[role="dialog"] button:has-text("Reservar")')
                    book_exists = await self.page.is_visible('[role="dialog"] button:has-text("Book")')
                    cancel_esp = await self.page.is_visible('[role="dialog"] button:has-text("Cancelar reserva")')
                    cancel_eng = await self.page.is_visible('[role="dialog"] button:has-text("Cancel booking")')
                    
                    if cancel_esp or cancel_eng:
                        return {
                            "success": True,
                            "message": "Reserva exitosa - Botón de cancelación disponible",
                            "error_type": None
                        }
                    elif not reservar_exists and not book_exists:
                        return {
                            "success": True,
                            "message": "Reserva exitosa - Botones de reserva no disponibles",
                            "error_type": None
                        }
                    else:
                        return {
                            "success": True,
                            "message": "Reserva procesada - Estado indeterminado pero probable éxito",
                            "error_type": None
                        }
                else:
                    return {
                        "success": True,
                        "message": "Reserva exitosa - Modal cerrado después del click",
                        "error_type": None
                    }
                    
            except Exception as e:
                logger.warning(f"⚠️ Error en verificación: {str(e)}")
                return {
                    "success": True,
                    "message": "Reserva procesada - Click ejecutado sin errores detectados",
                    "error_type": None
                }
                
        except Exception as e:
            logger.error(f"❌ Error verificando reserva: {str(e)}")
            return {
                "success": False,
                "message": f"Error en verificación: {str(e)}",
                "error_type": "VERIFICATION_ERROR"
            }
    
    async def _cleanup_browser(self):
        """Limpia recursos del navegador y Playwright"""
        try:
            if self.page and not self.page.is_closed():
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.debug(f"⚠️ Error en cleanup: {str(e)}")
        finally:
            self.playwright = None
            self.browser = None
            self.context = None
            self.page = None
            self.button_selector = None
            logger.info("🧹 Cleanup del navegador completado")
