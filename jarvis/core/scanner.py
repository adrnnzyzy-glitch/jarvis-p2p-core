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

    async def get_multi_filter_competitors(self) -> Dict[str, Dict[str, dict]]:
        """
        Escanea asíncronamente y en paralelo los mejores precios del mercado 
        para diferentes filtros de montos en Bolívares.
        
        - Maker Sell (Pestaña Verde / BUY API): 20k, 50k, 100k VES
        - Maker Buy (Pestaña Roja / SELL API): 20k, 30k, 50k VES
        
        Retorna:
            Dict con 'maker_sell' y 'maker_buy', cada uno mapeando el filtro de monto al precio (Decimal).
        """
        sell_filters = ["20000", "50000", "100000"]
        buy_filters = ["20000", "30000", "50000"]
        
        # Tareas para VENDER USDT (Maker Sell = TradeType BUY)
        maker_sell_tasks = [
            self.client.get_top_ad(trade_type="BUY", trans_amount=amount)
            for amount in sell_filters
        ]
        
        # Tareas para COMPRAR USDT (Maker Buy = TradeType SELL)
        maker_buy_tasks = [
            self.client.get_top_ad(trade_type="SELL", trans_amount=amount)
            for amount in buy_filters
        ]
        
        # Ejecutar todas las peticiones en paralelo
        sell_results = await asyncio.gather(*maker_sell_tasks)
        buy_results = await asyncio.gather(*maker_buy_tasks)
        
        maker_sell_prices = {
            amount: ad_data for amount, ad_data in zip(sell_filters, sell_results) if ad_data["price"] > Decimal("0")
        }
        
        maker_buy_prices = {
            amount: ad_data for amount, ad_data in zip(buy_filters, buy_results) if ad_data["price"] > Decimal("0")
        }
        
        return {
            "maker_sell": maker_sell_prices,
            "maker_buy": maker_buy_prices
        }
