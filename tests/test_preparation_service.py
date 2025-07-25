"""
Tests para PreparationService - Servicio de preparación web para reservas programadas

Estas pruebas validan:
- Preparación exitosa de navegación web
- Manejo de errores de navegación
- Mantenimiento de sesión durante espera
- Validación del botón de reserva
- Ejecución del click final
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.preparation_service import PreparationService


class TestPreparationService:
    """Tests para el servicio de preparación web"""
    
    @pytest.fixture
    def preparation_service(self):
        """Fixture que crea una instancia del servicio"""
        with patch.dict('os.environ', {
            'CROSSFIT_URL': 'https://test.crossfit.com',
            'USERNAME': 'test@example.com',
            'PASSWORD': 'testpass',
            'BROWSER_HEADLESS': 'true'
        }):
            return PreparationService()
    
    @pytest.mark.asyncio
    async def test_init_preparation_service(self, preparation_service):
        """Test inicialización del servicio"""
        assert preparation_service.crossfit_url == 'https://test.crossfit.com'
        assert preparation_service.username == 'test@example.com'
        assert preparation_service.password == 'testpass'
        assert preparation_service.headless is True
        assert preparation_service.browser is None
        assert preparation_service.context is None
        assert preparation_service.page is None
        assert preparation_service.button_selector is None
    
    @pytest.mark.asyncio
    async def test_init_missing_credentials(self):
        """Test inicialización con credenciales faltantes"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Faltan credenciales"):
                PreparationService()
    
    @pytest.mark.asyncio
    async def test_prepare_reservation_success(self, preparation_service):
        """Test preparación exitosa de reserva"""
        # Mock de Playwright
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        # Configurar mocks
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_page.url = 'https://test.crossfit.com/home'
        mock_page.is_closed.return_value = False
        mock_page.is_visible.return_value = True
        mock_page.is_enabled.return_value = True
        
        with patch('app.services.preparation_service.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            # Mock métodos privados para test aislado
            preparation_service._perform_login = AsyncMock()
            preparation_service._navigate_to_classes = AsyncMock()
            preparation_service._select_date = AsyncMock()
            preparation_service._locate_class = AsyncMock()
            preparation_service._prepare_reservation_button = AsyncMock(return_value={
                "success": True,
                "message": "Botón preparado",
                "error_type": None
            })
            
            # Simular botón preparado
            preparation_service.button_selector = 'button:has-text("Reservar")'
            
            result = await preparation_service.prepare_reservation(
                "18:00 CrossFit 18:00-19:00",
                "LU 21"
            )
            
            # Verificaciones
            assert result["success"] is True
            assert result["button_ready"] is True
            assert result["session_active"] is True
            assert result["page_context"]["button_selector"] == 'button:has-text("Reservar")'
            assert result["error_type"] is None
            assert result["preparation_time"] > 0
            
            # Verificar que se llamaron los métodos de navegación
            preparation_service._perform_login.assert_called_once()
            preparation_service._navigate_to_classes.assert_called_once()
            preparation_service._select_date.assert_called_once_with("LU 21")
            preparation_service._locate_class.assert_called_once_with("18:00 CrossFit 18:00-19:00")
            preparation_service._prepare_reservation_button.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_prepare_reservation_button_not_found(self, preparation_service):
        """Test preparación con botón de reserva no encontrado"""
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_page.url = 'https://test.crossfit.com/home'
        
        with patch('app.services.preparation_service.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            # Mock métodos que fallan en la preparación del botón
            preparation_service._perform_login = AsyncMock()
            preparation_service._navigate_to_classes = AsyncMock()
            preparation_service._select_date = AsyncMock()
            preparation_service._locate_class = AsyncMock()
            preparation_service._prepare_reservation_button = AsyncMock(return_value={
                "success": False,
                "message": "No se encontró botón de reserva",
                "error_type": "BUTTON_NOT_FOUND"
            })
            preparation_service._cleanup_browser = AsyncMock()
            
            result = await preparation_service.prepare_reservation(
                "18:00 CrossFit 18:00-19:00",
                "LU 21"
            )
            
            # Verificaciones
            assert result["success"] is False
            assert result["button_ready"] is False
            assert result["session_active"] is False
            assert result["error_type"] == "BUTTON_NOT_FOUND"
            assert "No se encontró botón de reserva" in result["message"]
    
    @pytest.mark.asyncio
    async def test_prepare_reservation_no_cupos(self, preparation_service):
        """Test preparación cuando no quedan cupos"""
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_page.url = 'https://test.crossfit.com/home'
        
        with patch('app.services.preparation_service.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            preparation_service._perform_login = AsyncMock()
            preparation_service._navigate_to_classes = AsyncMock()
            preparation_service._select_date = AsyncMock()
            preparation_service._locate_class = AsyncMock()
            preparation_service._prepare_reservation_button = AsyncMock(return_value={
                "success": False,
                "message": "Sin cupos disponibles - Botón: 'No quedan cupos'",
                "error_type": "NO_CUPOS"
            })
            preparation_service._cleanup_browser = AsyncMock()
            
            result = await preparation_service.prepare_reservation(
                "18:00 CrossFit 18:00-19:00",
                "LU 21"
            )
            
            assert result["success"] is False
            assert result["error_type"] == "NO_CUPOS"
            assert "Sin cupos disponibles" in result["message"]
    
    @pytest.mark.asyncio
    async def test_prepare_reservation_already_reserved(self, preparation_service):
        """Test preparación cuando la clase ya está reservada"""
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_page.url = 'https://test.crossfit.com/home'
        
        with patch('app.services.preparation_service.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
            
            preparation_service._perform_login = AsyncMock()
            preparation_service._navigate_to_classes = AsyncMock()
            preparation_service._select_date = AsyncMock()
            preparation_service._locate_class = AsyncMock()
            preparation_service._prepare_reservation_button = AsyncMock(return_value={
                "success": False,
                "message": "La clase ya está reservada",
                "error_type": "ALREADY_RESERVED"
            })
            preparation_service._cleanup_browser = AsyncMock()
            
            result = await preparation_service.prepare_reservation(
                "18:00 CrossFit 18:00-19:00",
                "LU 21"
            )
            
            assert result["success"] is False
            assert result["error_type"] == "ALREADY_RESERVED"
            assert "ya está reservada" in result["message"]
    
    @pytest.mark.asyncio
    async def test_execute_final_click_success(self, preparation_service):
        """Test ejecución exitosa del click final"""
        # Simular preparación previa
        mock_page = AsyncMock()
        mock_page.is_closed = AsyncMock(return_value=False)
        mock_page.is_visible = AsyncMock(return_value=True)
        mock_page.is_enabled = AsyncMock(return_value=True)
        mock_page.click = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        
        preparation_service.page = mock_page
        preparation_service.button_selector = 'button:has-text("Reservar")'
        
        # Mock verificación de éxito
        preparation_service._verify_reservation_success = AsyncMock(return_value={
            "success": True,
            "message": "Reserva exitosa - Confirmada con botón 'Cancelar reserva'",
            "error_type": None
        })
        preparation_service._cleanup_browser = AsyncMock()
        
        result = await preparation_service.execute_final_click()
        
        # Verificaciones
        assert result["success"] is True
        assert result["click_successful"] is True
        assert result["reservation_confirmed"] is True
        assert result["error_type"] is None
        assert result["execution_time"] > 0
        
        # Verificar que se hizo click
        mock_page.click.assert_called_once_with('button:has-text("Reservar")', timeout=2000)
        preparation_service._verify_reservation_success.assert_called_once()
        preparation_service._cleanup_browser.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_final_click_not_prepared(self, preparation_service):
        """Test ejecución sin preparación previa"""
        # No configurar página ni selector (estado no preparado)
        preparation_service._cleanup_browser = AsyncMock()
        
        result = await preparation_service.execute_final_click()
        
        assert result["success"] is False
        assert result["click_successful"] is False
        assert result["reservation_confirmed"] is False
        assert result["error_type"] == "EXECUTION_FAILED"
        assert "Sesión no preparada" in result["message"]
    
    @pytest.mark.asyncio
    async def test_execute_final_click_page_closed(self, preparation_service):
        """Test ejecución con página cerrada"""
        mock_page = AsyncMock()
        mock_page.is_closed = AsyncMock(return_value=True)  # Página cerrada
        
        preparation_service.page = mock_page
        preparation_service.button_selector = 'button:has-text("Reservar")'
        preparation_service._cleanup_browser = AsyncMock()
        
        result = await preparation_service.execute_final_click()
        
        assert result["success"] is False
        assert result["error_type"] == "EXECUTION_FAILED"
        assert "Página cerrada" in result["message"]
    
    @pytest.mark.asyncio
    async def test_execute_final_click_verification_failed(self, preparation_service):
        """Test ejecución con falla en verificación"""
        mock_page = AsyncMock()
        mock_page.is_closed = AsyncMock(return_value=False)
        mock_page.click = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        
        preparation_service.page = mock_page
        preparation_service.button_selector = 'button:has-text("Reservar")'
        
        # Mock verificación que falla
        preparation_service._verify_reservation_success = AsyncMock(return_value={
            "success": False,
            "message": "Error en verificación de reserva",
            "error_type": "VERIFICATION_FAILED"
        })
        preparation_service._cleanup_browser = AsyncMock()
        
        result = await preparation_service.execute_final_click()
        
        assert result["success"] is False
        assert result["click_successful"] is True  # Click se ejecutó
        assert result["reservation_confirmed"] is False  # Pero verificación falló
        assert result["error_type"] == "VERIFICATION_FAILED"
    
    @pytest.mark.asyncio
    async def test_validate_button_ready_all_ok(self, preparation_service):
        """Test validación de botón cuando todo está listo"""
        mock_page = AsyncMock()
        mock_page.is_closed = AsyncMock(return_value=False)
        mock_page.is_visible = AsyncMock(side_effect=lambda selector: {
            '[role="dialog"]': True,
            'button:has-text("Reservar")': True
        }.get(selector, False))
        
        preparation_service.page = mock_page
        preparation_service.button_selector = 'button:has-text("Reservar")'
        
        result = await preparation_service.validate_button_ready()
        
        assert result["button_ready"] is True
        assert result["session_active"] is True
        assert result["page_available"] is True
        assert result["modal_open"] is True
        assert result["selector_valid"] is True
    
    @pytest.mark.asyncio
    async def test_validate_button_ready_not_prepared(self, preparation_service):
        """Test validación sin preparación"""
        result = await preparation_service.validate_button_ready()
        
        assert result["button_ready"] is False
        assert result["session_active"] is False
        assert result["page_available"] is False
        assert result["modal_open"] is False
        assert result["selector_valid"] is False
    
    @pytest.mark.asyncio
    async def test_validate_button_ready_page_closed(self, preparation_service):
        """Test validación con página cerrada"""
        mock_page = AsyncMock()
        mock_page.is_closed = AsyncMock(return_value=True)
        
        preparation_service.page = mock_page
        preparation_service.button_selector = 'button:has-text("Reservar")'
        
        result = await preparation_service.validate_button_ready()
        
        assert result["button_ready"] is False
        assert result["session_active"] is False
        assert result["page_available"] is False
    
    @pytest.mark.asyncio
    async def test_validate_button_ready_modal_closed(self, preparation_service):
        """Test validación con modal cerrado"""
        mock_page = AsyncMock()
        mock_page.is_closed = AsyncMock(return_value=False)
        mock_page.is_visible = AsyncMock(side_effect=lambda selector: {
            '[role="dialog"]': False,  # Modal cerrado
            'button:has-text("Reservar")': True
        }.get(selector, False))
        
        preparation_service.page = mock_page
        preparation_service.button_selector = 'button:has-text("Reservar")'
        
        result = await preparation_service.validate_button_ready()
        
        assert result["button_ready"] is False
        assert result["session_active"] is True
        assert result["page_available"] is True
        assert result["modal_open"] is False
        assert result["selector_valid"] is True


class TestPreparationServicePrivateMethods:
    """Tests para métodos privados de navegación"""
    
    @pytest.fixture
    def preparation_service(self):
        """Fixture con servicio y página mock"""
        with patch.dict('os.environ', {
            'CROSSFIT_URL': 'https://test.crossfit.com',
            'USERNAME': 'test@example.com',
            'PASSWORD': 'testpass',
            'BROWSER_HEADLESS': 'true'
        }):
            service = PreparationService()
            service.page = AsyncMock()
            return service
    
    @pytest.mark.asyncio
    async def test_perform_login_success(self, preparation_service):
        """Test login exitoso"""
        mock_page = preparation_service.page
        mock_page.url = 'https://test.crossfit.com/home'
        
        await preparation_service._perform_login()
        
        # Verificar que se intentaron llenar los campos
        assert mock_page.fill.call_count >= 2  # Email y password
        assert mock_page.click.call_count >= 1  # Botón login
    
    @pytest.mark.asyncio
    async def test_perform_login_email_not_found(self, preparation_service):
        """Test login con campo de email no encontrado"""
        mock_page = preparation_service.page
        mock_page.wait_for_selector.side_effect = Exception("Selector not found")
        
        with pytest.raises(Exception, match="No se pudo encontrar el campo de email"):
            await preparation_service._perform_login()
    
    @pytest.mark.asyncio
    async def test_navigate_to_classes_success(self, preparation_service):
        """Test navegación exitosa a clases"""
        await preparation_service._navigate_to_classes()
        
        # Verificar que se intentó hacer click en enlace de clases
        preparation_service.page.click.assert_called()
    
    @pytest.mark.asyncio
    async def test_select_date_success(self, preparation_service):
        """Test selección exitosa de fecha"""
        await preparation_service._select_date("LU 21")
        
        # Verificar que se intentó hacer click en la fecha
        preparation_service.page.click.assert_called()
    
    @pytest.mark.asyncio
    async def test_select_date_invalid_format(self, preparation_service):
        """Test selección de fecha con formato inválido"""
        with pytest.raises(Exception, match="Formato de fecha inválido"):
            await preparation_service._select_date("FECHA_INVALIDA")
    
    @pytest.mark.asyncio
    async def test_locate_class_success(self, preparation_service):
        """Test localización exitosa de clase"""
        await preparation_service._locate_class("18:00 CrossFit 18:00-19:00")
        
        # Verificar que se buscó y clickeó la clase
        preparation_service.page.wait_for_selector.assert_called_with(
            'text="18:00 CrossFit 18:00-19:00"',
            timeout=8000
        )
        preparation_service.page.click.assert_called()
    
    @pytest.mark.asyncio
    async def test_prepare_reservation_button_success(self, preparation_service):
        """Test preparación exitosa del botón"""
        mock_page = preparation_service.page
        mock_page.is_visible.return_value = True
        mock_page.is_enabled.return_value = True
        
        result = await preparation_service._prepare_reservation_button()
        
        assert result["success"] is True
        assert preparation_service.button_selector is not None
    
    @pytest.mark.asyncio
    async def test_verify_reservation_success_confirmed(self, preparation_service):
        """Test verificación exitosa de reserva"""
        mock_page = preparation_service.page
        # Simular que encuentra botón de cancelar reserva
        mock_page.wait_for_selector.side_effect = [
            None,  # Primer selector encuentra cancelar reserva
            Exception("Not found")  # Otros selectores fallan
        ]
        
        result = await preparation_service._verify_reservation_success()
        
        assert result["success"] is True
        assert "Cancelar reserva" in result["message"]
    
    @pytest.mark.asyncio
    async def test_cleanup_browser(self, preparation_service):
        """Test limpieza de recursos"""
        # Configurar mocks de navegador
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        
        mock_page.is_closed = AsyncMock(return_value=False)
        mock_page.close = AsyncMock()
        mock_context.close = AsyncMock()
        mock_browser.close = AsyncMock()
        
        preparation_service.page = mock_page
        preparation_service.context = mock_context
        preparation_service.browser = mock_browser
        preparation_service.button_selector = 'test-selector'
        
        await preparation_service._cleanup_browser()
        
        # Verificar que se cerraron los recursos
        mock_page.close.assert_called_once()
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        
        # Verificar que se limpiaron las referencias
        assert preparation_service.browser is None
        assert preparation_service.context is None
        assert preparation_service.page is None
        assert preparation_service.button_selector is None


# Tests de integración simplificados
class TestPreparationServiceIntegration:
    """Tests de integración para el servicio completo"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_preparation_flow_mock(self):
        """Test del flujo completo de preparación (con mocks)"""
        with patch.dict('os.environ', {
            'CROSSFIT_URL': 'https://test.crossfit.com',
            'USERNAME': 'test@example.com',
            'PASSWORD': 'testpass',
            'BROWSER_HEADLESS': 'true'
        }):
            service = PreparationService()
            
            # Mock completo del flujo
            with patch('app.services.preparation_service.async_playwright') as mock_playwright:
                mock_p = AsyncMock()
                mock_browser = AsyncMock()
                mock_context = AsyncMock()
                mock_page = AsyncMock()
                
                mock_playwright.return_value.__aenter__.return_value = mock_p
                mock_p.chromium.launch.return_value = mock_browser
                mock_browser.new_context.return_value = mock_context
                mock_context.new_page.return_value = mock_page
                mock_page.url = 'https://test.crossfit.com/home'
                mock_page.is_closed.return_value = False
                mock_page.is_visible.return_value = True
                mock_page.is_enabled.return_value = True
                
                # Test preparación
                result = await service.prepare_reservation(
                    "18:00 CrossFit 18:00-19:00",
                    "LU 21"
                )
                
                assert result["success"] is True
                assert result["button_ready"] is True
                
                # Test ejecución
                service.page = mock_page
                service.button_selector = 'button:has-text("Reservar")'
                
                # Configurar página para ejecución exitosa
                mock_page.is_closed = AsyncMock(return_value=False)
                mock_page.click = AsyncMock()
                mock_page.wait_for_timeout = AsyncMock()
                
                service._verify_reservation_success = AsyncMock(return_value={
                    "success": True,
                    "message": "Reserva exitosa",
                    "error_type": None
                })
                service._cleanup_browser = AsyncMock()
                
                execution_result = await service.execute_final_click()
                
                assert execution_result["success"] is True
                assert execution_result["click_successful"] is True
