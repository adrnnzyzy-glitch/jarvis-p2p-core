from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from jarvis.core.config import settings

class AdminSecurityMiddleware(BaseMiddleware):
    """
    Middleware de seguridad crítica: Intercepta todos los mensajes entrantes
    y bloquea silenciosamente cualquier interacción de un ID de Telegram 
    que no esté explícitamente en ADMIN_TELEGRAM_IDS.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.from_user.id not in settings.admin_telegram_ids:
            # Bloqueo silencioso: No procesamos el handler
            return None
            
        # Usuario autorizado, continuamos la ejecución del comando
        return await handler(event, data)
