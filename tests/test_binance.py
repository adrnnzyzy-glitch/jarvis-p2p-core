import pytest
from decimal import Decimal
from jarvis.api.binance import BinanceP2PClient

@pytest.mark.asyncio
async def test_binance_client_returns_decimal():
    """
    Auditoría QA: Asegurar que el adaptador del cliente API parsea
    los datos correctamente a Decimal y no usa tipos flotantes.
    """
    client = BinanceP2PClient()
    orderbook = await client.get_orderbook()
    
    buy_price = orderbook["buy_orders"][0]["price"]
    buy_asset = orderbook["buy_orders"][0]["available_asset"]
    
    assert isinstance(buy_price, Decimal), "El precio en el Orderbook debe ser Decimal"
    assert isinstance(buy_asset, Decimal), "El activo disponible debe ser Decimal"
