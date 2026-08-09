from typing import Optional
from decimal import Decimal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración global de la aplicación JARVIS.
    Las variables no vitales son estrictamente opcionales para evitar 
    bloqueos críticos durante el arranque del sistema.
    """
    # Variables críticas (ejemplo)
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/jarvis_db"
    admin_telegram_ids: list[int] = [8702518274] # ID de admin por defecto
    min_net_margin_pct: Decimal = Decimal("0.006") # Regla de protección de capital
    capital_usdt: Decimal = Decimal("2000.00") # Capital de trabajo
    
    # Variables NO vitales (Obligatoriamente opcionales)
    binance_rsa_private_key: Optional[str] = None
    binance_merchant_id: Optional[str] = None
    redis_host: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
