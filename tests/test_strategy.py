import pytest
from decimal import Decimal
from jarvis.core.arithmetic import ArithmeticEngine
from jarvis.core.strategy import StrategyEngine
from jarvis.core.config import settings

@pytest.fixture
def arithmetic_engine():
    # Usamos fees ficticios: Maker 0.1%, Taker 0.2%
    return ArithmeticEngine(maker_fee="0.001", taker_fee="0.002")

@pytest.fixture
def strategy_engine(arithmetic_engine):
    # Sobrescribimos temporalmente para usar el de la prueba
    engine = StrategyEngine(arithmetic_engine)
    engine.min_margin = Decimal("0.008") # 0.8% explícito para pruebas
    engine.step = Decimal("0.01")
    return engine

def test_strategy_sell_healthy_margin(strategy_engine):
    """
    Si el competidor vende a un precio que nos deja un buen margen,
    el Circuit Breaker NO debe activarse y sugerimos competidor - 0.01
    """
    buy_rate = Decimal("35.00")
    # Para 0.8% margen, vendiendo, el break-even + margen es aprox 35.31
    # Cost = 35.00
    # Min Sell = (35.00 * 1.008) / 0.999 = 35.315...
    # Si competidor está a 36.00, estamos sobrados de margen
    competitor_price = Decimal("36.00")
    
    result = strategy_engine.calculate_sell_strategy(competitor_price, buy_rate)
    
    assert result["action"] == "SELL"
    assert result["circuit_breaker_tripped"] is False
    assert result["ideal_price"] == Decimal("35.99")
    assert result["suggested_price"] == Decimal("35.99")

def test_strategy_sell_circuit_breaker(strategy_engine):
    """
    Si el competidor tira el precio por debajo de nuestra rentabilidad,
    el Circuit Breaker DEBE activarse y fijar el precio mínimo rentable.
    """
    buy_rate = Decimal("35.00")
    # Min Sell aprox 35.315...
    # Competidor está a 35.10 (Pérdida/Margen muy bajo)
    competitor_price = Decimal("35.10")
    
    result = strategy_engine.calculate_sell_strategy(competitor_price, buy_rate)
    
    assert result["circuit_breaker_tripped"] is True
    assert result["suggested_price"] > Decimal("35.10") 
    assert result["suggested_price"] == result["min_profitable_price"]
    
def test_strategy_buy_healthy_margin(strategy_engine):
    """
    Comprando USDT. Si competidor compra barato, nosotros compramos un poco
    más caro pero aún con margen.
    """
    sell_rate = Decimal("36.00")
    # Max buy = (36.00 * 0.999) / 1.008 = 35.678...
    competitor_price = Decimal("35.00")
    
    result = strategy_engine.calculate_buy_strategy(competitor_price, sell_rate)
    
    assert result["circuit_breaker_tripped"] is False
    assert result["suggested_price"] == Decimal("35.01")

def test_strategy_buy_circuit_breaker(strategy_engine):
    """
    Comprando USDT. Si el competidor compra MUY caro, nos salimos
    de margen.
    """
    sell_rate = Decimal("36.00")
    # Max buy = 35.678...
    competitor_price = Decimal("35.80")
    
    result = strategy_engine.calculate_buy_strategy(competitor_price, sell_rate)
    
    assert result["circuit_breaker_tripped"] is True
    assert result["suggested_price"] == result["max_profitable_price"]
