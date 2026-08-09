import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from jarvis.main import main

@pytest.mark.asyncio
async def test_main_concurrent_startup():
    """
    Verifica que main() inicie el MarketScanner (vía strategy_loop) y 
    el Bot de Telegram (vía start_polling) concurrentemente sin bloquearse.
    """
    # Evitamos que start_polling y strategy_loop bloqueen el test y espiamos sus llamadas
    with patch("jarvis.main.Dispatcher.start_polling", new_callable=AsyncMock) as mock_start_polling, \
         patch("jarvis.main.asyncio.create_task") as mock_create_task, \
         patch("jarvis.main.strategy_loop") as mock_strategy_loop:
        
        # Simulamos que create_task devuelve un mock de tarea
        mock_task = MagicMock()
        mock_task.cancel = MagicMock()
        mock_create_task.return_value = mock_task

        # Ejecutar main
        await main()

        # 1. Verificar que la tarea asíncrona de la estrategia fue creada (concurrencia iniciada)
        mock_create_task.assert_called_once()
        # El argumento de create_task debe ser el resultado de strategy_loop
        assert mock_strategy_loop.called, "strategy_loop debe ser invocado para pasarlo a create_task"
        
        # 2. Verificar que start_polling fue invocado (el bot inicia)
        mock_start_polling.assert_awaited_once()

        # 3. Verificar que la limpieza se llamó exitosamente al finalizar main()
        # ya que start_polling terminará inmediatamente al ser un mock.
        mock_task.cancel.assert_called_once()
