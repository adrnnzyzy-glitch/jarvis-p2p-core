import pytest
from unittest.mock import AsyncMock, MagicMock
from jarvis.bot.middleware import AdminSecurityMiddleware
from jarvis.core.config import settings

@pytest.mark.asyncio
async def test_admin_security_middleware():
    """
    Auditoría QA: Verificar rigurosamente que el middleware de seguridad
    de aiogram permita el paso exclusivamente a los IDs autorizados y
    bloquee contundentemente los IDs no registrados.
    """
    middleware = AdminSecurityMiddleware()
    
    # Handler simulado (lo que se ejecutaría si pasa el middleware)
    mock_handler = AsyncMock(return_value="Autorizado")
    
    # Configurar el entorno de prueba con un ID autorizado
    authorized_id = 123456789
    settings.admin_telegram_ids = [authorized_id]
    
    # Simulación de un mensaje enviado por ADMIN
    auth_event = MagicMock()
    auth_event.from_user.id = authorized_id
    
    # Simulación de un mensaje enviado por INTRUSO
    intruder_event = MagicMock()
    intruder_event.from_user.id = 999999999
    
    # Prueba 1: Acceso de Admin
    result_auth = await middleware(mock_handler, auth_event, {})
    assert result_auth == "Autorizado", "El admin DEBE poder ejecutar los comandos."
    mock_handler.assert_called_once()
    
    # Reset del mock
    mock_handler.reset_mock()
    
    # Prueba 2: Intento de intrusión
    result_unauth = await middleware(mock_handler, intruder_event, {})
    assert result_unauth is None, "El intruso DEBE ser bloqueado silenciosamente (retornar None)."
    mock_handler.assert_not_called()
