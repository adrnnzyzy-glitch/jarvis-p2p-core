from decimal import Decimal
from typing import Dict, Any
from jarvis.core.arithmetic import ArithmeticEngine
from jarvis.core.config import settings

class StrategyEngine:
    """
    Calcula el precio competitivo (Top 1) y ejecuta la regla de 
    protección de capital (Circuit Breaker).
    """
    def __init__(self, arithmetic_engine: ArithmeticEngine):
        self.arithmetic_engine = arithmetic_engine
        self.min_margin = settings.min_net_margin_pct
        self.step = Decimal("0.01") # Mejorar por un céntimo

    def calculate_sell_strategy(self, top_sell_price: Decimal, buy_rate_ves: Decimal) -> Dict[str, Any]:
        """
        Calcula la estrategia para VENDER USDT (Anuncio de Venta).
        Para ser Top 1 al vender, debemos ofrecer un precio MÁS BAJO que la competencia.
        """
        # 1. Precio competitivo ideal
        ideal_price = top_sell_price - self.step
        
        # 2. Precio mínimo rentable (Circuit Breaker)
        min_profitable_price = self.arithmetic_engine.calculate_minimum_sell_price(
            buy_rate_ves=buy_rate_ves, 
            min_margin_pct=self.min_margin
        )
        
        circuit_breaker_tripped = False
        suggested_price = ideal_price
        
        # 3. Validar protección de capital
        if ideal_price < min_profitable_price:
            circuit_breaker_tripped = True
            suggested_price = min_profitable_price
            
        return {
            "action": "SELL",
            "competitor_price": top_sell_price,
            "ideal_price": ideal_price,
            "suggested_price": suggested_price,
            "min_profitable_price": min_profitable_price,
            "circuit_breaker_tripped": circuit_breaker_tripped
        }

    def calculate_buy_strategy(self, top_buy_price: Decimal, sell_rate_ves: Decimal) -> Dict[str, Any]:
        """
        Calcula la estrategia para COMPRAR USDT (Anuncio de Compra).
        Para ser Top 1 al comprar, debemos ofrecer un precio MÁS ALTO que la competencia.
        """
        ideal_price = top_buy_price + self.step
        
        max_profitable_price = self.arithmetic_engine.calculate_maximum_buy_price(
            sell_rate_ves=sell_rate_ves,
            min_margin_pct=self.min_margin
        )
        
        circuit_breaker_tripped = False
        suggested_price = ideal_price
        
        if ideal_price > max_profitable_price:
            circuit_breaker_tripped = True
            suggested_price = max_profitable_price
            
        return {
            "action": "BUY",
            "competitor_price": top_buy_price,
            "ideal_price": ideal_price,
            "suggested_price": suggested_price,
            "max_profitable_price": max_profitable_price,
            "circuit_breaker_tripped": circuit_breaker_tripped
        }

    def evaluate_multi_filter_profitability(self, market_data: Dict[str, Dict[str, dict]]) -> Dict[str, Any]:
        """
        Evalúa la rentabilidad para cada filtro de venta (Maker Sell),
        usando el peor precio de compra (Maker Buy más alto) como base de costo.
        """
        maker_sell = market_data.get("maker_sell", {})
        maker_buy = market_data.get("maker_buy", {})
        
        # Opción A: Usar el precio Maker Buy más alto (peor caso) como costo base
        if not maker_buy:
            return {"error": "No hay datos de Maker Buy para calcular costos."}
            
        cost_basis = max(ad["price"] for ad in maker_buy.values())
        
        results = {}
        for filter_amount, ad_data in maker_sell.items():
            top_sell_price = ad_data["price"]
            competitor_name = ad_data["nickName"]
            # Calculate strategy for this specific filter
            strategy_result = self.calculate_sell_strategy(top_sell_price, cost_basis)
            strategy_result["competitor_name"] = competitor_name
            results[filter_amount] = strategy_result
            
        return {
            "cost_basis": cost_basis,
            "filters": results
        }
