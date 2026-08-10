import asyncio
import aiohttp
from decimal import Decimal

class BinanceP2PClient:
    """
    Cliente asíncrono para la interacción con la API P2P de Binance.
    """
    def __init__(self, merchant_id: str | None = None):
        self.merchant_id = merchant_id
        self.api_url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    async def _fetch_page(self, trade_type: str, fiat: str, asset: str, trans_amount: str | None = None) -> list:
        payload = {
            "page": 1,
            "rows": 10,
            "asset": asset,
            "tradeType": trade_type,
            "fiat": fiat,
            "publisherType": "merchant",
            "payTypes": ["Banesco"]
        }
        if trans_amount:
            payload["transAmount"] = trans_amount
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    print(f"Error Binance API: {response.status}")
                    return []

    async def get_top_ad(self, trade_type: str, fiat: str = "VES", asset: str = "USDT", trans_amount: str | None = None) -> dict:
        """
        Obtiene los datos del mejor anuncio (Top 1) para un tipo de operación y filtro de monto.
        """
        data = await self._fetch_page(trade_type, fiat, asset, trans_amount)
        if data:
            price = Decimal(data[0].get("adv", {}).get("price", "0"))
            nickName = data[0].get("advertiser", {}).get("nickName", "Desconocido")
            return {"price": price, "nickName": nickName}
        return {"price": Decimal("0"), "nickName": "N/A"}

    async def get_orderbook(self, fiat: str = "VES", asset: str = "USDT") -> dict:
        """
        Consulta el Orderbook de Binance P2P.
        Asegura que los montos y precios (strings de la API JSON)
        se transformen y manipulen internamente como Decimal.
        """
        # Para orderbook:
        # sell_orders (asks) son tradeType = "BUY" (anuncios de vendedores, nosotros compramos)
        # buy_orders (bids) son tradeType = "SELL" (anuncios de compradores, nosotros vendemos)
        
        sell_data, buy_data = await asyncio.gather(
            self._fetch_page("BUY", fiat, asset),
            self._fetch_page("SELL", fiat, asset)
        )
        
        sell_orders = []
        for ad in sell_data:
            adv = ad.get("adv", {})
            sell_orders.append({
                "price": Decimal(adv.get("price", "0")),
                "available_asset": Decimal(adv.get("tradableQuantity", "0"))
            })
            
        buy_orders = []
        for ad in buy_data:
            adv = ad.get("adv", {})
            buy_orders.append({
                "price": Decimal(adv.get("price", "0")),
                "available_asset": Decimal(adv.get("tradableQuantity", "0"))
            })
            
        return {
            "buy_orders": buy_orders,
            "sell_orders": sell_orders
        }
