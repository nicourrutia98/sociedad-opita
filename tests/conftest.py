# -*- coding: utf-8 -*-
"""
tests/conftest.py — Fixtures compartidos para pytest
====================================================

Mock del DeepSeek API + fixtures de ciudades y personas.

Uso:
    pytest tests/ -v
    pytest tests/test_city_factory.py -v
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Agregar root al path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ------------------------------------------------------------------
# Mock del LLM (sin red, sin costo)
# ------------------------------------------------------------------

class MockDeepSeekResponse:
    """Respuesta simulada de DeepSeek para tests deterministas."""

    def __init__(self, text: str, reasoning: str = ""):
        self.text = text
        self.reasoning = reasoning
        self.input_tokens = 100
        self.output_tokens = len(text.split())
        self.model_key = "deepseek-chat"
        self.cost_usd = 0.0001


def mock_llm_call(prompt: str, **kwargs) -> "MockDeepSeekResponse":
    """Mock que retorna un texto fijo según la persona mencionada en el prompt."""
    if "Don Rosalío" in prompt or "don_rosalio" in prompt:
        text = "asina es la cosa, mijo. La alambrada no se toca."
    elif "Doña Rosa" in prompt or "dona_rosa" in prompt:
        text = "pues mirá ve, le cuento lo que pasó..."
    elif "Padre Cecilio" in prompt or "padre_cecilio" in prompt:
        text = "Dios es el que sabe, mijo. Recemos por ello."
    elif "Jhon Eliécer" in prompt or "jhon_eliecer" in prompt:
        text = "la tierra es un cacho y usté el bozal..."
    else:
        text = "[mock response] Respuesta genérica para tests."
    return MockDeepSeekResponse(text=text)


# ------------------------------------------------------------------
# Fixtures pytest
# ------------------------------------------------------------------

def pytest_configure(config):
    """Setup global: registrar mocks."""
    # Importante: NO importar motor real (rompería tests con red real)
    pass
