from aiogram import Router, types
from aiogram.filters import Command
from decimal import Decimal
from jarvis.core.arithmetic import ArithmeticEngine

router = Router()
# Instanciamos el motor para validación de inputs
engine = ArithmeticEngine(maker_fee="0.001", taker_fee="0.002")

@router.message(Command("status"))
async def status_cmd(message: types.Message):
    """Reporta el estado general del bot de trading."""
    await message.answer("JARVIS Motor Aritmético: ONLINE y operando.")

@router.message(Command("trade"))
async def trade_cmd(message: types.Message):
    """
    Comando estricto de trading: Requiere explícitamente
    una cantidad exacta de USDT como parámetro.
    """
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Error: Debe proveer una cantidad exacta de USDT. Ejemplo: /trade 150.00")
        return
        
    try:
        usdt_amount = args[1]
        # Validación crítica delegada al motor aritmético (asegura Decimal y mayor a 0)
        valid_usdt = engine.validate_usdt_quantity(usdt_amount)
        
        await message.answer(f"Orden de trading aceptada y procesando cantidad exacta: {valid_usdt} USDT")
    except ValueError as e:
        await message.answer(f"Error de validación matemática: {str(e)}")
