# Imagen base ligera
FROM python:3.10-slim

# Regla Arquitectónica Crítica: Aislamiento absoluto en /opt/venv/
# Previene [Errno 13] Permission denied evitando el uso del user space o pip global.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Directorio de trabajo
WORKDIR /app

# Copiar configuración de dependencias
COPY pyproject.toml ./

# Actualizar pip e instalar poetry en el venv global
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

# Instalar dependencias del proyecto usando poetry
# Forzamos que poetry instale directamente en nuestro /opt/venv/
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

# Copiar el código fuente del orquestador
COPY jarvis/ jarvis/

# Ejecutar el orquestador asíncrono
CMD ["python", "-m", "jarvis.main"]
