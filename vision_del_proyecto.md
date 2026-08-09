# Vision Document: Proyecto JARVIS - Orquestador P2P Avanzado

## Objetivo Estratégico
Desarrollar "JARVIS", un motor autónomo para el ciclo completo de comercio P2P en Binance (Par: USDT/VES). El sistema requiere tolerancia cero a fallos financieros, precisión matemática absoluta y seguridad de grado institucional.

## Principios Críticos de Arquitectura y Prevención de Errores
1.  **Precisión Matemática (Cero Floats):** Queda ESTRICTAMENTE PROHIBIDO el uso de tipos `float`. Todos los cálculos de volumen (USDT), tasas fiat (VES) y comisiones (Fee) deben utilizar variables de precisión decimal estricta (`Decimal` en Python). 
2.  **Configuración Segura (Pydantic Settings):** Los ajustes de entorno deben gestionarse mediante un validador estricto. **Regla de oro:** Para evitar bloqueos críticos (`AttributeError`) en el arranque del servidor, variables no vitales (como `binance_rsa_private_key`, `binance_merchant_id`, `redis_host`) deben definirse obligatoriamente como OPCIONALES (`Optional[str] = None` o `default=None`) en la clase `Settings`.
3.  **Infraestructura de Despliegue (Docker):** El sistema se construirá con un `Dockerfile` optimizado. Para evitar el error de permisos `[Errno 13]`, las dependencias de Python deben instalarse y copiarse explícitamente en un entorno virtual global como `/opt/venv/`, evitando siempre el uso de directorios ocultos de usuario como `/root/.local`.

## Módulos Core del Sistema
1.  **Capa de Datos:** Conexión asíncrona a PostgreSQL.
2.  **Cliente API Binance:** Interfaz para consultar el Orderbook en tiempo real y gestionar órdenes. Debe manejar Rate Limits para evitar baneos.
3.  **Motor Aritmético:** Lógica para calcular rentabilidad neta real descontando comisiones Maker/Taker.
4.  **Panel de Control en Telegram:** Bot asíncrono interactivo. El bot solo debe responder a los usuarios cuyo ID esté en la variable `ADMIN_TELEGRAM_IDS`.