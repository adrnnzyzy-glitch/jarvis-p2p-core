import os
from pathlib import Path

def test_dockerfile_strict_venv():
    """
    Auditoría QA: Valida rigurosamente que el desarrollador haya configurado
    el Dockerfile utilizando el entorno /opt/venv/ dictado en la visión.
    """
    project_root = Path(__file__).parent.parent
    dockerfile_path = project_root / "Dockerfile"
    
    assert dockerfile_path.exists(), "Fallo Crítico: El Dockerfile no existe."
    
    with open(dockerfile_path, "r", encoding="utf-8") as df:
        content = df.read()
        
    assert "/opt/venv" in content, "Fallo de Seguridad: Dependencias no aisladas en /opt/venv/"
    assert 'ENV PATH="/opt/venv/bin:$PATH"' in content, "Fallo Crítico: El PATH global no apunta al /opt/venv/"

def test_main_entrypoint_exists():
    """
    Auditoría QA: Verifica la existencia del punto de arranque.
    """
    project_root = Path(__file__).parent.parent
    main_path = project_root / "jarvis" / "main.py"
    
    assert main_path.exists(), "Fallo Crítico: jarvis/main.py no fue encontrado."
