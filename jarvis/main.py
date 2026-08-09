import asyncio
import os
from decimal import Decimal
from aiogram import Bot, Dispatcher
from jarvis.bot.handlers import router
from jarvis.api.binance import BinanceP2PClient
from jarvis.core.arithmetic import ArithmeticEngine
from jarvis.core.scanner import MarketScanner
from jarvis.core.strategy import StrategyEngine
from jarvis.bot.notifier import send_strategy_alert
from jarvis.core.config import settings

async def strategy_loop(scanner: MarketScanner, strategy: StrategyEngine):
    """
    Tarea en segundo plano que consulta el Orderbook y evalúa la estrategia
    continuamente sin bloquear el event loop principal.
    """
    print("Iniciando loop de MarketScanner y StrategyEngine...")
    
    while True:
        try:
            # 1. Escanear competencia con múltiples filtros
            market_data = await scanner.get_multi_filter_competitors()
            
            # 2. Evaluar rentabilidad y estrategia multi-filtro
            evaluation = strategy.evaluate_multi_filter_profitability(market_data)
            
            if "error" not in evaluation:
                # 3. Despachar alertas
                filters_results = evaluation.get("filters", {})
                for amount, result in filters_results.items():
                    result["filter_amount"] = amount
                    await send_strategy_alert(result)
                
        except Exception as e:
            print(f"Error en strategy_loop: {e}")
            
        # Esperar 60 segundos antes de la siguiente pasada
        await asyncio.sleep(60)

async def main():
    """
    Orquestador principal de JARVIS.
    Levanta el bot de Telegram y arranca el monitoreo continuo de Binance P2P.
    """
    print("Iniciando Motor Orquestador JARVIS P2P...")
    print("Seguridad: ACTIVADA | Tipo Matemático: STRICT DECIMAL")
    
    # 1. Inicializar componentes del Motor
    binance_client = BinanceP2PClient(merchant_id=settings.binance_merchant_id)
    scanner = MarketScanner(client=binance_client)
    
    arithmetic = ArithmeticEngine(maker_fee="0.001", taker_fee="0.002")
    strategy = StrategyEngine(arithmetic_engine=arithmetic)
    
    # 2. Inicializar Bot de Telegram
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ADVERTENCIA: TELEGRAM_BOT_TOKEN no configurado en el entorno.")
        # Usamos un token ficticio con formato válido para evitar que aiogram falle en init
        token = "123456789:ABCDEF1234567890abcdef1234567890abc"
        
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    
    # 3. Crear tarea en segundo plano (Background Task) para el Scanner
    scanner_task = asyncio.create_task(strategy_loop(scanner, strategy))
    
    # 4. Iniciar el bot (bloquea el thread principal)
    try:
        print("Iniciando polling del bot de Telegram...")
        await dp.start_polling(bot, strategy=strategy)
    finally:
        # Limpieza al detener
        scanner_task.cancel()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Apagando JARVIS...")
