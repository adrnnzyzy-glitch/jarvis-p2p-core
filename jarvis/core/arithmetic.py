from decimal import Decimal, getcontext

# Fijar la precisión matemática
getcontext().prec = 28

class ArithmeticEngine:
    def __init__(self, maker_fee: Decimal | str, taker_fee: Decimal | str):
        """
        Inicializa el motor aritmético asegurando que las comisiones
        se manejen estrictamente como Decimal.
        """
        self.maker_fee = Decimal(str(maker_fee))
        self.taker_fee = Decimal(str(taker_fee))

    def validate_usdt_quantity(self, amount: str | Decimal) -> Decimal:
        """
        Validación crítica de negocio: Asegura que el input es una cantidad de USDT,
        no un precio. Arroja ValueError en cantidades inválidas.
        """
        val = Decimal(str(amount))
        if val <= Decimal("0"):
            raise ValueError("La cantidad transaccional de USDT debe ser estrictamente mayor a cero.")
        
        # Una cantidad transaccional nunca debería ser confundida con un formato inválido
        return val

    def calculate_net_profit(self, usdt_volume: Decimal | str, buy_rate_ves: Decimal | str, sell_rate_ves: Decimal | str) -> Decimal:
        """
        Calcula la ganancia neta real en VES (moneda fiat).
        Flujo P2P asumido:
        1. Comprar USDT como Maker (Publicar anuncio de compra con fiat).
           - Costo Fiat: usdt_volume * buy_rate_ves
           - USDT recibidos netos: usdt_volume - (usdt_volume * maker_fee)
        2. Vender USDT como Maker (Publicar anuncio de venta por fiat).
           - Ingreso Fiat: USDT recibidos netos * sell_rate_ves
        3. Ganancia Neta = Ingreso Fiat - Costo Fiat
        """
        vol = self.validate_usdt_quantity(usdt_volume)
        buy_rate = Decimal(str(buy_rate_ves))
        sell_rate = Decimal(str(sell_rate_ves))
        
        # Costo de adquirir el USDT total
        cost_ves = vol * buy_rate
        
        # Cantidad de USDT resultante después de la comisión de compra (Maker)
        usdt_bought_net = vol * (Decimal("1") - self.maker_fee)
        
        # Ingreso bruto al vender el USDT neto retenido
        revenue_ves = usdt_bought_net * sell_rate
        
        # Profit final
        net_profit_ves = revenue_ves - cost_ves
        return net_profit_ves

    def calculate_margin_pct(self, usdt_volume: Decimal | str, buy_rate_ves: Decimal | str, sell_rate_ves: Decimal | str) -> Decimal:
        """
        Calcula el porcentaje de margen neto (Ganancia Neta / Costo).
        """
        vol = self.validate_usdt_quantity(usdt_volume)
        buy_rate = Decimal(str(buy_rate_ves))
        sell_rate = Decimal(str(sell_rate_ves))
        
        cost_ves = vol * buy_rate
        if cost_ves == Decimal("0"):
            return Decimal("0")
            
        net_profit_ves = self.calculate_net_profit(vol, buy_rate, sell_rate)
        return net_profit_ves / cost_ves

    def calculate_minimum_sell_price(self, buy_rate_ves: Decimal | str, min_margin_pct: Decimal | str) -> Decimal:
        """
        Calcula el precio mínimo de venta para garantizar el min_margin_pct.
        """
        buy_rate = Decimal(str(buy_rate_ves))
        margin = Decimal(str(min_margin_pct))
        
        min_sell_rate = ((margin + Decimal("1")) * buy_rate) / (Decimal("1") - self.maker_fee)
        return min_sell_rate

    def calculate_maximum_buy_price(self, sell_rate_ves: Decimal | str, min_margin_pct: Decimal | str) -> Decimal:
        """
        Calcula el precio máximo de compra para garantizar el min_margin_pct.
        """
        sell_rate = Decimal(str(sell_rate_ves))
        margin = Decimal(str(min_margin_pct))
        
        max_buy_rate = (sell_rate * (Decimal("1") - self.maker_fee)) / (margin + Decimal("1"))
        return max_buy_rate
