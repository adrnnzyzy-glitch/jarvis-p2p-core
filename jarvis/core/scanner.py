import asyncio
from decimal import Decimal
from typing import Dict, Any
from jarvis.api.binance import BinanceP2PClient

class MarketScanner:
    """
    Escanea asíncronamente el Orderbook público de Binance P2P 
    buscando los precios de los competidores.
    """
    def __init__(self, client: BinanceP2PClient):
        self.client = client

    async def get_top_competitors(self) -> Dict[str, Decimal]:
        """
        Consulta el orderbook y extrae los mejores precios actuales (Top 1)
        tanto para la compra como para la venta.
        
        Retorna:
            Dict con 'top_buy_price' y 'top_sell_price'
        """
        orderbook = await self.client.get_orderbook()
        
        buy_orders = orderbook.get("buy_orders", [])
        sell_orders = orderbook.get("sell_orders", [])
        
        top_buy_price = Decimal("0")
        if buy_orders:
            # Buscamos el precio más alto dispuesto a pagar por USDT
            top_buy_price = max(order["price"] for order in buy_orders)
            
        top_sell_price = Decimal("0")
        if sell_orders:
            # Buscamos el precio más bajo dispuesto a vender USDT
            top_sell_price = min(order["price"] for order in sell_orders)
            
        return {
            "top_buy_price": top_buy_price,
            "top_sell_price": top_sell_price
        }
