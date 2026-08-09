# Plan de Acción Arquitectónico: Proyecto JARVIS

Este documento detalla la arquitectura técnica completa y el plan de implementación iterativo para el orquestador P2P "JARVIS" (USDT/VES en Binance).

## REGLAS CRÍTICAS DE NEGOCIO Y ARQUITECTURA
1. **Inputs de Cantidad (USDT):** Toda la lógica matemática, de trading y validación de datos debe estructurarse asumiendo que los *inputs* del sistema representan **cantidades exactas de criptomoneda (USDT)**, y EN NINGÚN CASO precios directos de transacción. Los validadores de datos bloquearán cualquier entrada que represente un precio o tasa directa en lugar de una cantidad transaccional.
2. **Precisión Matemática Absoluta:** Prohibido el uso de tipos `float`. Todos los cálculos de volumen (USDT), equivalencia fiat (VES) y comisiones (Fee) utilizarán el tipo `Decimal` de forma estricta.
3. **Resiliencia en el Arranque:** Variables de entorno no vitales (`binance_rsa_private_key`, `binance_merchant_id`, `redis_host`) se configurarán obligatoriamente como OPCIONALES en Pydantic.
4. **Despliegue Seguro:** La infraestructura Dockerizada usará `/opt/venv/` global para la gestión de dependencias en Python evitando problemas de permisos `[Errno 13]`.

---

## Fases de Implementación

### Fase 1: Entorno, Core de Configuración e Infraestructura
**Pasos Atómicos:**
1. Inicializar estructura del proyecto Python asíncrono (ej. `pyproject.toml`, FastAPI/Motor asíncrono).
2. Diseñar el validador de configuración `Settings` mediante `pydantic-settings`.
3. Implementar validación específica en `Settings` para que `binance_rsa_private_key`, `binance_merchant_id` y `redis_host` sean definidos como `Optional[str] = None`.
4. Desarrollar el sistema de Logging estructurado y asíncrono.
5. Diseñar el `Dockerfile` base asegurando la creación y uso exclusivo del entorno virtual `/opt/venv/` para instalación de dependencias, evadiendo directorios de usuario.

### Fase 2: Capa de Datos (Data Layer)
**Pasos Atómicos:**
1. Definir los modelos de datos base y esquemas para almacenar el histórico de transacciones, métricas del motor y auditoría de eventos.
2. Configurar la conexión asíncrona al motor de base de datos PostgreSQL (ej. utilizando `asyncpg` + `SQLAlchemy` async).
3. Diseñar los repositorios (Repository Pattern) para operaciones de persistencia.
4. Crear la estructura inicial de migraciones de base de datos (ej. mediante `alembic`).

### Fase 3: Conexión y Cliente API Binance
**Pasos Atómicos:**
1. Diseñar la clase cliente asíncrona para interactuar con la API de Binance P2P.
2. Implementar el módulo de consulta y suscripción del Orderbook P2P (USDT/VES) en tiempo real.
3. Desarrollar un gestor avanzado de límites de peticiones (Rate Limits) aplicando técnicas de backoff exponencial para mitigar riesgos de baneo (IP/Account).
4. Escribir adaptadores de datos para convertir de forma segura las respuestas de Binance (JSON/Strings) a entidades del dominio interno manejadas exclusivamente con `Decimal`.

### Fase 4: Motor Aritmético y de Trading
**Pasos Atómicos:**
1. Construir la capa de **Validación de Datos de Entrada (Input Validation)** que asegure la regla crítica: Los inputs operan sobre *cantidades de USDT* y no sobre precios.
2. Implementar los algoritmos de cálculo de rentabilidad neta real (calculando Spread y descontando fees Maker/Taker).
3. Asegurar las operaciones aritméticas para que interactúen correctamente con las cantidades dadas sin pérdidas de precisión (0 floats).
4. Desarrollar la suite de pruebas unitarias y casos límite (Edge cases) matemáticos del motor aritmético.

### Fase 5: Panel de Control en Telegram (Bot)
**Pasos Atómicos:**
1. Inicializar la arquitectura del bot interactivo asíncrono en Telegram (ej. usando `aiogram` o librería asíncrona afín).
2. Desarrollar y aplicar un middleware/decorador de seguridad que intercepte todos los mensajes, permitiendo la ejecución de comandos **sólo** para los IDs registrados en `ADMIN_TELEGRAM_IDS`.
3. Crear comandos de supervisión: estado del bot, latencia, saldo estimado.
4. Implementar comandos de control de trading ajustados para recibir y manipular únicamente "cantidades exactas de USDT" como parámetros de entrada.

### Fase 6: Orquestación Final y Ensamblaje
**Pasos Atómicos:**
1. Implementar el controlador/loop principal (Event Loop) que orquesta el ciclo: *Lectura de Binance -> Procesamiento Motor Aritmético -> Acciones*.
2. Conectar el sistema de alertas del Motor Aritmético hacia el módulo de Telegram para notificaciones asíncronas al administrador.
3. Crear configuración `docker-compose.yml` integrando el contenedor principal (`/opt/venv/` Python app), la base de datos PostgreSQL, y demás servicios perimetrales de forma interconectada y segura.
