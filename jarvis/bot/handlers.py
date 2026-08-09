from aiogram import Router, types
from aiogram.filters import Command
from decimal import Decimal
from jarvis.core.arithmetic import ArithmeticEngine
from jarvis.bot.middleware import AdminSecurityMiddleware
from jarvis.core.strategy import StrategyEngine

router = Router()
# Conectar rigurosamente el middleware de seguridad para todos los mensajes
router.message.middleware(AdminSecurityMiddleware())

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
        valid_usdt = engine.validate_usdt_quantity(usdt_amount)
        await message.answer(f"Orden de trading aceptada y procesando cantidad exacta: {valid_usdt} USDT")
    except ValueError as e:
        await message.answer(f"Error de validación matemática: {str(e)}")

@router.message(Command("setmargin"))
async def setmargin_cmd(message: types.Message, strategy: StrategyEngine):
    """
    Modifica en caliente el margen mínimo de ganancia del StrategyEngine.
    """
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Error: Debe proveer el nuevo margen en formato decimal. Ejemplo: /setmargin 0.01")
        return
        
    try:
        new_margin = Decimal(args[1])
        if new_margin <= Decimal("0"):
            await message.answer("Error: El margen debe ser mayor a 0.")
            return
            
        # Modificar en caliente
        strategy.min_margin = new_margin
        await message.answer(f"✅ Margen mínimo actualizado con éxito a: <b>{new_margin * 100}%</b> ({new_margin})", parse_mode="HTML")
    except Exception as e:
        await message.answer("Error de formato. Asegúrese de usar un número decimal válido.")
