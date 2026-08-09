import pytest
from decimal import Decimal
from jarvis.core.arithmetic import ArithmeticEngine

def test_arithmetic_engine_net_profit():
    """
    Auditoría QA: Verificar el cálculo matemático preciso 
    usando exclusivamente Decimal y descontando fees.
    """
    # Escenario: Fee Maker 0.1% (0.001)
    engine = ArithmeticEngine(maker_fee=Decimal("0.001"), taker_fee=Decimal("0.002"))
    
    # Compramos 100 USDT a tasa de 35.0 VES
    # Gastamos: 3500 VES
    # Recibimos (Neto después de comisiones): 100 - (100 * 0.001) = 99.9 USDT
    # Vendemos 99.9 USDT a tasa de 36.0 VES
    # Ingresamos: 99.9 * 36.0 = 3596.4 VES
    # Ganancia Neta: 3596.4 - 3500.0 = 96.4 VES
    
    usdt_vol = "100.0"
    buy_rate = "35.0"
    sell_rate = "36.0"
    
    profit = engine.calculate_net_profit(usdt_vol, buy_rate, sell_rate)
    
    assert isinstance(profit, Decimal), "¡Regla rota! El profit DEBE ser Decimal."
    assert profit == Decimal("96.4"), f"Cálculo erróneo. Esperado: 96.4, Obtenido: {profit}"

def test_validate_usdt_quantity_blocks_invalid():
    """
    Auditoría QA: Verificar que la regla crítica de validación 
    de cantidad de USDT bloquee valores inválidos.
    """
    engine = ArithmeticEngine(maker_fee="0.001", taker_fee="0.002")
    
    with pytest.raises(ValueError, match="estrictamente mayor a cero"):
        engine.validate_usdt_quantity(Decimal("0.0"))
        
    with pytest.raises(ValueError, match="estrictamente mayor a cero"):
        engine.validate_usdt_quantity(Decimal("-5.5"))
