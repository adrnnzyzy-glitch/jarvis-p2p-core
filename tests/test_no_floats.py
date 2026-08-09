import os
import ast
from pathlib import Path

def test_no_float_usage_in_source_code():
    """
    Auditoría estricta de QA:
    Analiza el Abstract Syntax Tree (AST) de todos los archivos .py
    en el directorio principal del proyecto para asegurar que no exista
    ningún uso explícito del tipo 'float' en el código fuente.
    """
    project_root = Path(__file__).parent.parent / "jarvis"
    
    if not project_root.exists():
        # Si aún no hay código fuente, pasa la prueba
        return
        
    for py_file in project_root.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))
            
            for node in ast.walk(tree):
                # Validar llamadas a la función float()
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "float":
                        assert False, f"¡REGLA ROTA! Uso de float() detectado en {py_file} en la línea {node.lineno}."
                        
                # Validar anotaciones de tipo float (ej. var: float)
                if isinstance(node, ast.Name) and node.id == "float":
                    assert False, f"¡REGLA ROTA! Tipo float detectado en {py_file} en la línea {node.lineno}."
                    
                # Validar constantes float (ej. 3.14)
                if isinstance(node, ast.Constant) and isinstance(node.value, float):
                    assert False, f"¡REGLA ROTA! Constante float detectada en {py_file} en la línea {node.lineno}."
