from decimal import Decimal
import asyncio

class BinanceP2PClient:
    """
    Cliente asíncrono para la interacción con la API P2P de Binance.
    """
    def __init__(self, merchant_id: str | None = None):
        self.merchant_id = merchant_id

    async def get_orderbook(self, fiat: str = "VES", asset: str = "USDT") -> dict:
        """
        Consulta el Orderbook de Binance P2P.
        Asegura que los montos y precios (strings de la API JSON)
        se transformen y manipulen internamente como Decimal.
        """
        # Simulación de latencia de red asíncrona
        await asyncio.sleep(0)
        
        # Simulación de respuesta de Binance, parseada a Decimal en el adaptador
        return {
            "buy_orders": [
                {"price": Decimal("35.10"), "available_asset": Decimal("150.00")}
            ],
            "sell_orders": [
                {"price": Decimal("35.50"), "available_asset": Decimal("200.00")}
            ]
        }
