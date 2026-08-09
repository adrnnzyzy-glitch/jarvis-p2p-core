import os
from jarvis.core.config import Settings

def test_settings_instantiation_without_optional_vars(monkeypatch):
    """
    Auditoría QA: 
    Verifica que al instanciar los Settings sin las variables no vitales,
    el sistema NO colapsa (no lanza ValidationError ni AttributeError)
    y asume los valores por defecto (None).
    """
    # Asegurarse de que el entorno esté limpio de estas variables
    monkeypatch.delenv("BINANCE_RSA_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("BINANCE_MERCHANT_ID", raising=False)
    monkeypatch.delenv("REDIS_HOST", raising=False)

    # El sistema no debería colapsar al instanciar
    config = Settings()

    # Verificación estricta de que son None
    assert config.binance_rsa_private_key is None, "El private key debería ser None"
    assert config.binance_merchant_id is None, "El merchant id debería ser None"
    assert config.redis_host is None, "El redis host debería ser None"
