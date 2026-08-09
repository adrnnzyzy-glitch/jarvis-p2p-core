import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from jarvis.db.session import get_db

@pytest.mark.asyncio
async def test_get_db_yields_async_session():
    """
    Auditoría QA:
    Verificar que la dependencia de base de datos retorne correctamente 
    un objeto de tipo AsyncSession, asegurando la conectividad asíncrona
    y el uso correcto del generador sin bloquear el Event Loop.
    """
    # Obtenemos el generador
    generator = get_db()
    
    # Avanzamos el generador para obtener la sesión
    session = await generator.__anext__()
    
    # Verificamos que sea una instancia asíncrona de SQLAlchemy
    assert isinstance(session, AsyncSession), "El generador debe retornar un AsyncSession"
    
    # Cerramos el generador para liberar recursos (simula salida del bloque async with)
    try:
        await generator.__anext__()
    except StopAsyncIteration:
        pass
    else:
        assert False, "El generador no debería tener más elementos."
